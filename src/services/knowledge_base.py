import chromadb
from chromadb.utils import embedding_functions
import json
import os

class KnowledgeBase:
    def __init__(self, path="data/chroma_db"):
        # Ensure the directory exists
        os.makedirs(path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=path)
        # Use a lightweight model for embeddings
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        
        self.collection = self.client.get_or_create_collection(
            name="incident_history",
            embedding_function=self.ef
        )

    def add_incident(self, trace_id: str, summary: str, resolution: list, root_cause: dict):
        """
        Adds a resolved incident to the knowledge base.
        """
        # Convert complex objects to strings for metadata
        metadata = {
            "trace_id": trace_id,
            "resolution": json.dumps(resolution),
            "root_cause": json.dumps(root_cause)
        }
        
        self.collection.add(
            documents=[summary],
            metadatas=[metadata],
            ids=[trace_id]
        )

    def search_similar(self, query: str, n_results: int = 3):
        """
        Searches for similar incidents based on the query (e.g., current insights).
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
