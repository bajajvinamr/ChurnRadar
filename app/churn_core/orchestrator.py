"""
Conversation Orchestrator - Function-Calling LLM
Implements the chat interface with OpenAI function calling
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
import httpx

from .conversation import (
    get_headline_kpis, list_cohorts, get_cohort_passport, 
    show_roi, list_definitions, compare_cohorts, export_copy_pack
)

load_dotenv()


class ConversationOrchestrator:
    """
    Function-calling LLM orchestrator for churn radar conversations.
    Routes user queries to appropriate tool functions.
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.conversation_history = []
        
        # Define available tools for function calling
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_headline_kpis",
                    "description": "Get headline KPIs: recoverable profit, ready groups, expected reactivations",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "list_cohorts",
                    "description": "List top customer cohorts sorted by profit potential",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "description": "Max number of cohorts to return", "default": 5}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_cohort_passport", 
                    "description": "Get detailed metrics for a specific cohort",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Cohort name (e.g. 'Premium engagement lapsed')"}
                        },
                        "required": ["name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "show_roi",
                    "description": "Calculate ROI projection for a cohort",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Cohort name"}
                        },
                        "required": ["name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_definitions",
                    "description": "Get definitions of business terms (Come-Back Odds, Activity, etc.)",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compare_cohorts",
                    "description": "Compare two cohorts side by side",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "a": {"type": "string", "description": "First cohort name"},
                            "b": {"type": "string", "description": "Second cohort name"}
                        },
                        "required": ["a", "b"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "export_copy_pack",
                    "description": "Export copy pack and data files for campaign delivery",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Cohort name to export"}
                        },
                        "required": ["name"]
                    }
                }
            }
        ]
    
    def _execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool function with given arguments."""
        
        function_map = {
            "get_headline_kpis": get_headline_kpis,
            "list_cohorts": list_cohorts,
            "get_cohort_passport": get_cohort_passport,
            "show_roi": show_roi,
            "list_definitions": list_definitions,
            "compare_cohorts": compare_cohorts,
            "export_copy_pack": export_copy_pack
        }
        
        if function_name not in function_map:
            return {"error": f"Unknown function: {function_name}"}
        
        try:
            func = function_map[function_name]
            if arguments:
                return func(**arguments)
            else:
                return func()
        except Exception as e:
            return {"error": f"Function execution failed: {str(e)}"}
    
    def chat(self, user_message: str) -> Tuple[str, Optional[Dict]]:
        """
        Process user message and return assistant response.
        
        Args:
            user_message: User's question or request
            
        Returns:
            Tuple of (assistant_message, tool_data)
        """
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # System prompt for retention assistant
        system_prompt = """You are a Retention Assistant for Churn Radar. You help marketers understand their customer retention data and generate re-engagement campaigns.

Key principles:
- Use tools to fetch real facts; never invent numbers
- Speak plainly and explain business terms on first mention  
- Format currency as ₹12,34,567 (Indian format)
- When showing cohorts, include the one-line "why" reason
- For copy requests, mention that messages have brand-safe evaluation badges
- Keep responses focused and actionable

Common user intents:
- "What should I do today?" → get_headline_kpis + list_cohorts(3) 
- "Open [cohort name]" → get_cohort_passport + show_roi
- "What's [term]?" → list_definitions (find the term)
- "Compare A vs B" → compare_cohorts
- "Export [cohort]" → export_copy_pack

Be conversational but data-driven. Always lead with the most important insight."""

        messages = [{"role": "system", "content": system_prompt}] + self.conversation_history
        
        try:
            headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}
            payload = {
                'model': 'gpt-3.5-turbo',
                'messages': messages,
                'tools': self.tools,
                'tool_choice': 'auto',
                'max_tokens': 800,
                'temperature': 0.3
            }
            
            response = httpx.post(
                'https://api.openai.com/v1/chat/completions',
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                return f"Sorry, I'm having trouble connecting. Please try again.", None
            
            result = response.json()
            assistant_message = result['choices'][0]['message']
            
            # Check if the assistant wants to call tools
            if assistant_message.get('tool_calls'):
                tool_results = []
                
                for tool_call in assistant_message['tool_calls']:
                    function_name = tool_call['function']['name']
                    arguments = json.loads(tool_call['function']['arguments'])
                    
                    # Execute the function
                    function_result = self._execute_function(function_name, arguments)
                    tool_results.append({
                        'call': tool_call,
                        'result': function_result
                    })
                    
                    # Add tool result to conversation
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call]
                    })
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call['id'],
                        "content": json.dumps(function_result)
                    })
                
                # Get final response with tool results
                messages = [{"role": "system", "content": system_prompt}] + self.conversation_history
                
                final_response = httpx.post(
                    'https://api.openai.com/v1/chat/completions',
                    json={
                        'model': 'gpt-3.5-turbo',
                        'messages': messages,
                        'max_tokens': 800,
                        'temperature': 0.3
                    },
                    headers=headers,
                    timeout=30
                )
                
                if final_response.status_code == 200:
                    final_result = final_response.json()
                    final_message = final_result['choices'][0]['message']['content']
                    
                    # Add to conversation history
                    self.conversation_history.append({"role": "assistant", "content": final_message})
                    
                    # Return response with tool data for UI enhancements
                    return final_message, tool_results[0]['result'] if tool_results else None
                else:
                    return "I found the data but had trouble formatting the response. Please try again.", None
            
            else:
                # No tools needed, direct response
                response_text = assistant_message['content']
                self.conversation_history.append({"role": "assistant", "content": response_text})
                return response_text, None
                
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}", None
    
    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict]:
        """Get current conversation history."""
        return self.conversation_history.copy()


# Convenience function for single interactions
def ask_retention_assistant(question: str) -> Tuple[str, Optional[Dict]]:
    """
    Ask a single question to the retention assistant.
    
    Args:
        question: User question
        
    Returns:
        Tuple of (response, tool_data)
    """
    orchestrator = ConversationOrchestrator()
    return orchestrator.chat(question)