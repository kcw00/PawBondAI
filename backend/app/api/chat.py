from fastapi import APIRouter, HTTPException
from app.services.matching_service import matching_service
from app.services.vertex_gemini_service import vertex_gemini_service
from app.models.schemas import ChatRequest, AnalyzeApplicationRequest

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message")
async def handle_chat_message(request: ChatRequest):
    """
    Main conversational endpoint
    Determines intent and routes to appropriate service
    """
    try:
        # Detect intent using Vertex Gemini
        intent = await vertex_gemini_service.detect_intent(request.message)

        if intent["type"] == "find_adopters":
            result = await matching_service.find_adopters(
                query=request.message, filters=intent.get("filters")
            )
        elif intent["type"] == "analyze_application":
            result = await matching_service.analyze_application(request.message)
        else:
            # General question
            result = await vertex_gemini_service.generate_response(
                prompt=request.message, context=request.context
            )

        return {"success": True, "intent": intent["type"], "response": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
