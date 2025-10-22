from google import genai
from google.genai import types
from app.tools import TOOL_REGISTRY
from app.core.config import get_settings
from typing import List, Dict, Any
import json

settings = get_settings()

# Define tool schemas for Gemini using new SDK
TOOL_DECLARATIONS = [
    types.FunctionDeclaration(
        name="get_dog_profile",
        description="Retrieve complete dog profile including medical history, behavioral notes, and adoption status. Use when user asks about a specific dog by name or ID.",
        parameters={
            "type": "object",
            "properties": {
                "dog_id": {
                    "type": "string",
                    "description": "Unique dog identifier (e.g., 'dog_001', 'luna_001')",
                }
            },
            "required": ["dog_id"],
        },
    ),
    types.FunctionDeclaration(
        name="search_similar_cases",
        description="Find similar medical cases or adoption outcomes from the rescue database. Use to learn from past experiences and identify success patterns.",
        parameters={
            "type": "object",
            "properties": {
                "symptoms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of medical symptoms, behavioral traits, or conditions to match (e.g., ['heartworm', 'anxious', 'malnutrition'])",
                },
                "species": {
                    "type": "string",
                    "description": "Animal species",
                    "default": "dog",
                },
            },
            "required": ["symptoms"],
        },
    ),
]

# Create tool for Gemini
rescue_tool = types.Tool(function_declarations=TOOL_DECLARATIONS)

# System prompt
SYSTEM_PROMPT = """You are PawBondAI, an AI assistant for dog adoption matching and rescue operations.

YOUR ROLE:
- Help find the best matches between dogs and potential adopters
- Provide information about specific dogs in the system
- Learn from historical adoption outcomes to improve future matches
- Support rescue coordinators with data-driven insights

IMPORTANT GUIDELINES:
1. **Use Tools Wisely**: When user asks about a specific dog, use get_dog_profile to retrieve accurate data
2. **Learn from History**: When discussing adoption success, use search_similar_cases to find patterns
3. **Be Data-Driven**: Base recommendations on actual data, not assumptions
4. **Empathetic Tone**: Rescue workers are stressed and caring for vulnerable animals
5. **Clear Communication**: Provide actionable insights, not just raw data

WHEN TO USE TOOLS:
- "Tell me about Luna" or "Show me dog_001's profile" → get_dog_profile
- "Find similar cases to Luna" or "What dogs like this succeeded?" → search_similar_cases

IMPORTANT: If user mentions a dog name, try to infer the ID or ask for clarification.

Always be helpful, accurate, and kind."""


class PawBondAIAgent:
    def __init__(self):
        self.client = genai.Client(
            vertexai=True, project=settings.gcp_project_id, location=settings.vertex_ai_location
        )
        self.chat_sessions: Dict[str, Any] = {}

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return results"""
        tool_func = TOOL_REGISTRY.get(tool_name)
        if not tool_func:
            return {"error": f"Tool {tool_name} not found"}

        try:
            result = await tool_func(**arguments)
            return result
        except Exception as e:
            return {"error": str(e)}

    async def chat(
        self, user_message: str, session_id: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Main conversation loop with tool calling
        """
        # Add context if provided (e.g., dog_id, location)
        if context:
            context_prompt = f"\n\nContext: {json.dumps(context)}"
            user_message += context_prompt

        # Build config with tools
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[rescue_tool],
        )

        # Generate content with tools
        response = self.client.models.generate_content(
            model=settings.gemini_model, contents=user_message, config=config
        )

        # Handle function calls
        while response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            tool_name = function_call.name
            tool_args = dict(function_call.args)

            # Execute tool
            tool_result = await self.execute_tool(tool_name, tool_args)

            # Send tool result back to model
            response = self.client.models.generate_content(
                model=settings.gemini_model,
                contents=[
                    types.Part.from_function_response(
                        name=tool_name, response={"result": tool_result}
                    )
                ],
                config=config,
            )

        # Get final text response
        final_response = response.candidates[0].content.parts[0].text

        return {"response": final_response, "session_id": session_id}


agent = PawBondAIAgent()
