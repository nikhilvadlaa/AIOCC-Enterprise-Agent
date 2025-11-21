import unittest
from src.services.knowledge_base import KnowledgeBase
from src.agents.root_cause_agent import RootCauseAgent
from src.agents.action_executor_agent import ActionExecutorAgent
from src.tools.slack_notifier import SlackNotifier

class TestAdvancedFeatures(unittest.TestCase):
    def test_knowledge_base_search(self):
        kb = KnowledgeBase()
        # Test searching for "latency" which is in the seed data
        results = kb.search("latency")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['id'], 'INC-001')
        print(f"\n[PASS] KnowledgeBase found: {results[0]['root_cause']}")

    def test_root_cause_rag(self):
        # Mock memory bank
        class MockMemory:
            def find_by_type(self, t): return []
        
        agent = RootCauseAgent(MockMemory())
        # Simulate insights that trigger RAG
        insights = {'sales_conversion_change': -0.1, 'support_spike': False}
        reasons = agent.correlate(insights, {})
        
        found_rag = False
        for r in reasons:
            if r['reason'] == 'similar_past_incident':
                found_rag = True
                print(f"\n[PASS] RootCauseAgent found similar incident: {r['detail']}")
        
        self.assertTrue(found_rag, "RootCauseAgent failed to find similar incident")

    def test_action_approval(self):
        # Mock Slack Notifier
        class MockSlack(SlackNotifier):
            def __init__(self):
                self.sent_approval = False
            def send_approval_request(self, channel, message, action_id, trace_id=None):
                self.sent_approval = True
                return {"ok": True, "mock": True}
            def post_message(self, channel, message, trace_id=None):
                return {"ok": True}

        mock_slack = MockSlack()
        agent = ActionExecutorAgent(slack_notifier=mock_slack)
        
        # Test high-risk action
        action_item = {'action': 'restart_server', 'owner': 'devops', 'reason': 'memory leak'}
        result = agent.execute_action(action_item)
        
        self.assertTrue(mock_slack.sent_approval, "ActionExecutorAgent did not request approval for 'restart_server'")
        self.assertEqual(result['status'], 'approval_requested')
        print(f"\n[PASS] ActionExecutorAgent requested approval for: {action_item['action']}")

if __name__ == '__main__':
    unittest.main()
