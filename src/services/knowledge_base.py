import chromadb
from chromadb.utils import embedding_functions
import json
import os
from typing import List, Dict, Any, Optional

from src.config import Config
from src.utils.logger import logger

class KnowledgeBase:
    def __init__(self, path: Optional[str] = None):
        # Use Config path if not provided
        self.path = path or str(Config.CHROMA_DB_DIR)
        
        # Ensure the directory exists
        os.makedirs(self.path, exist_ok=True)
        
        try:
            self.client = chromadb.PersistentClient(path=self.path)
            # Use a lightweight model for embeddings
            self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
            
            self.collection = self.client.get_or_create_collection(
                name="incident_history",
                embedding_function=self.ef
            )
            logger.info(f"KnowledgeBase initialized at {self.path}")
            
            # Seed data if empty (for Demo/Competition purposes)
            if self.collection.count() == 0:
                self._seed_data()
        except Exception as e:
            logger.error(f"Failed to initialize KnowledgeBase: {e}")
            raise

    def _seed_data(self):
        """Seeds the knowledge base with sample incidents for demonstration."""
        logger.info("Seeding Knowledge Base with sample data...")
        sample_incidents = [
            {
                "id": "inc-001",
                "summary": "High Latency in Payment Gateway due to Redis Cache Miss",
                "resolution": [{"action": "Scale Up Redis", "target": "Cache Cluster"}],
                "root_cause": {"reason": "Cache Eviction Policy"}
            },
            {
                "id": "inc-002",
                "summary": "Database Connection Timeout during Peak Load",
                "resolution": [{"action": "Increase Connection Pool Size", "target": "Primary DB"}],
                "root_cause": {"reason": "Connection Pool Exhaustion"}
            },
            {
                "id": "inc-003",
                "summary": "API 500 Errors caused by Memory Leak in Service A",
                "resolution": [{"action": "Restart Service", "target": "Service A"}],
                "root_cause": {"reason": "Memory Leak"}
            }
        ]
        
        for inc in sample_incidents:
            self.add_incident(
                trace_id=inc["id"],
                summary=inc["summary"],
                resolution=inc["resolution"],
                root_cause=inc["root_cause"]
            )

    def add_incident(self, trace_id: str, summary: str, resolution: List[Dict], root_cause: Dict):
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
        logger.info(f"Added incident {trace_id} to Knowledge Base.")

    def search_similar(self, query: str, n_results: int = 3) -> Dict[str, Any]:
        """
        Searches for similar incidents based on the query (e.g., current insights).
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
