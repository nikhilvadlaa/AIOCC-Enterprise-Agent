# src/agents/root_cause_agent.py
"""
RootCauseAgent
- Correlates insights with datasets
- Produces a ranked list of possible causes
- Uses simple heuristics + memory lookup to create candidate reasons
"""

from typing import Dict, List

class RootCauseAgent:
    def __init__(self, memory_bank):
        self.memory = memory_bank

    def correlate(self, insights: Dict, datasets: Dict) -> List[Dict]:
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

        # If nothing found, return a low-confidence generic reason
        if not reasons:
            reasons.append({'reason': 'unknown', 'confidence': 0.2, 'detail': 'no strong correlations found'})

        return reasons
