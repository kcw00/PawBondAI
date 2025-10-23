from google.cloud import storage
from app.core.config import get_settings
import uuid
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.core.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class StorageService:
    def __init__(self):
        if settings.gcs_bucket_name:
            self.client = storage.Client(project=settings.gcp_project_id)
            self.bucket = self.client.bucket(settings.gcs_bucket_name)
        else:
            self.client = None
            self.bucket = None

    def upload_image(self, file_data: bytes, content_type: str) -> Optional[str]:
        """Upload image to GCS and return public URL"""
        if not self.bucket:
            return None

        # Generate unique filename
        filename = f"images/{uuid.uuid4()}.jpg"
        blob = self.bucket.blob(filename)

        # Upload
        blob.upload_from_string(file_data, content_type=content_type)
        blob.make_public()

        return blob.public_url

    def delete_image(self, image_url: str):
        """Delete image from GCS"""
        if not self.bucket:
            return

        # Extract filename from URL
        filename = image_url.split("/")[-1]
        blob = self.bucket.blob(f"images/{filename}")
        blob.delete()

    # ========================================
    # CHAT HISTORY METHODS
    # ========================================

    def save_chat_message(
        self,
        session_id: str,
        role: str,
        content: str,
        intent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save a chat message to GCS
        Storage path: chat-history/{session_id}/messages.json
        """
        if not self.bucket:
            logger.warning("GCS bucket not configured, cannot save chat history")
            return False

        try:
            # Path for this session's messages
            blob_path = f"chat-history/{session_id}/messages.json"
            blob = self.bucket.blob(blob_path)

            # Get existing messages or create new list
            messages = []
            if blob.exists():
                existing_data = blob.download_as_text()
                messages = json.loads(existing_data)

            # Add new message
            messages.append({
                "role": role,
                "content": content,
                "intent": intent,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            })

            # Save back to GCS
            blob.upload_from_string(
                json.dumps(messages, indent=2),
                content_type="application/json"
            )

            logger.info(f"Saved message to session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving chat message: {e}")
            return False

    def get_chat_history(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve chat history for a session
        Returns: {session_id, messages: [...], created_at, updated_at}
        """
        if not self.bucket:
            return None

        try:
            blob_path = f"chat-history/{session_id}/messages.json"
            blob = self.bucket.blob(blob_path)

            if not blob.exists():
                return None

            # Download messages
            data = blob.download_as_text()
            messages = json.loads(data)

            # Get timestamps
            blob.reload()  # Load metadata
            created_at = blob.time_created
            updated_at = blob.updated

            return {
                "session_id": session_id,
                "messages": messages,
                "message_count": len(messages),
                "created_at": created_at.isoformat() if created_at else None,
                "updated_at": updated_at.isoformat() if updated_at else None,
            }

        except Exception as e:
            logger.error(f"Error retrieving chat history: {e}")
            return None

    def list_chat_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List all chat sessions
        Returns: [{session_id, created_at, message_count, preview}, ...]
        """
        if not self.bucket:
            return []

        try:
            # List all message files in chat-history/
            prefix = "chat-history/"
            blobs = self.bucket.list_blobs(prefix=prefix)

            sessions = []
            for blob in blobs:
                if blob.name.endswith("/messages.json"):
                    # Extract session_id from path
                    session_id = blob.name.split("/")[1]

                    # Download to get message count and preview
                    data = blob.download_as_text()
                    messages = json.loads(data)

                    # Get first user message as preview
                    preview = "No messages"
                    for msg in messages:
                        if msg.get("role") == "user":
                            preview = msg.get("content", "")[:100]
                            break

                    blob.reload()
                    sessions.append({
                        "session_id": session_id,
                        "created_at": blob.time_created.isoformat() if blob.time_created else None,
                        "updated_at": blob.updated.isoformat() if blob.updated else None,
                        "message_count": len(messages),
                        "preview": preview
                    })

                    if len(sessions) >= limit:
                        break

            # Sort by updated_at descending
            sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

            return sessions

        except Exception as e:
            logger.error(f"Error listing chat sessions: {e}")
            return []

    def delete_chat_session(self, session_id: str) -> bool:
        """Delete a chat session"""
        if not self.bucket:
            return False

        try:
            blob_path = f"chat-history/{session_id}/messages.json"
            blob = self.bucket.blob(blob_path)

            if blob.exists():
                blob.delete()
                logger.info(f"Deleted chat session {session_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error deleting chat session: {e}")
            return False


# Create singleton instance
storage_service = StorageService()
