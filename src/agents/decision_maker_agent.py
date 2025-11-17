# src/agents/decision_maker_agent.py
"""
DecisionMakerAgent
- Converts reasons into prioritized action plan with owners and notes
- For demo: actions are templated with confidence and impact estimates
"""

from typing import List, Dict

class DecisionMakerAgent:
    def __init__(self, business_rules: Dict = None):
        # business_rules can map reasons -> default actions/owners
        self.rules = business_rules or {
            'low_campaign_conversion': {'action':'pause_campaign','owner':'marketing_lead','note':'Investigate targeting and creatives','impact':'reduce wasted spend'},
            'support_escalations': {'action':'open_bug','owner':'engineering_lead','note':'Inspect error logs and release','impact':'fix revenue leakage'},
            'product_bug_or_degradation': {'action':'open_bug','owner':'engineering_lead','note':'Investigate recent release','impact':'restore UX'},
            'campaign_performance_issue': {'action':'audit_campaign','owner':'marketing_lead','note':'Check audiences and landing pages','impact':'improve conversions'},
            'recurrent_issue': {'action':'create_postmortem','owner':'ops_lead','note':'Deep dive recurring incidents','impact':'long term stability'},
            'unknown': {'action':'human_investigate','owner':'ops_lead','note':'Manual triage required','impact':'unknown'}
        }

    def make_plan(self, reasons: List[Dict]) -> List[Dict]:
        plan = []
        # Sort reasons by confidence desc
        sorted_reasons = sorted(reasons, key=lambda r: r.get('confidence',0), reverse=True)
        for r in sorted_reasons:
            key = r['reason']
            rule = self.rules.get(key, self.rules['unknown'])
            plan_item = {
                'reason': key,
                'action': rule['action'],
                'owner': rule['owner'],
                'note': rule['note'],
                'impact': rule['impact'],
                'confidence': r.get('confidence', 0.5)
            }
            plan.append(plan_item)
        return plan
