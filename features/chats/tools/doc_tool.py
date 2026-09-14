import os
import pypdf
import docx
from pathlib import Path
from typing import List, Dict, Any, Tuple
from django.conf import settings
import chromadb
from chromadb.config import Settings

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        # Minimal fallback character splitter
        class RecursiveCharacterTextSplitter:
            def __init__(self, chunk_size=1000, chunk_overlap=150):
                self.chunk_size = chunk_size
                self.chunk_overlap = chunk_overlap

            def split_text(self, text: str) -> List[str]:
                chunks = []
                start = 0
                while start < len(text):
                    end = start + self.chunk_size
                    chunks.append(text[start:end])
                    start += self.chunk_size - self.chunk_overlap
                return chunks
from features.chats.services.gemini_service import get_gemini_embeddings

CHROMA_DIR = os.path.join(settings.BASE_DIR, "chroma_db")
os.makedirs(CHROMA_DIR, exist_ok=True)

chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
doc_collection = chroma_client.get_or_create_collection(name="document_embeddings")


def extract_text_from_file(file_path: str) -> List[Tuple[int, str]]:
    """Extract page number and text from PDF or DOCX file."""
    ext = os.path.splitext(file_path)[1].lower()
    pages_text = []

    if ext == ".pdf":
        try:
            reader = pypdf.PdfReader(file_path)
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append((idx + 1, text))
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
    elif ext in [".docx", ".doc"]:
        try:
            doc = docx.Document(file_path)
            full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            if full_text.strip():
                pages_text.append((1, full_text))
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")
    else:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
                if text.strip():
                    pages_text.append((1, text))
        except Exception as e:
            print(f"Error reading text file {file_path}: {e}")

    return pages_text


def index_document_file(file_path: str, file_name: str, file_url: str, document_id: Any = None) -> int:
    """Extract, chunk, embed, and store document in ChromaDB."""
    pages_text = extract_text_from_file(file_path)
    if not pages_text:
        return 0

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    embeddings = get_gemini_embeddings()

    ids = []
    documents = []
    metadatas = []
    embeddings_list = []

    chunk_counter = 0
    for page_num, text in pages_text:
        chunks = text_splitter.split_text(text)
        for idx, chunk in enumerate(chunks):
            chunk_id = f"doc_{document_id or 'file'}_{page_num}_{idx}_{chunk_counter}"
            chunk_counter += 1

            embed_val = embeddings.embed_query(chunk)

            ids.append(chunk_id)
            documents.append(chunk)
            embeddings_list.append(embed_val)
            metadatas.append({
                "file_name": file_name,
                "file_url": file_url,
                "document_id": str(document_id or ""),
                "page": page_num,
                "snippet": chunk[:200] + "..." if len(chunk) > 200 else chunk
            })

    if ids:
        doc_collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings_list,
            metadatas=metadatas
        )

    return len(ids)


def search_documents(query: str, top_k: int = 5) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Search ChromaDB for chunks matching query.
    Returns (formatted_context_string, list_of_source_documents)
    """
    if doc_collection.count() == 0:
        return "NO_RELEVANT_CONTEXT_FOUND", []

    try:
        embeddings = get_gemini_embeddings()
        query_embed = embeddings.embed_query(query)

        results = doc_collection.query(
            query_embeddings=[query_embed],
            n_results=min(top_k, doc_collection.count())
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        if not documents:
            return "NO_RELEVANT_CONTEXT_FOUND", []

        context_parts = []
        source_docs = []
        seen_files = set()

        for doc_text, meta in zip(documents, metadatas):
            file_name = meta.get("file_name", "Unknown File")
            file_url = meta.get("file_url", "")
            page = meta.get("page", 1)
            snippet = meta.get("snippet", doc_text[:200])

            context_parts.append(f"--- Document: {file_name} (Page {page}) ---\n{doc_text}")

            source_key = (file_name, file_url)
            if source_key not in seen_files:
                seen_files.add(source_key)
                source_docs.append({
                    "file_name": file_name,
                    "file_url": file_url,
                    "page": page,
                    "snippet": snippet
                })

        formatted_context = "\n\n".join(context_parts)
        return formatted_context, source_docs

    except Exception as e:
        print(f"Error searching ChromaDB: {e}")
        return "NO_RELEVANT_CONTEXT_FOUND", []
