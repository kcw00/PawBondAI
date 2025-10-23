from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Body
from typing import List, Dict, Any
from datetime import datetime
import uuid
import json

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
    BulkDogUpload,
    BulkUploadResponse,
    MedicalEvent,
)
from app.services.elasticsearch_client import es_client
from app.services.storage_service import storage_service
from app.services.compatibility_service import compatibility_service
from app.services.vertex_gemini_service import vertex_gemini_service
from app.services.medical_extraction_service import medical_extraction_service
from app.core.config import get_settings
from app.core.logger import setup_logger
from app.models.es_documents import Dog
from elasticsearch.dsl import AsyncSearch
import csv
import io


settings = get_settings()
router = APIRouter()
logger = setup_logger(__name__)


@router.post("", response_model=DogResponse)
async def create_dog(dog: DogCreate):
    """
    Create a new dog profile with AI-powered medical extraction

    User provides:
    - Basic info (name, breed, age)
    - Medical history as free text (optional)

    AI automatically extracts:
    - Medical events timeline
    - Past conditions vs current conditions
    - Active treatments
    - Severity score
    - Adoption readiness status
    """
    logger.info(f"Received request to create dog: {dog.name}")
    dog_id = str(uuid.uuid4())

    try:
        # Create AsyncDocument instance
        doc = Dog(meta={"id": dog_id})

        # Set basic fields from request
        doc.name = dog.name
        doc.breed = dog.breed
        doc.age = dog.age
        doc.weight_kg = dog.weight_kg
        doc.sex = dog.sex
        doc.rescue_date = dog.rescue_date
        doc.adoption_status = dog.adoption_status
        doc.behavioral_notes = dog.behavioral_notes
        doc.combined_profile = dog.combined_profile

        # Initialize arrays
        doc.photos = []
        doc.medical_document_ids = []

        # AI-powered medical extraction
        if dog.medical_history and dog.medical_history.strip():
            logger.info(f"Extracting medical data for {dog.name}")
            extracted = await medical_extraction_service.extract_medical_data(
                dog.medical_history, dog.name
            )

            # Store original text
            doc.medical_history = dog.medical_history

            # Store extracted structured data
            doc.medical_events = extracted.get("medical_events", [])
            doc.past_conditions = extracted.get("past_conditions", [])
            doc.active_treatments = extracted.get("active_treatments", [])
            doc.severity_score = extracted.get("severity_score", 0)
            doc.adoption_readiness = extracted.get("adoption_readiness", "ready")

            logger.info(
                f"Medical extraction complete: {doc.adoption_readiness}, severity {doc.severity_score}"
            )
        else:
            # No medical history - set healthy defaults
            doc.medical_history = None
            doc.medical_events = []
            doc.past_conditions = []
            doc.active_treatments = []
            doc.severity_score = 0
            doc.adoption_readiness = "ready"

        # Save to Elasticsearch (timestamps set automatically)
        await doc.save(using=es_client.client)

        logger.info(f"Dog profile created and indexed with ID: {dog_id}")

        # Convert medical_events to MedicalEvent objects for response
        medical_events_response = [MedicalEvent(**event) for event in (doc.medical_events or [])]

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
            medical_history=doc.medical_history,
            medical_events=medical_events_response,
            past_conditions=doc.past_conditions,
            active_treatments=doc.active_treatments,
            severity_score=doc.severity_score,
            adoption_readiness=doc.adoption_readiness,
            medical_document_ids=doc.medical_document_ids,
            photos=doc.photos,
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

        # Convert medical_events to MedicalEvent objects for response
        medical_events_response = None
        if hasattr(doc, "medical_events") and doc.medical_events:
            medical_events_response = [MedicalEvent(**event) for event in doc.medical_events]

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
            medical_history=doc.medical_history if hasattr(doc, "medical_history") else None,
            medical_events=medical_events_response,
            past_conditions=doc.past_conditions if hasattr(doc, "past_conditions") else None,
            active_treatments=doc.active_treatments if hasattr(doc, "active_treatments") else None,
            severity_score=doc.severity_score if hasattr(doc, "severity_score") else None,
            adoption_readiness=(
                doc.adoption_readiness if hasattr(doc, "adoption_readiness") else None
            ),
            medical_document_ids=(
                doc.medical_document_ids if hasattr(doc, "medical_document_ids") else None
            ),
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
        logger.info(f"Fetching dogs from index: {settings.dogs_index}, limit: {limit}")
        s = AsyncSearch(using=es_client.client, index=settings.dogs_index)
        s = s.query("match_all")
        s = s.sort("-created_at")
        s = s[0:limit]

        response = await s.execute()
        logger.info(f"Elasticsearch returned {len(response)} hits")

        dogs = []
        for hit in response:
            try:
                # Convert hit to dict using to_dict() method
                hit_dict = hit.to_dict()
                
                # Handle medical_history - can be string or list
                medical_history = hit_dict.get("medical_history")
                if isinstance(medical_history, list):
                    medical_history = " ".join(str(x) for x in medical_history) if medical_history else None
                
                # medical_events should now be plain dicts after to_dict()
                medical_events = hit_dict.get("medical_events")
                
                dog_data = {
                    "id": hit.meta.id,
                    "name": hit_dict.get("name", "Unknown"),
                    "breed": hit_dict.get("breed"),
                    "age": hit_dict.get("age"),
                    "weight_kg": hit_dict.get("weight_kg"),
                    "sex": hit_dict.get("sex"),
                    "rescue_date": hit_dict.get("rescue_date"),
                    "adoption_status": hit_dict.get("adoption_status", "available"),
                    "behavioral_notes": hit_dict.get("behavioral_notes"),
                    "combined_profile": hit_dict.get("combined_profile"),
                    "medical_history": medical_history,
                    "photos": hit_dict.get("photos", []),
                    "medical_events": medical_events,
                    "past_conditions": hit_dict.get("past_conditions"),
                    "active_treatments": hit_dict.get("active_treatments"),
                    "severity_score": hit_dict.get("severity_score"),
                    "adoption_readiness": hit_dict.get("adoption_readiness"),
                    "medical_document_ids": hit_dict.get("medical_document_ids"),
                }
                
                # Handle dates
                if hasattr(hit, "created_at") and hit.created_at:
                    dog_data["created_at"] = hit.created_at.isoformat() if hasattr(hit.created_at, 'isoformat') else str(hit.created_at)
                else:
                    dog_data["created_at"] = None
                    
                if hasattr(hit, "updated_at") and hit.updated_at:
                    dog_data["updated_at"] = hit.updated_at.isoformat() if hasattr(hit.updated_at, 'isoformat') else str(hit.updated_at)
                else:
                    dog_data["updated_at"] = None
                
                dogs.append(DogResponse(**dog_data))
                logger.info(f"Successfully parsed dog: {dog_data['name']} ({hit.meta.id})")
            except Exception as e:
                logger.error(f"Failed to parse dog document {hit.meta.id}: {e}", exc_info=True)
                # Skip invalid documents
                continue

        logger.info(f"Returning {len(dogs)} dogs out of {len(response)} hits")
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
            medical_history=doc.medical_history if doc.medical_history else None,
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

        logger.info(f"Retrieved {len(ranked_applications)} matching applications for dog {dog_id}")

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

        visual_analysis = await vertex_gemini_service.analyze_image(photo_bytes, analysis_prompt)

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
        raise HTTPException(status_code=500, detail=f"Failed to create intake assessment: {str(e)}")


# Semantic Search Endpoint
# ~~~~~ worked! tested with postman
@router.post("/search", response_model=List[DogResponse])
async def search_dogs_semantic(
    query: str = Body(..., embed=True),
    field: str = Body("combined_profile", embed=True),
    limit: int = Body(10, embed=True, ge=1, le=100),
):
    """
    Semantic search for dogs using ES inference endpoint.
    Searches across behavioral_notes, combined_profile, or medical_history using embeddings.

    Args:
        query: Natural language search query
        field: Field to search (combined_profile, behavioral_notes, medical_history)
        limit: Number of results to return
    """
    try:
        # Validate field
        valid_fields = ["combined_profile", "behavioral_notes", "medical_history"]
        if field not in valid_fields:
            raise HTTPException(
                status_code=400, detail=f"Invalid field. Must be one of: {', '.join(valid_fields)}"
            )

        # Build semantic search using AsyncSearch
        s = AsyncSearch(using=es_client.client, index=settings.dogs_index)
        s = s.query("semantic", field=field, query=query)
        s = s[0:limit]

        response = await s.execute()

        dogs = []
        for hit in response:
            # Convert medical_events to MedicalEvent objects for response
            medical_events_response = None
            if hasattr(hit, "medical_events") and hit.medical_events:
                medical_events_response = [MedicalEvent(**event) for event in hit.medical_events]

            # Convert medical_history from list to string if needed
            medical_history_str = None
            if hasattr(hit, "medical_history") and hit.medical_history:
                # ES returns multi=True fields as AttrList, convert to string
                if hasattr(hit.medical_history, "__iter__") and not isinstance(
                    hit.medical_history, str
                ):
                    # It's a list or list-like, take first element
                    medical_history_str = (
                        hit.medical_history[0] if len(hit.medical_history) > 0 else None
                    )
                else:
                    medical_history_str = hit.medical_history

            dogs.append(
                DogResponse(
                    id=hit.meta.id,
                    name=hit.name,
                    breed=hit.breed,
                    age=hit.age,
                    weight_kg=hit.weight_kg if hasattr(hit, "weight_kg") else None,
                    sex=hit.sex,
                    rescue_date=hit.rescue_date if hasattr(hit, "rescue_date") else None,
                    adoption_status=(
                        hit.adoption_status if hasattr(hit, "adoption_status") else None
                    ),
                    behavioral_notes=(
                        hit.behavioral_notes if hasattr(hit, "behavioral_notes") else None
                    ),
                    medical_history=medical_history_str,
                    medical_events=medical_events_response,
                    past_conditions=(
                        hit.past_conditions if hasattr(hit, "past_conditions") else None
                    ),
                    active_treatments=(
                        hit.active_treatments if hasattr(hit, "active_treatments") else None
                    ),
                    severity_score=hit.severity_score if hasattr(hit, "severity_score") else None,
                    adoption_readiness=(
                        hit.adoption_readiness if hasattr(hit, "adoption_readiness") else None
                    ),
                    medical_document_ids=(
                        hit.medical_document_ids if hasattr(hit, "medical_document_ids") else None
                    ),
                    combined_profile=(
                        hit.combined_profile if hasattr(hit, "combined_profile") else None
                    ),
                    photos=hit.photos if hasattr(hit, "photos") else [],
                    created_at=hit.created_at if hasattr(hit, "created_at") else None,
                    updated_at=hit.updated_at if hasattr(hit, "updated_at") else None,
                )
            )

        logger.info(f"Semantic search for '{query}' on field '{field}' returned {len(dogs)} dogs")
        return dogs

    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")


@router.post("/bulk-upload", response_model=BulkUploadResponse)
async def bulk_upload_dogs(file: UploadFile = File(...)):
    """
    Bulk upload dogs via CSV file with AI-powered medical extraction

    CSV format:
    - name (required)
    - breed (optional)
    - age (optional)
    - medical_history (optional - free text)
    - weight_kg (optional)
    - sex (optional)

    AI automatically processes each row to extract:
    - Medical events timeline
    - Past conditions
    - Active treatments
    - Severity score
    - Adoption readiness

    Returns:
    - Total processed
    - Successful uploads
    - Failed uploads
    - List of created dog IDs
    """
    logger.info(f"Bulk upload initiated: {file.filename}")

    try:
        # Read CSV file
        contents = await file.read()
        decoded = contents.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(decoded))

        # Validate CSV headers
        required_fields = ["name"]
        optional_fields = ["breed", "age", "medical_history", "weight_kg", "sex"]

        headers = csv_reader.fieldnames
        if not headers or "name" not in headers:
            raise HTTPException(status_code=400, detail="CSV must contain 'name' column")

        # Parse rows
        dogs_data = []
        for row in csv_reader:
            dog_dict = {
                "name": row.get("name", "").strip(),
                "breed": row.get("breed", "").strip() or None,
                "age": int(row.get("age", 0)) if row.get("age", "").strip() else None,
                "medical_history": row.get("medical_history", "").strip() or None,
                "weight_kg": (
                    float(row.get("weight_kg", 0)) if row.get("weight_kg", "").strip() else None
                ),
                "sex": row.get("sex", "").strip() or None,
            }

            if dog_dict["name"]:  # Only add if name is not empty
                dogs_data.append(dog_dict)

        if not dogs_data:
            raise HTTPException(status_code=400, detail="No valid dog data found in CSV")

        logger.info(f"Parsed {len(dogs_data)} dogs from CSV")

        # Batch extract medical data
        extracted_dogs = await medical_extraction_service.batch_extract(dogs_data)

        # Insert into Elasticsearch
        dog_ids = []
        errors = []
        successful = 0

        for i, dog_data in enumerate(extracted_dogs):
            try:
                dog_id = str(uuid.uuid4())

                # Create AsyncDocument instance
                doc = Dog(meta={"id": dog_id})

                # Set basic fields
                doc.name = dog_data["name"]
                doc.breed = dog_data.get("breed")
                doc.age = dog_data.get("age")
                doc.weight_kg = dog_data.get("weight_kg")
                doc.sex = dog_data.get("sex")
                doc.rescue_date = datetime.now()
                doc.adoption_status = "available"

                # Set medical fields
                doc.medical_history = dog_data.get("medical_history")
                doc.medical_events = dog_data.get("medical_events", [])
                doc.past_conditions = dog_data.get("past_conditions", [])
                doc.active_treatments = dog_data.get("active_treatments", [])
                doc.severity_score = dog_data.get("severity_score", 0)
                doc.adoption_readiness = dog_data.get("adoption_readiness", "ready")

                # Initialize arrays
                doc.photos = []
                doc.medical_document_ids = []

                # Save to Elasticsearch
                await doc.save(using=es_client.client)

                dog_ids.append(dog_id)
                successful += 1

                logger.info(
                    f"Bulk upload: Created dog {i+1}/{len(extracted_dogs)}: {doc.name} ({dog_id})"
                )

            except Exception as e:
                logger.error(f"Failed to create dog {dog_data.get('name', 'Unknown')}: {e}")
                errors.append(
                    {
                        "row": i + 2,  # +2 for CSV line number (header + 0-index)
                        "name": dog_data.get("name", "Unknown"),
                        "error": str(e),
                    }
                )

        logger.info(f"Bulk upload complete: {successful}/{len(dogs_data)} successful")

        return BulkUploadResponse(
            total_processed=len(dogs_data),
            successful=successful,
            failed=len(errors),
            dog_ids=dog_ids,
            errors=errors,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk upload failed: {str(e)}")
