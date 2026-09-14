import chromadb

VECTOR_DB_PATH = "./src/resources/vector_db"

#<!--================================================
#   VECTOR DB FOR PERSISTENT MEMORY FROM DOCUMENTS
#=================================================-->
doc_client = chromadb.PersistentClient(path=VECTOR_DB_PATH)

doc_collection = doc_client.get_or_create_collection(name="documents")


#<!--================================================
#   CHAT MEMORY (SESSION)
#=================================================-->
chat_client = chromadb.Client()

chat_collection = chat_client.get_or_create_collection(name="chat")

