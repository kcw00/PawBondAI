from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from typing import List, Dict, Any
from datetime import datetime
import uuid

from app.models.schemas import (
    DogResponse,
    DogCreate,
    MatchingResponse,
    RankedApplication,
    CompatibilityResult,
    DimensionScore,
    ApplicationResponse,
    IntakeAssessmentRequest,
    IntakeAssessmentResponse,
)
from app.services.elasticsearch_client import es_client
from app.services.storage_service import storage_service
from app.services.compatibility_service import compatibility_service
from app.services.vertex_ai_service import vertex_ai_service
from app.core.config import get_settings
from app.core.logger import setup_logger
from app.models.es_documents import Dog
from elasticsearch.dsl import AsyncSearch


settings = get_settings()
router = APIRouter()
logger = setup_logger(__name__)


@router.post("", response_model=DogResponse)
async def create_dog(dog: DogCreate):
    """Create a new dog profile using AsyncDocument"""
    logger.info(f"Received request to create dog: {dog.name}")
    dog_id = str(uuid.uuid4())

    try:
        # Create AsyncDocument instance
        doc = Dog(meta={'id': dog_id})

        # Set fields from request
        doc.name = dog.name
        doc.breed = dog.breed
        doc.age = dog.age
        doc.weight_kg = dog.weight_kg
        doc.sex = dog.sex
        doc.rescue_date = dog.rescue_date
        doc.adoption_status = dog.adoption_status
        doc.behavioral_notes = dog.behavioral_notes
        doc.combined_profile = dog.combined_profile

        # Initialize empty arrays
        doc.medical_history = []
        doc.photos = []

        # Save to Elasticsearch (timestamps set automatically)
        await doc.save(using=es_client.client)

        logger.info(f"Dog profile created and indexed with ID: {dog_id}")

        return DogResponse(
            id=dog_id,
            name=dog.name,
            breed=dog.breed,
            age=dog.age,
            weight_kg=dog.weight_kg,
            sex=dog.sex,
            rescue_date=dog.rescue_date,
            adoption_status=dog.adoption_status,
            behavioral_notes=dog.behavioral_notes,
            combined_profile=dog.combined_profile,
            medical_history=[],
            photos=[],
            created_at=doc.created_at.isoformat() if doc.created_at else None,
            updated_at=doc.updated_at.isoformat() if doc.updated_at else None,
        )
    except Exception as e:
        logger.error(f"Failed to create dog profile {dog_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create dog profile: {str(e)}")


@router.get("/{dog_id}", response_model=DogResponse)
async def get_dog(dog_id: str):
    """Get dog profile by ID using AsyncDocument"""
    try:
        doc = await Dog.get(id=dog_id, using=es_client.client)

        return DogResponse(
            id=dog_id,
            name=doc.name,
            breed=doc.breed,
            age=doc.age,
            weight_kg=doc.weight_kg,
            sex=doc.sex,
            rescue_date=doc.rescue_date,
            adoption_status=doc.adoption_status,
            behavioral_notes=doc.behavioral_notes,
            combined_profile=doc.combined_profile,
            medical_history=doc.medical_history if doc.medical_history else [],
            photos=doc.photos if doc.photos else [],
            created_at=doc.created_at.isoformat() if doc.created_at else None,
            updated_at=doc.updated_at.isoformat() if doc.updated_at else None,
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Dog not found: {str(e)}")


@router.get("", response_model=List[DogResponse])
async def list_dogs(limit: int = 10):
    """List all dogs using AsyncSearch"""
    try:
        s = AsyncSearch(using=es_client.client, index="dogs")
        s = s.query("match_all")
        s = s.sort("-created_at")
        s = s[0:limit]

        response = await s.execute()

        dogs = []
        for hit in response:
            try:
                dogs.append(DogResponse(
                    id=hit.meta.id,
                    name=hit.name,
                    breed=hit.breed,
                    age=hit.age,
                    weight_kg=hit.weight_kg,
                    sex=hit.sex,
                    rescue_date=hit.rescue_date,
                    adoption_status=hit.adoption_status,
                    behavioral_notes=hit.behavioral_notes,
                    combined_profile=hit.combined_profile,
                    medical_history=hit.medical_history if hasattr(hit, 'medical_history') and hit.medical_history else [],
                    photos=hit.photos if hasattr(hit, 'photos') and hit.photos else [],
                    created_at=hit.created_at.isoformat() if hasattr(hit, 'created_at') and hit.created_at else None,
                    updated_at=hit.updated_at.isoformat() if hasattr(hit, 'updated_at') and hit.updated_at else None,
                ))
            except Exception as e:
                logger.error(f"Failed to parse dog document {hit.meta.id}: {e}")
                # Skip invalid documents
                continue

        return dogs
    except Exception as e:
        logger.error(f"Error listing dogs: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing dogs: {str(e)}")


@router.put("/{dog_id}", response_model=DogResponse)
async def update_dog(dog_id: str, dog_update: DogCreate):
    """Update dog profile using AsyncDocument"""
    try:
        # Get existing dog
        doc = await Dog.get(id=dog_id, using=es_client.client)

        # Update fields
        doc.name = dog_update.name
        doc.breed = dog_update.breed
        doc.age = dog_update.age
        doc.weight_kg = dog_update.weight_kg
        doc.sex = dog_update.sex
        doc.rescue_date = dog_update.rescue_date
        doc.adoption_status = dog_update.adoption_status
        doc.behavioral_notes = dog_update.behavioral_notes
        doc.combined_profile = dog_update.combined_profile

        # Save (updated_at set automatically by save method)
        await doc.save(using=es_client.client)

        logger.info(f"Updated dog profile {dog_id}")

        return DogResponse(
            id=dog_id,
            name=doc.name,
            breed=doc.breed,
            age=doc.age,
            weight_kg=doc.weight_kg,
            sex=doc.sex,
            rescue_date=doc.rescue_date,
            adoption_status=doc.adoption_status,
            behavioral_notes=doc.behavioral_notes,
            combined_profile=doc.combined_profile,
            medical_history=doc.medical_history if doc.medical_history else [],
            photos=doc.photos if doc.photos else [],
            created_at=doc.created_at.isoformat() if doc.created_at else None,
            updated_at=doc.updated_at.isoformat() if doc.updated_at else None,
        )
    except Exception as e:
        logger.error(f"Error updating dog {dog_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Dog not found: {str(e)}")


@router.delete("/{dog_id}")
async def delete_dog(dog_id: str):
    """Delete dog profile using AsyncDocument"""
    try:
        doc = await Dog.get(id=dog_id, using=es_client.client)
        dog_name = doc.name

        await doc.delete(using=es_client.client)

        logger.info(f"Deleted dog profile {dog_id} (name: {dog_name})")
        return {"message": "Dog deleted successfully", "id": dog_id, "name": dog_name}

    except Exception as e:
        logger.error(f"Error deleting dog {dog_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Dog not found: {str(e)}")


@router.get("/{dog_id}/history")
async def get_dog_history(dog_id: str):
    """Get medical history for a dog using AsyncDocument"""
    try:
        doc = await Dog.get(id=dog_id, using=es_client.client)
        return {
            "id": dog_id,
            "name": doc.name,
            "medical_history": doc.medical_history if doc.medical_history else [],
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Dog not found: {str(e)}")


@router.post("/{dog_id}/photos")
async def upload_dog_photo(dog_id: str, file: UploadFile = File(...)):
    """Upload a photo for a dog using AsyncDocument"""
    try:
        # Read file
        file_data = await file.read()

        # Upload to GCS
        image_url = storage_service.upload_image(file_data, file.content_type)

        if not image_url:
            raise HTTPException(status_code=500, detail="Storage service not configured")

        # Get dog and update photos
        doc = await Dog.get(id=dog_id, using=es_client.client)

        if not doc.photos:
            doc.photos = []
        doc.photos.append(image_url)

        await doc.save(using=es_client.client)

        logger.info(f"Added photo to dog {dog_id}")
        return {"image_url": image_url, "total_photos": len(doc.photos)}
    except Exception as e:
        logger.error(f"Error uploading photo for dog {dog_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/{dog_id}/matches", response_model=MatchingResponse)
async def get_matching_applications(dog_id: str, limit: int = 10):
    """
    Smart matching endpoint - ranks all applications for a specific dog

    Returns applications sorted by compatibility score with detailed breakdown
    """
    try:
        # Verify dog exists
        await es_client.get_document(index_name=settings.dogs_index, id=dog_id)

        # Get ranked applications
        ranked = await compatibility_service.rank_applications_for_dog(dog_id, limit)

        # Convert to response format
        ranked_applications = []
        for item in ranked:
            app_data = item["application"]
            compat_data = item["compatibility"]

            # Create ApplicationResponse
            application_response = ApplicationResponse(**app_data)

            # Create CompatibilityResult
            compatibility_result = CompatibilityResult(
                overall_score=compat_data["overall_score"],
                dimension_scores=DimensionScore(**compat_data["dimension_scores"]),
                recommendation=compat_data["recommendation"],
                concerns=compat_data["concerns"],
                application_id=compat_data["application_id"],
                dog_id=compat_data["dog_id"],
            )

            ranked_applications.append(
                RankedApplication(
                    application=application_response,
                    compatibility=compatibility_result,
                )
            )

        logger.info(
            f"Retrieved {len(ranked_applications)} matching applications for dog {dog_id}"
        )

        return MatchingResponse(
            dog_id=dog_id,
            total_applications=len(ranked_applications),
            ranked_applications=ranked_applications,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting matching applications for dog {dog_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get matching applications: {str(e)}"
        )


@router.post("/intake-assessment", response_model=IntakeAssessmentResponse)
async def create_intake_assessment(
    photo: UploadFile = File(...),
    dog_name: str = "",
    breed: str = "",
    approximate_age: int = 0,
    rescue_notes: str = "",
):
    """
    Smart intake assessment endpoint with AI-powered photo analysis

    Analyzes uploaded dog photo using Gemini Vision to assess:
    - Physical health indicators
    - Breed characteristics
    - Approximate age
    - Body condition
    - Visible medical concerns

    Creates preliminary dog profile with recommendations
    """
    try:
        # Read photo
        photo_bytes = await photo.read()

        # Analyze photo with Gemini Vision
        analysis_prompt = f"""
        This is an intake photo for a rescue dog.

        Dog Information:
        - Name: {dog_name or "Unknown"}
        - Reported Breed: {breed or "Unknown"}
        - Approximate Age: {approximate_age or "Unknown"} years
        - Rescue Notes: {rescue_notes or "None provided"}

        Please provide a comprehensive intake assessment.
        """

        visual_analysis = await vertex_ai_service.analyze_image(
            photo_bytes, analysis_prompt
        )

        # Parse analysis to extract structured information
        medical_concerns = []
        recommended_actions = []
        urgency_level = "medium"

        analysis_lower = visual_analysis.lower()

        # Identify medical concerns
        concern_keywords = [
            "injury",
            "wound",
            "skin condition",
            "malnutrition",
            "emaciated",
            "overweight",
            "limping",
            "eye issue",
            "ear infection",
            "dental",
            "parasite",
        ]

        for keyword in concern_keywords:
            if keyword in analysis_lower:
                medical_concerns.append(keyword.title())

        # Determine urgency
        urgent_keywords = ["emergency", "severe", "critical", "immediate", "urgent"]
        if any(keyword in analysis_lower for keyword in urgent_keywords):
            urgency_level = "high"
            recommended_actions.append("Schedule immediate veterinary examination")
        elif not medical_concerns:
            urgency_level = "low"

        # Generate recommendations
        if "underweight" in analysis_lower or "malnourished" in analysis_lower:
            recommended_actions.append("Develop nutritional recovery plan")

        if "skin" in analysis_lower:
            recommended_actions.append("Skin examination and treatment protocol")

        if "behavioral" in analysis_lower or "anxious" in analysis_lower:
            recommended_actions.append("Behavioral assessment and socialization plan")

        if not recommended_actions:
            recommended_actions.append("Complete veterinary wellness check")
            recommended_actions.append("Begin standard intake protocol")

        # Create initial dog profile
        dog_id = str(uuid.uuid4())

        doc = Dog(meta={"id": dog_id})
        doc.name = dog_name or "Intake-" + dog_id[:8]
        doc.breed = breed
        doc.age = approximate_age if approximate_age > 0 else None
        doc.rescue_date = datetime.now()
        doc.adoption_status = "intake"
        doc.behavioral_notes = rescue_notes or "Initial intake - assessment pending"
        doc.medical_history = [f"Intake assessment completed: {visual_analysis[:200]}..."]

        await doc.save(using=es_client.client)

        logger.info(f"Intake assessment completed for dog {dog_id}")

        return IntakeAssessmentResponse(
            dog_id=dog_id,
            visual_analysis=visual_analysis,
            behavioral_assessment=rescue_notes or "Pending detailed behavioral assessment",
            medical_concerns=medical_concerns,
            recommended_actions=recommended_actions,
            urgency_level=urgency_level,
            created_at=datetime.now(),
        )

    except Exception as e:
        logger.error(f"Error creating intake assessment: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create intake assessment: {str(e)}"
        )
