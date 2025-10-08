from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from datetime import datetime
import uuid

from app.models.schemas import Dog, DogCreate
from app.services.elasticsearch_client import es_client
from app.services.storage_service import storage_service
from app.core.config import get_settings

settings = get_settings()
router = APIRouter()


@router.post("", response_model=Dog)
async def create_dog(dog: DogCreate):
    """Create a new dog profile"""
    dog_id = str(uuid.uuid4())
    dog_dict = dog.model_dump()
    dog_dict.update(
        {
            "id": dog_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "medical_history": [],
            "photos": [],
        }
    )

    # Index in Elasticsearch
    es_client.index_document(
        index_name=settings.dogs_index, document=dog_dict, doc_id=dog_id
    )

    return Dog(**dog_dict)


@router.get("/{dog_id}", response_model=Dog)
async def get_dog(dog_id: str):
    """Get dog profile by ID"""
    try:
        result = es_client.get_document(index_name=settings.dogs_index, doc_id=dog_id)
        return Dog(**result["_source"])
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Dog not found: {str(e)}")


@router.get("", response_model=List[Dog])
async def list_dogs(limit: int = 10):
    """List all dogs"""
    query = {
        "query": {"match_all": {}},
        "size": limit,
        "sort": [{"created_at": {"order": "desc"}}],
    }

    result = es_client.search(index_name=settings.dogs_index, query=query)

    dogs = [Dog(**hit["_source"]) for hit in result["hits"]["hits"]]
    return dogs


@router.put("/{dog_id}", response_model=Dog)
async def update_dog(dog_id: str, dog_update: DogCreate):
    """Update dog profile"""
    try:
        # Get existing dog
        existing = es_client.get_document(index_name=settings.dogs_index, doc_id=dog_id)

        # Update fields
        updated_dict = existing["_source"]
        updated_dict.update(dog_update.model_dump(exclude_unset=True))
        updated_dict["updated_at"] = datetime.now()

        # Save
        es_client.update_document(
            index_name=settings.dogs_index, doc_id=dog_id, document=updated_dict
        )

        return Dog(**updated_dict)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Dog not found: {str(e)}")


@router.delete("/{dog_id}")
async def delete_dog(dog_id: str):
    """Delete dog profile"""
    try:
        es_client.delete_document(index_name=settings.dogs_index, doc_id=dog_id)
        return {"message": "Dog deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Dog not found: {str(e)}")


@router.get("/{dog_id}/history")
async def get_dog_history(dog_id: str):
    """Get medical history for a dog"""
    try:
        result = es_client.get_document(index_name=settings.dogs_index, doc_id=dog_id)
        return {
            "dog_id": dog_id,
            "medical_history": result["_source"].get("medical_history", []),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Dog not found: {str(e)}")


@router.post("/{dog_id}/photos")
async def upload_dog_photo(dog_id: str, file: UploadFile = File(...)):
    """Upload a photo for a dog"""
    try:
        # Read file
        file_data = await file.read()

        # Upload to GCS
        image_url = storage_service.upload_image(file_data, file.content_type)

        if not image_url:
            raise HTTPException(
                status_code=500, detail="Storage service not configured"
            )

        # Update dog profile
        dog = es_client.get_document(index_name=settings.dogs_index, doc_id=dog_id)

        photos = dog["_source"].get("photos", [])
        photos.append(image_url)

        es_client.update_document(
            index_name=settings.dogs_index, doc_id=dog_id, document={"photos": photos}
        )

        return {"image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
