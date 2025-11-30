import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from src.config import Config
from src.agents.llm_reasoning_agent import LLMReasoningAgent

def test_refine_plan():
    # Ensure DEMO_MODE is False so we hit the LLM logic (which we will mock)
    Config.DEMO_MODE = False
    Config.GCP_PROJECT_ID = "test-project" # Ensure it tries to init vertexai

    # Mock vertexai.init to avoid actual auth
    with patch("src.agents.llm_reasoning_agent.vertexai.init"), \
         patch("src.agents.llm_reasoning_agent.GenerativeModel") as MockModel:
        
        # Setup mock response
        mock_instance = MockModel.return_value
        mock_response = MagicMock()
        mock_response.text = """
        ```json
        {
            "plan": [
                {
                    "action": "check_logs",
                    "target": "server1",
                    "reasoning": "High latency observed",
                    "priority": "High",
                    "risk_assessment": "Low"
                }
            ]
        }
        ```
        """
        mock_instance.generate_content.return_value = mock_response

        agent = LLMReasoningAgent()
        
        raw_plan = [{"action": "check_logs", "target": "server1"}]
        insights = {"summary": "High latency detected"}
        root_causes = [{"cause": "CPU overload", "probability": 0.9}]
        
        print("Testing refine_plan with MOCK...")
        try:
            refined_plan = agent.refine_plan(raw_plan, insights, root_causes)
            print("Refined Plan Type:", type(refined_plan))
            print("Refined Plan Content:")
            print(json.dumps(refined_plan, indent=2))
            
            if isinstance(refined_plan, list) and len(refined_plan) > 0:
                 print("SUCCESS: Output is structured and parsed correctly.")
            else:
                 print("FAILURE: Output is not structured or empty.")

        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_refine_plan()
