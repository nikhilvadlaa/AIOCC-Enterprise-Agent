import json
import os
from typing import List, Dict

class KnowledgeBase:
    def __init__(self, data_path="data/incident_history.json"):
        self.data_path = data_path
        self.incidents = self._load_data()

    def _load_data(self) -> List[Dict]:
        if not os.path.exists(self.data_path):
            return []
        try:
            with open(self.data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return []

    def search(self, query: str, limit: int = 2) -> List[Dict]:
        """
        Simple keyword-based search.
        Returns incidents where keywords from the query appear in symptoms or tags.
        """
        query_words = set(query.lower().split())
        results = []

        for incident in self.incidents:
            score = 0
            text_to_search = (incident.get('symptoms', '') + " " + " ".join(incident.get('tags', []))).lower()
            
            for word in query_words:
                if word in text_to_search:
                    score += 1
            
            if score > 0:
                results.append((score, incident))

        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        
        return [item[1] for item in results[:limit]]

    def add_incident(self, incident: Dict):
        self.incidents.append(incident)
        # In a real app, we would persist this back to disk or DB
