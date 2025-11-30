import json
import re
import vertexai
from typing import List, Dict, Any, Optional
from vertexai.preview.generative_models import GenerativeModel, GenerationConfig
from src.services.knowledge_base import KnowledgeBase
from src.config import Config
from src.utils.logger import logger

class LLMReasoningAgent:
    def __init__(self, model_name: str = "gemini-1.5-flash", temperature: float = 0.2, knowledge_base: Optional[KnowledgeBase] = None):
        # Initialize Vertex AI if project ID is set and NOT in demo mode
        project_id = Config.GCP_PROJECT_ID
        location = Config.GCP_LOCATION
        is_demo = Config.DEMO_MODE
        
        if project_id and not is_demo:
            try:
                vertexai.init(project=project_id, location=location)
                self.model = GenerativeModel(model_name)
                logger.info(f"LLM initialized with model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Vertex AI: {e}")
                self.model = None
        else:
            logger.info("LLM running in DEMO MODE or Project ID not set.")
            self.model = None

        self.generation_config = GenerationConfig(
            temperature=temperature,
            response_mime_type="application/json"
        )
        self.knowledge_base = knowledge_base

    def refine_plan(self, raw_plan: List[Dict], insights: Dict, root_causes: List[Dict]) -> List[Dict]:
        """
        Refines the initial action plan using LLM reasoning.
        Returns a list of refined action steps.
        """
        # DEMO MODE: Bypass LLM if enabled
        if Config.DEMO_MODE:
            logger.info("[LLM] Demo Mode enabled. Returning simulated response.")
            return [
                {
                    "action": "Scale Up Database",
                    "target": "Primary DB Cluster",
                    "reasoning": "High CPU utilization (95%) detected. Scaling up will alleviate pressure immediately.",
                    "priority": "High",
                    "risk_assessment": "Low risk. Zero-downtime scaling."
                },
                {
                    "action": "Clear Redis Cache",
                    "target": "Cache Layer",
                    "reasoning": "Stale cache entries might be contributing to latency.",
                    "priority": "Medium",
                    "risk_assessment": "Medium risk. Temporary cache miss spike expected."
                }
            ]

        similar_incidents = []
        if self.knowledge_base:
            # Create a query from insights summary or root causes
            query = f"{insights.get('summary', '')} {root_causes[0].get('description', '') if root_causes else ''}"
            try:
                results = self.knowledge_base.search_similar(query)
                if results and results['documents']:
                    similar_incidents = results['documents'][0]
            except Exception as e:
                logger.error(f"Error searching knowledge base: {e}")

        prompt = f"""
        You are an expert Enterprise AIOps Agent. Your goal is to refine an initial remediation plan based on system insights and identified root causes.

        ### Context
        **Insights:**
        {json.dumps(insights, indent=2)}

        **Root Causes:**
        {json.dumps(root_causes, indent=2)}

        **Similar Past Incidents (RAG):**
        {json.dumps(similar_incidents, indent=2)}

        **Initial Plan:**
        {json.dumps(raw_plan, indent=2)}

        ### Instructions
        1.  **Analyze**: Review the insights, root causes, and similar past incidents.
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
            if not self.model:
                logger.warning("LLM model not initialized. Returning original plan.")
                return raw_plan

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
            logger.error(f"Error parsing LLM response: {e}")
            # Fallback: return original plan with a note
            return raw_plan
        except Exception as e:
            logger.error(f"Error generating refined plan: {e}")
            return raw_plan
