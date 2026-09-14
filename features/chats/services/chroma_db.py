import chromadb
from django.conf import settings

CHROMA_PATH = settings.BASE_DIR / "chroma_db"
client = chromadb.PersistentClient(path=str(CHROMA_PATH))

CHAT_COLLECTION_NAME = "chat_memory_bge-large-en-v1.5_1024"
DOC_COLLECTION_NAME = "documents_bge-large-en-v1.5_1024"

chat_collection = client.get_or_create_collection(name=CHAT_COLLECTION_NAME)
doc_collection = client.get_or_create_collection(name=DOC_COLLECTION_NAME)
