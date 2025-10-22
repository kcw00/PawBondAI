from fastapi import APIRouter, HTTPException
from app.services.matching_service import matching_service
from app.services.vertex_gemini_service import vertex_gemini_service
from app.core.agent import agent
from app.models.schemas import ChatRequest, AnalyzeApplicationRequest

router = APIRouter()


# Chat Endpoints
# Main conversational endpoint
# ~~~~worked! testing done by with postman.
@router.post("/message")
async def handle_chat_message(request: ChatRequest):
    """
    Main conversational endpoint
    Determines intent and routes to appropriate service or AI agent
    """
    try:
        # Detect intent using Vertex Gemini
        intent = await vertex_gemini_service.detect_intent(request.message)

        # Route based on intent type
        if intent["type"] == "find_adopters":
            # Use matching service for adopter search
            result = await matching_service.find_adopters(
                query=request.message, filters=intent.get("filters")
            )
            return {"success": True, "intent": intent["type"], "response": result}

        elif intent["type"] == "analyze_application":
            # Use matching service for application analysis
            result = await matching_service.analyze_application(request.message)
            return {"success": True, "intent": intent["type"], "response": result}

        else:
            # Check if this is a dog info query or similar cases query
            message_lower = request.message.lower()
            is_dog_query = any(
                keyword in message_lower
                for keyword in [
                    "tell me about",
                    "show me",
                    "dog profile",
                    "medical history",
                    "similar cases",
                    "find similar",
                    "like this",
                    "dog_",  # Match dog_001, dog_002, etc.
                ]
            )

            if is_dog_query:
                # Use AI agent with tools for dog info and similar cases
                session_id = (
                    request.context.get("session_id", "default") if request.context else "default"
                )
                result = await agent.chat(
                    user_message=request.message,
                    session_id=session_id,
                    context=request.context,
                )
                return {
                    "success": True,
                    "intent": "dog_info_with_tools",
                    "response": result["response"],
                    "session_id": result["session_id"],
                }
            else:
                # General question - use basic Gemini
                result = await vertex_gemini_service.generate_response(
                    prompt=request.message, context=request.context
                )
                return {"success": True, "intent": "general", "response": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Analyze Adoption Application
# ~~~~worked! testing done by with postman.
@router.post("/analyze-application")
async def analyze_application(request: AnalyzeApplicationRequest):
    """
    Analyze an adoption application
    THE KEY FEATURE for demo
    """
    try:
        analysis = await matching_service.analyze_application(request.application_text)

        return {"success": True, "analysis": analysis}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search-insights/{query_id}")
async def get_search_insights(query_id: str):
    """
    Get Elasticsearch query details for visualization
    """
    # TODO: Implement query caching and retrieval
    return {
        "success": True,
        "insights": {
            "query_id": query_id,
            # Query breakdown, timing, etc.
        },
    }
