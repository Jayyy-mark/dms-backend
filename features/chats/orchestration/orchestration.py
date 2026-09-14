import re

try:
    from semantic_kernel import Kernel
    from semantic_kernel.functions import kernel_function
except ImportError:
    Kernel = None

    def kernel_function(*_args, **_kwargs):
        def decorator(function):
            return function
        return decorator

from features.chats.models import ChatMessage, Document
from features.chats.services.chat_memory import retrieve_memory, save_to_chroma
from features.chats.services.helpers import format_context
from features.chats.services.llm import (
    answer_database_question,
    answer_document_question,
    answer_general_question,
)
from features.chats.services.rag import retrieve_docs, store_document


class ChatKernelTools:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    @kernel_function(name="route_message", description="Route a chat message to database, document, or general handling.")
    def route_message(self, message: str, has_file: bool = False) -> str:
        return self.orchestrator.route(message, has_file=has_file)


class ChatOrchestrator:
    database_keywords = {
        "database", "db", "sql", "table", "record", "records", "count",
        "how many", "list", "staff", "document count", "user", "room",
        "department", "category", "rank", "role", "location",
    }
    document_keywords = {
        "document", "file", "pdf", "docx", "summarize", "summary",
        "analyze", "analyse", "extract", "find in", "according to",
        "uploaded",
    }
    greeting_patterns = (
        r"^\s*(hi|hello|hey|mingalarbar)\s*[!.]*\s*$",
    )

    def __init__(self):
        if Kernel is None:
            raise RuntimeError(
                "semantic-kernel is required for chat orchestration. "
                "Install backend requirements before using the chat module."
            )

        self.kernel = Kernel()
        try:
            self.kernel.add_plugin(ChatKernelTools(self), plugin_name="ChatTools")
        except AttributeError:
            pass

    def route(self, message, has_file=False):
        text = (message or "").lower()
        if has_file:
            return "DOCUMENT"
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in self.greeting_patterns):
            return "GENERAL"
        if any(keyword in text for keyword in self.database_keywords):
            return "DATABASE"
        if any(keyword in text for keyword in self.document_keywords):
            return "DOCUMENT"
        return "GENERAL"

    def handle(self, user, message, file=None, document_id=None):
        if not message and not file and not document_id:
            return {"error": "Message or file required"}, 400

        prompt = message or "Summarize this document."
        route = self.route(prompt, has_file=bool(file) or bool(document_id))
        user_id = str(user.id)
        upload_info = None

        if file:
            document = Document.objects.create(file=file)
            upload_info = store_document(document.file.path, user_id=user_id)

        if message:
            ChatMessage.objects.create(user_id=user.id, role="user", content=message)

        recent = self.get_recent_messages(user.id)
        memory = self.get_memory(route, user_id, prompt)
        context = format_context(memory + recent)

        if route == "DATABASE":
            response, sql_result = answer_database_question(prompt, context=context)
            source = "database"
            extra = {"sql_result": sql_result}
        elif route == "DOCUMENT":
            docs = retrieve_docs(prompt, user_id=user_id)
            response = answer_document_question(prompt, docs, context=context)
            source = "document"
            extra = {"docs_used": docs, "document_status": upload_info}
        else:
            response = self.answer_general(prompt, context=context)
            source = "general"
            extra = {}

        ChatMessage.objects.create(user_id=user.id, role="assistant", content=response)
        self.persist_memory(route, user_id, message, response)
        self.compact_history(user.id)

        return {
            "response": response,
            "source": source,
            "route": route,
            "file_uploaded": bool(file),
            **extra,
        }, 200

    def answer_general(self, message, context=""):
        if any(re.search(pattern, message or "", re.IGNORECASE) for pattern in self.greeting_patterns):
            return "Hello! How can I help you today?"
        return answer_general_question(message, context=context)

    def get_recent_messages(self, user_id, limit=5):
        messages = ChatMessage.objects.filter(user_id=user_id).order_by("-created_at")[:limit]
        return [{"role": message.role, "content": message.content} for message in reversed(messages)]

    def get_memory(self, route, user_id, message):
        if route == "GENERAL":
            return []
        return retrieve_memory(user_id, message)

    def persist_memory(self, route, user_id, message, response):
        if route == "GENERAL":
            return
        save_to_chroma(user_id, "user", message)
        save_to_chroma(user_id, "assistant", response)

    def compact_history(self, user_id):
        queryset = ChatMessage.objects.filter(user_id=user_id)
        if queryset.count() <= 40:
            return

        old_ids = list(queryset.order_by("id").values_list("id", flat=True)[:20])
        ChatMessage.objects.filter(id__in=old_ids).delete()
