from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from app.core.agent import agent
from typing import Optional, Dict, Any
import uuid

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    session_id = request.session_id or str(uuid.uuid4())

    try:
        result = await agent.chat(
            user_message=request.message, session_id=session_id, context=request.context
        )

        return ChatResponse(response=result["response"], session_id=result["session_id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/with-image")
async def chat_with_image(
    message: str,
    image: UploadFile = File(...),
    session_id: Optional[str] = None,
    context: Optional[str] = None,
):
    """Chat endpoint with image upload"""
    session_id = session_id or str(uuid.uuid4())

    # Read image
    image_bytes = await image.read()

    # Add image analysis to context
    import base64

    image_b64 = base64.b64encode(image_bytes).decode()

    # Construct message with image reference
    enhanced_message = f"{message}\n\n[User uploaded an image for analysis]"

    # Parse context if string
    context_dict = {}
    if context:
        import json

        context_dict = json.loads(context)

    # Add image to context
    context_dict["image_data"] = image_b64
    context_dict["has_image"] = True

    try:
        result = await agent.chat(
            user_message=enhanced_message, session_id=session_id, context=context_dict
        )

        return {
            "response": result["response"],
            "session_id": result["session_id"],
            "image_analyzed": True,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def end_session(session_id: str):
    """End a chat session"""
    if session_id in agent.chat_sessions:
        del agent.chat_sessions[session_id]
        return {"message": "Session ended", "session_id": session_id}
    else:
        raise HTTPException(status_code=404, detail="Session not found")
