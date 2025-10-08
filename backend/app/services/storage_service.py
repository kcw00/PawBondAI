from google.cloud import storage
from app.core.config import get_settings
import uuid
from typing import Optional

settings = get_settings()


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


# Create singleton instance
storage_service = StorageService()
