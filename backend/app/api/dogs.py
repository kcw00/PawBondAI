from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from typing import List, Dict, Any
from datetime import datetime
import uuid
import time

from app.models.schemas import Dog, DogCreate
from app.services.elasticsearch_client import es_client
from app.services.storage_service import storage_service
from app.core.config import get_settings
from app.core.logger import setup_logger


settings = get_settings()
router = APIRouter()
logger = setup_logger(__name__)


# ~~~~~worked! testing done by with postman.
@router.post("", response_model=Dog)
async def create_dog(dog: DogCreate):
    """Create a new dog profile"""
    logger.info(f"Received request to create dog: {dog.name}")
    logger.debug(f"Dog data: {dog}")
    dog_id = str(uuid.uuid4())
    dog_dict = dog.model_dump()
    dog_dict.update(
        {
            "dog_id": dog_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "medical_history": [],
            "photos": [],
        }
    )

    # Index directly instead of using background task
    try:
        result = await es_client.index_document(
            index_name=settings.dogs_index, document=dog_dict, doc_id=dog_id
        )
        logger.info(f"Dog profile created and indexed with ID: {dog_id}")
        logger.debug(f"Indexing result: {result}")
    except Exception as e:
        logger.error(f"Failed to index dog profile {dog_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create dog profile: {str(e)}")
    return Dog(**dog_dict)


def index_dog_profile(index_name: str, document: Dict[str, Any], doc_id: str):
    """Background task to index a dog profile with improved error handling."""
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Try to index the document
            es_client.index_document(index_name=index_name, document=document, doc_id=doc_id)
            logger.info(f"Dog profile indexed successfully: {doc_id}")
            return
        except Exception as e:
            retry_count += 1
            logger.warning(
                f"Attempt {retry_count}/{max_retries} failed to index dog profile {doc_id}: {e}"
            )
            if retry_count < max_retries:
                # Wait before retrying (exponential backoff)
                time.sleep(2**retry_count)
            else:
                logger.error(
                    f"Failed to index dog profile {doc_id} after {max_retries} attempts: {e}"
                )
                # You might want to implement a dead letter queue or other recovery mechanism here


# ~~~~~worked! testing done by with postman.
# get age_display needed for frontend display, but not needed in backend db.
@router.get("/{dog_id}", response_model=Dog)
async def get_dog(dog_id: str):
    """Get dog profile by ID"""
    try:
        result = await es_client.get_document(index_name=settings.dogs_index, doc_id=dog_id)
        dog_data = result["_source"]

        # Ensure medical_history is a list
        if "medical_history" in dog_data and isinstance(dog_data["medical_history"], str):
            dog_data["medical_history"] = (
                [dog_data["medical_history"]] if dog_data["medical_history"] else []
            )

        return Dog(**dog_data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Dog not found: {str(e)}")


# ~~~~~worked! testing done by with postman.
# get age_display needed for frontend display, but not needed in backend db.
@router.get("", response_model=List[Dog])
async def list_dogs(limit: int = 10):
    """List all dogs"""
    query = {
        "query": {"match_all": {}},
        "size": limit,
        "sort": [{"created_at": {"order": "desc"}}],
    }

    result = await es_client.search(index_name=settings.dogs_index, query=query)

    dogs = []
    for hit in result["hits"]["hits"]:
        try:
            dog_data = hit["_source"]

            # Ensure medical_history is a list
            if "medical_history" in dog_data and isinstance(dog_data["medical_history"], str):
                dog_data["medical_history"] = (
                    [dog_data["medical_history"]] if dog_data["medical_history"] else []
                )

            # Ensure created_at and updated_at are strings
            if "created_at" in dog_data and not isinstance(dog_data["created_at"], str):
                dog_data["created_at"] = str(dog_data["created_at"])
            if "updated_at" in dog_data and not isinstance(dog_data["updated_at"], str):
                dog_data["updated_at"] = str(dog_data["updated_at"])

            dogs.append(Dog(**dog_data))
        except Exception as e:
            logger.error(f"Failed to parse dog document {hit.get('_id')}: {e}")
            logger.debug(f"Dog data: {dog_data}")
            # Skip invalid documents
            continue

    return dogs


# ~~~~~worked! testing done by with postman.
@router.put("/{dog_id}", response_model=Dog)
async def update_dog(dog_id: str, dog_update: DogCreate):
    """Update dog profile"""
    try:
        # Get existing dog
        existing = await es_client.get_document(index_name=settings.dogs_index, doc_id=dog_id)

        # Update fields
        updated_dict = existing["_source"]
        updated_dict.update(dog_update.model_dump(exclude_unset=True))
        updated_dict["updated_at"] = datetime.now().isoformat()

        # Ensure medical_history is a list
        if "medical_history" in updated_dict and isinstance(updated_dict["medical_history"], str):
            updated_dict["medical_history"] = (
                [updated_dict["medical_history"]] if updated_dict["medical_history"] else []
            )

        # Save
        await es_client.update_document(
            index_name=settings.dogs_index, doc_id=dog_id, document=updated_dict
        )

        return Dog(**updated_dict)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Dog not found: {str(e)}")


# ~~~~~worked! testing done by with postman.
# need to log the dog_name when deleting.
@router.delete("/{dog_id}")
async def delete_dog(dog_id: str):
    """Delete dog profile"""
    from elasticsearch import NotFoundError

    try:
        result = await es_client.delete_document(index_name=settings.dogs_index, doc_id=dog_id)

        # Check the result - Elasticsearch returns a dict with 'result' key
        if isinstance(result, dict):
            es_result = result.get('result', '')
            logger.info(f"Dog {dog_id} deletion result: {es_result}")

            if es_result == 'deleted':
                return {"message": "Dog deleted successfully", "dog_id": dog_id}
            elif es_result == 'not_found':
                raise HTTPException(status_code=404, detail=f"Dog not found: {dog_id}")

        return {"message": "Dog deleted successfully", "dog_id": dog_id}

    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"Dog not found: {dog_id}")
    except Exception as e:
        logger.error(f"Error deleting dog {dog_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete dog: {str(e)}")


# ~~~~~worked! testing done by with postman.
@router.get("/{dog_id}/history")
async def get_dog_history(dog_id: str):
    """Get medical history for a dog"""
    try:
        result = await es_client.get_document(index_name=settings.dogs_index, doc_id=dog_id)
        return {
            "dog_id": dog_id,
            "medical_history": result["_source"].get("medical_history", []),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Dog not found: {str(e)}")


# need to implement later
@router.post("/{dog_id}/photos")
async def upload_dog_photo(dog_id: str, file: UploadFile = File(...)):
    """Upload a photo for a dog"""
    try:
        # Read file
        file_data = await file.read()

        # Upload to GCS
        image_url = storage_service.upload_image(file_data, file.content_type)

        if not image_url:
            raise HTTPException(status_code=500, detail="Storage service not configured")

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
