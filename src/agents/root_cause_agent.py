# src/agents/root_cause_agent.py
"""
RootCauseAgent
- Correlates insights with datasets
- Produces a ranked list of possible causes
- Uses simple heuristics + memory lookup to create candidate reasons
"""

from typing import Dict, List, Any, Optional
from src.services.knowledge_base import KnowledgeBase
from src.utils.logger import logger

class RootCauseAgent:
    def __init__(self, memory_bank: Any, knowledge_base: Optional[KnowledgeBase] = None):
        self.memory = memory_bank
        # Use provided KB or create a new one (though DI is preferred)
        self.kb = knowledge_base or KnowledgeBase()
        logger.info("RootCauseAgent initialized.")

    def correlate(self, insights: Dict, datasets: Dict) -> List[Dict]:
        logger.info("Correlating insights to find root causes...")
        reasons = []

        # If sales conversion dropped significantly -> check marketing and support
        if insights.get('sales_conversion_change', 0) < -0.05:
            # marketing correlation: campaign conversion drop
            if insights.get('marketing_drop', False):
                reasons.append({'reason': 'low_campaign_conversion', 'confidence': 0.8, 'detail': f"marketing_pct_change={insights.get('marketing_pct_change')}"})
            # support correlation: escalations could cause reduced conversions
            if insights.get('support_spike', False):
                reasons.append({'reason': 'support_escalations', 'confidence': 0.75, 'detail': f"support_increase_pct={insights.get('support_increase_pct')}"})
            # check memory for previous incidents with same pattern
            past = self.memory.find_by_type('incident') if hasattr(self.memory, 'find_by_type') else []
            if past:
                reasons.append({'reason': 'recurrent_issue', 'confidence': 0.5, 'detail': f"past_count={len(past)}"})

        # If support spike but sales stable -> maybe product bug
        if insights.get('support_spike', False) and insights.get('sales_conversion_change', 0) >= -0.05:
            reasons.append({'reason': 'product_bug_or_degradation', 'confidence': 0.7, 'detail': 'support spike without sales drop'})

        # If marketing drop only
        if insights.get('marketing_drop', False) and insights.get('sales_conversion_change', 0) >= -0.05:
            reasons.append({'reason': 'campaign_performance_issue', 'confidence': 0.75, 'detail': 'marketing conversion decreased'})

        # Check Knowledge Base for similar incidents
        query_terms = []
        if insights.get('support_spike'): query_terms.append("support")
        if insights.get('sales_conversion_change', 0) < -0.05: query_terms.append("latency checkout")
        
        if query_terms:
            query = " ".join(query_terms)
            try:
                similar_incidents = self.kb.search_similar(query)
                # Parse results from ChromaDB format
                if similar_incidents and similar_incidents.get('documents'):
                    # Chroma returns list of lists for documents, metadatas, ids
                    docs = similar_incidents['documents'][0]
                    metas = similar_incidents['metadatas'][0]
                    ids = similar_incidents['ids'][0]
                    
                    for i, doc in enumerate(docs):
                        # Extract root cause from metadata if available
                        meta = metas[i] if i < len(metas) else {}
                        # We might need to parse the JSON string in metadata
                        import json
                        rc_str = meta.get('root_cause', '{}')
                        try:
                            rc_data = json.loads(rc_str)
                            reason_text = rc_data.get('reason', 'similar incident')
                        except:
                            reason_text = 'similar incident'

                        reasons.append({
                            'reason': 'similar_past_incident',
                            'confidence': 0.6,
                            'detail': f"Matches past incident {ids[i]}: {reason_text}"
                        })
            except Exception as e:
                logger.error(f"Error searching knowledge base: {e}")

        # If nothing found, return a low-confidence generic reason
        if not reasons:
            reasons.append({'reason': 'unknown', 'confidence': 0.2, 'detail': 'no strong correlations found'})

        logger.info(f"Identified {len(reasons)} potential root causes.")
        return reasons
