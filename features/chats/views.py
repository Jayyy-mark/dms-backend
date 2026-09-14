import os
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Document, ChatMessage
from .pipelines.rag_agent import RagAgentPipeline
from .tools.doc_tool import index_document_file


@api_view(["POST"])
@permission_classes([AllowAny])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def chat(request):
    """
    RAG Agent Chatbot Endpoint
    Accepts JSON or FormData with message/text, document_id, and history.
    """
    message = request.data.get("message") or request.data.get("text") or ""
    document_id = request.data.get("document_id")
    history = request.data.get("history")

    if not message and not document_id:
        return Response({"error": "Message or document is required."}, status=400)

    # If history was not passed, fetch recent 10 messages from DB for authenticated user
    if not history and request.user and request.user.is_authenticated:
        recent_messages = ChatMessage.objects.filter(user=request.user).order_by("-created_at")[:10]
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(recent_messages)
        ]

    try:
        pipeline = RagAgentPipeline()
        result = pipeline.pipe(question=message, document_id=document_id, history=history)

        # Save user & assistant chat messages if user is authenticated
        if request.user and request.user.is_authenticated:
            try:
                ChatMessage.objects.create(user=request.user, role="user", content=message)
                ChatMessage.objects.create(user=request.user, role="assistant", content=result.get("response", ""))
            except Exception as err:
                print(f"Error saving chat message to DB: {err}")

        return Response(result, status=200)
    except Exception as error:
        print(f"Error in chat view: {error}")
        return Response({"error": str(error)}, status=500)


@api_view(["POST"])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def upload_chat_document(request):
    """
    Upload and index document endpoint
    """
    file = request.FILES.get("file")
    if not file:
        return Response({"error": "File required"}, status=400)

    try:
        # Create Document record
        document = Document.objects.create(file=file)
        
        file_path = document.file.path
        file_name = file.name
        file_url = document.file.url

        # Index document into ChromaDB vector store
        chunks_indexed = index_document_file(
            file_path=file_path,
            file_name=file_name,
            file_url=file_url,
            document_id=document.id
        )

        return Response(
            {
                "document_id": document.id,
                "file_name": file_name,
                "file_url": file_url,
                "chunks_indexed": chunks_indexed,
                "message": f"Document '{file_name}' uploaded and indexed successfully!"
            },
            status=201,
        )
    except Exception as error:
        print(f"Error uploading chat document: {error}")
        return Response({"error": str(error)}, status=500)
