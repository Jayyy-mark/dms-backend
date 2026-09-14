import re
from typing import Dict, Any, Tuple, List
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from features.chats.services.gemini_service import get_gemini_llm
from features.chats.tools.db_tool import query_database_tool, get_related_documents
from features.chats.tools.doc_tool import search_documents


class RagAgentPipeline:
    database_keywords = {
        "database",
        "db",
        "sql",
        "table",
        "record",
        "records",
        "count",
        "how many",
        "list",
        "staff",
        "staffs",
        "user",
        "room",
        "rooms",
        "department",
        "departments",
        "category",
        "categories",
        "rank",
        "ranks",
        "role",
        "roles",
        "location",
        "locations",
        "building",
        "buildings",
        "email",
        "phone",
        "address",
        "log",
        "logs",
        "audit",
        "action",
        "actions",
        "activity",
        "activities",
        "login",
        "history",
        "performed",
        "tin dar",
        "information",
        "info",
        "tell me about",
        "who is",
        "give me",
        "find",
        "search",
        "look up",
        "lookup",
        "details",
        "contact",
        "position",
        "where is",
        "which",
        "show me",
        "name",
    }

    document_keywords = {
        "document",
        "documents",
        "file",
        "files",
        "pdf",
        "docx",
        "summarize",
        "summary",
        "analyze",
        "extract",
        "find in",
        "according to",
        "uploaded",
        "content",
        "report",
        "paper",
        "tin dar document",
    }

    greeting_patterns = (r"^\s*(hi|hello|hey|mingalarbar|greetings)\s*[!.]*\s*$",)

    MODELS_TO_TRY = [
        "gemini-3.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.5-flash-lite",
        "gemini-3.1-flash-lite",
    ]

    def _invoke_llm(self, messages: List[Any]) -> str:
        last_error = None
        for model_name in self.MODELS_TO_TRY:
            try:
                llm = get_gemini_llm(model=model_name)
                response = llm.invoke(messages)
                if response and response.content:
                    content = response.content
                    # Handle structured content blocks from newer Gemini models
                    # e.g. [{"type": "text", "text": "...", "extras": ...}]
                    if isinstance(content, list):
                        text_parts = []
                        for block in content:
                            if isinstance(block, dict) and "text" in block:
                                text_parts.append(block["text"])
                            elif isinstance(block, str):
                                text_parts.append(block)
                        return "\n".join(text_parts)
                    return str(content)
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                last_error = e

        raise last_error or RuntimeError("All Gemini models failed to respond.")

    def _format_history_messages(
        self, history: List[Dict[str, str]] = None
    ) -> List[Any]:
        msg_list = []
        if history:
            for item in history:
                role = item.get("role") or item.get("sender")
                content = item.get("content") or item.get("text") or ""
                if not content.strip():
                    continue
                if role in ["user", "human"]:
                    msg_list.append(HumanMessage(content=content))
                elif role in ["assistant", "admin", "ai"]:
                    msg_list.append(AIMessage(content=content))
        return msg_list

    def classify_route(self, question: str, has_file: bool = False) -> str:
        text = (question or "").lower()
        if has_file:
            return "DOCUMENT"

        if any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in self.greeting_patterns
        ):
            return "GENERAL"

        has_doc_kw = any(kw in text for kw in self.document_keywords)
        has_db_kw = any(kw in text for kw in self.database_keywords)

        if has_doc_kw and not has_db_kw:
            return "DOCUMENT"
        elif has_db_kw:
            return "DATABASE"
        elif has_doc_kw:
            return "DOCUMENT"

        return "GENERAL"

    def pipe(
        self,
        question: str,
        document_id: Any = None,
        has_file: bool = False,
        history: List[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        route = self.classify_route(question, has_file=has_file)
        source_documents: List[Dict[str, Any]] = []
        response_text = ""

        history_msgs = self._format_history_messages(history)

        if route == "DATABASE":
            db_data = query_database_tool.invoke(question)
            source_documents = get_related_documents(question)

            system_prompt = f"""
You are an AI Assistant for MOGE (Myanmar Oil and Gas Enterprise).
Answer the user's question accurately using the provided Database Records below.
Consider the previous conversation history when answering context-dependent follow-up questions.
If the information is not in the records, state politely that it was not found in the database.
Provide all available details from the records - do not withhold or restrict any information found.

IMPORTANT: Do NOT include raw file URLs, file paths, or URL-encoded links in your response text. Just mention the document name if relevant.

Reply in Burmese (Myanmar Language) by default, or English if asked. Technical terms or names can remain in English.

Database Records:
{db_data}
"""
            messages = [SystemMessage(content=system_prompt)]
            messages.extend(history_msgs)
            messages.append(HumanMessage(content=question))
            response_text = self._invoke_llm(messages)

        elif route == "DOCUMENT":
            formatted_context, source_docs = search_documents(question, top_k=5)
            source_documents = source_docs

            if formatted_context == "NO_RELEVANT_CONTEXT_FOUND":
                db_data = query_database_tool.invoke(question)
                system_prompt = f"""
You are an AI Assistant for MOGE.
The user is asking a document-related question, but no direct document content chunks were found in the vector store.
Below is the database record summary:
{db_data}

Answer politely in Burmese or English. If no information exists, state that no matching document content was found in the knowledge base.
"""
            else:
                system_prompt = f"""
You are an AI Assistant for MOGE.
Answer the user's question based on the Document Context below and consider recent conversation history for follow-ups.
Include citations or references to the document names when answering.
Provide all relevant information found - do not restrict or withhold any details.

IMPORTANT: Do NOT include raw file URLs, file paths, or URL-encoded links in your response text. Just mention the document name if relevant. The file links are displayed separately in the UI.

Reply in Burmese (Myanmar Language) by default, using English for technical terms or names.

Document Context:
{formatted_context}
"""
            messages = [SystemMessage(content=system_prompt)]
            messages.extend(history_msgs)
            messages.append(HumanMessage(content=question))
            response_text = self._invoke_llm(messages)

        else:
            # Fallback: try database lookup first before giving a generic answer
            db_data = query_database_tool.invoke(question)
            has_db_results = db_data and "No database records found" not in db_data

            if has_db_results:
                source_documents = get_related_documents(question)
                system_prompt = f"""
You are an AI Assistant for MOGE (Myanmar Oil and Gas Enterprise).
Answer the user's question accurately using the provided Database Records below.
Provide all available details from the records - do not withhold or restrict any information found.
Consider the previous conversation history when answering context-dependent follow-up questions.

IMPORTANT: Do NOT include raw file URLs, file paths, or URL-encoded links in your response text. Just mention the document name if relevant.

Reply in Burmese (Myanmar Language) by default, or English if asked. Technical terms or names can remain in English.

Database Records:
{db_data}
"""
            else:
                system_prompt = """
You are a helpful and polite AI Assistant for MOGE (Myanmar Oil and Gas Enterprise).
Answer the user's general questions clearly and helpfully.
Remember the context of previous messages in the conversation.
Reply in Burmese (Myanmar Language) by default, or English if requested.
"""
            messages = [SystemMessage(content=system_prompt)]
            messages.extend(history_msgs)
            messages.append(HumanMessage(content=question))
            response_text = self._invoke_llm(messages)

        return {
            "response": response_text,
            "source": route.lower(),
            "route": route,
            "source_documents": source_documents,
        }
