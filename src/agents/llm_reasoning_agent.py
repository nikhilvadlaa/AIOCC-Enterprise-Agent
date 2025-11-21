import json
import re
from typing import List, Dict, Any, Optional
from vertexai.preview.generative_models import GenerativeModel, GenerationConfig

class LLMReasoningAgent:
    def __init__(self, model_name: str = "gemini-1.5-flash", temperature: float = 0.2):
        self.model = GenerativeModel(model_name)
        self.generation_config = GenerationConfig(
            temperature=temperature,
            response_mime_type="application/json"
        )

    def refine_plan(self, raw_plan: List[Dict], insights: Dict, root_causes: List[Dict]) -> List[Dict]:
        """
        Refines the initial action plan using LLM reasoning.
        Returns a list of refined action steps.
        """
        prompt = f"""
        You are an expert Enterprise AIOps Agent. Your goal is to refine an initial remediation plan based on system insights and identified root causes.

        ### Context
        **Insights:**
        {json.dumps(insights, indent=2)}

        **Root Causes:**
        {json.dumps(root_causes, indent=2)}

        **Initial Plan:**
        {json.dumps(raw_plan, indent=2)}

        ### Instructions
        1.  **Analyze**: Review the insights and root causes to understand the incident context.
        2.  **Prioritize**: Reorder steps to address the most critical root causes first.
        3.  **Enhance**: Add specific details, reasoning, and safety checks to each step.
        4.  **Format**: Return the result as a JSON array of action objects.

        ### Output Schema (JSON Array)
        [
            {{
                "action": "Action Name",
                "target": "Target System/Component",
                "reasoning": "Why this step is necessary",
                "priority": "High/Medium/Low",
                "risk_assessment": "Potential risks of this action"
            }}
        ]
        """

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            text_response = response.text.strip()
            # Clean up potential markdown code blocks if the model ignores mime_type
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            elif text_response.startswith("```"):
                text_response = text_response[3:]
            
            if text_response.endswith("```"):
                text_response = text_response[:-3]
            
            text_response = text_response.strip()
            refined_plan = json.loads(text_response)
            
            if isinstance(refined_plan, dict) and "plan" in refined_plan:
                 return refined_plan["plan"]
            
            return refined_plan

        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {e}")
            # Fallback: return original plan with a note
            return raw_plan
        except Exception as e:
            print(f"Error generating refined plan: {e}")
            return raw_plan

