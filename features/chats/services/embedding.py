#<!--==================================
#   Embedding SERVICES
#====================================-->
import fitz
import uuid
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection

from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import BaseNode

from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(
            self, 
            embedding_model : SentenceTransformer, 
            sentence_splitter : SentenceSplitter, 
            doc_client : ClientAPI, 
            doc_collection : Collection, 
            chat_client : ClientAPI, 
            chat_collection : Collection
        ):
        self.sentence_splitter = sentence_splitter
        self.fitz_doc = None
        self.documents = []
        self.doc_client = doc_client
        self.doc_collection = doc_collection
        self.chat_client = chat_client
        self.chat_collection = chat_collection
        self.nodes : list[BaseNode] = []
        self.chunks = []
        self.embeddings = []
        self.embedding_model : SentenceTransformer = embedding_model


    #<!--=================================
    #   OPEN DOCUMENTS USING FITZ
    #===================================-->
    def open_document(self, document_path):
        
        self.fitz_doc = fitz.open(document_path)

    
    #<!--====================================================
    #   PREPARE FITZ OPENED DOCUMENTS AS DOCUMENT FOR NODES
    #=====================================================-->
    def prepare_documents(self):

        for i, page in enumerate(self.fitz_doc):
            
            pageText = page.get_text().strip()

            if not pageText:
                continue

            self.documents.append(
                Document(
                    text = pageText,
                    metadata = { "page" : i + 1 }
                )
            )

        self.fitz_doc.close()
        self.fitz_doc = None

    
    #<!--====================
    #   GENERATE NODES
    #=====================-->    
    def generate_nodes(self):

        self.nodes = self.sentence_splitter.get_nodes_from_documents(self.documents, show_progress=True)

    
    #<!--====================
    #   GENERATE CHUNKS
    #=====================-->  
    def generate_chunks_from_nodes(self):

        self.chunks = [ n.get_content() for n in self.nodes ]

    
    #<!--====================
    #   GENERATE EmbeddingS
    #=====================-->  
    def generate_embeddings(self):
        
        self.embeddings = self.embedding_model.encode(
            self.chunks,
            normalize_embeddings=True,
            batch_size=12,
            show_progress_bar=True,
            convert_to_tensor=False
        )

    #<!--============================
    #   STORE EMBEDDINGS TO VECTOR
    #=============================--> 
    def store_to_vector(self):
        
        for i, (chunk, embedding) in enumerate(zip(self.chunks, self.embeddings)):
            self.doc_collection.add(
                ids=[str(i)],
                embeddings=[embedding.tolist()],
                documents=[chunk],
                metadatas=[{
                    "pages" : self.nodes[i].metadata["page"]
                }]
            )

    #<!--========================================
    #   CONVERT QUERY(STR) TO Embedding (NUMPY)
    #=========================================-->
    def search_embeddings(self, query:str ):
        print("Query : ", self.doc_collection.count())
        query_embedding = self.embedding_model.encode(query, normalize_embeddings=True).tolist()
        print("Query Embedding : ", query_embedding)
        results = self.doc_collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        print("Results : ", results)
        docs = results["documents"][0]
        print("Docs : ", docs)
        if not docs:
            return None
        
        return "\n\n".join(docs)
    
    #<!--===============================
    #   SAVED SESSION MEMORY
    #=================================-->
    def save_chat(self, question, answer):
        
        chat = f"User : {question} \n AI: {answer}"

        chat_embeddings = self.embedding_model.encode(chat, normalize_embeddings=True).tolist()

        self.chat_collection.add(
            ids=[str(uuid.uuid4)],
            embeddings=[chat_embeddings],
            documents=[chat]
        )

    #<!--===============================
    #   GET SESSION MEMORY
    #=================================-->
    def get_memory(self, query):

        if self.chat_collection.count() == 0:
            return None
        
        query_emb = self.embedding_model.encode(query, normalize_embeddings=True).tolist()

        results = self.chat_collection.query(
            query_embeddings=[query_emb],
            n_results=5
        )
        
        return "\n\n".join(results['documents'][0])




    
            

    

    



    





            
