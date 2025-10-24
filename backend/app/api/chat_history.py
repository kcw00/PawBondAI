from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.storage_service import storage_service
from app.models.schemas import (
    ChatHistoryResponse,
    ChatSessionListResponse,
    ChatMessage,
    SaveMessageRequest,
    UpdateChatNameRequest
)
from app.core.logger import setup_logger
import uuid

router = APIRouter()
logger = setup_logger(__name__)


@router.post("/save")
async def save_message(request: SaveMessageRequest):
    """
    Save a chat message to GCS
    """
    try:
        success = storage_service.save_chat_message(
            session_id=request.session_id,
            role=request.role,
            content=request.content,
            intent=request.intent,
            metadata=request.metadata
        )

        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to save message. Check if GCS bucket is configured."
            )

        return {"success": True, "session_id": request.session_id}

    except Exception as e:
        logger.error(f"Error saving message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_sessions(limit: int = Query(50, ge=1, le=100)):
    """
    List all chat sessions with previews
    """
    try:
        sessions = storage_service.list_chat_sessions(limit=limit)

        return ChatSessionListResponse(
            sessions=sessions,
            total=len(sessions)
        )

    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=ChatHistoryResponse)
async def get_session_history(session_id: str):
    """
    Get full chat history for a session
    """
    try:
        history = storage_service.get_chat_history(session_id)

        if not history:
            raise HTTPException(status_code=404, detail="Session not found")

        # Include name in metadata
        metadata = history.get("metadata") or {}
        if history.get("name"):
            metadata["name"] = history["name"]

        # Convert messages and log metadata
        converted_messages = []
        for i, msg in enumerate(history["messages"]):
            chat_msg = ChatMessage(**msg)
            if chat_msg.metadata:
                logger.info(f"API returning message {i} with metadata keys: {list(chat_msg.metadata.keys())}")
            converted_messages.append(chat_msg)

        return ChatHistoryResponse(
            session_id=history["session_id"],
            created_at=history["created_at"],
            updated_at=history["updated_at"],
            message_count=history["message_count"],
            messages=converted_messages,
            metadata=metadata if metadata else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{session_id}/name")
async def update_chat_name(session_id: str, request: UpdateChatNameRequest):
    """
    Update the custom name of a chat session
    """
    try:
        success = storage_service.update_chat_name(session_id, request.name)

        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"success": True, "message": f"Chat name updated to '{request.name}'"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating chat name: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a chat session
    """
    try:
        success = storage_service.delete_chat_session(session_id)

        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"success": True, "message": f"Session {session_id} deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/new")
async def create_new_session():
    """
    Generate a new session ID for starting a chat
    """
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}
