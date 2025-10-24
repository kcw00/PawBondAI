from fastapi import APIRouter, HTTPException, Path, Query, Body, UploadFile, File
from typing import List, Optional
from datetime import datetime
import uuid
import csv
import io

from app.models.schemas import ApplicationCreate, ApplicationResponse
from app.models.es_documents import Application
from app.services.elasticsearch_client import es_client
from app.services.language_service import detect_language
from app.core.config import get_settings
from app.core.logger import setup_logger
from elasticsearch.dsl import AsyncSearch, Q

settings = get_settings()
router = APIRouter()
logger = setup_logger(__name__)


# 1. Create an application
# ~~~~worked! testing done by with postman.
@router.post("", response_model=ApplicationResponse)
async def create_application(application: ApplicationCreate = Body(...)):
    """Create a new foster/adoption application - FLAT structure"""
    application_id = str(uuid.uuid4())

    try:
        # Create AsyncDocument instance
        doc = Application(meta={"id": application_id})

        # Map flat structure
        doc.applicant_name = application.applicant_name
        doc.phone = application.phone
        doc.email = application.email
        doc.gender = application.gender
        doc.address = application.address

        doc.housing_type = application.housing_type
        doc.has_yard = application.has_yard
        doc.yard_size_sqm = application.yard_size_sqm

        doc.family_members = application.family_members
        doc.all_family_members_agree = application.all_family_members_agree

        doc.experience_level = application.experience_level
        doc.has_other_pets = application.has_other_pets
        doc.other_pets_description = application.other_pets_description

        doc.motivation = application.motivation

        doc.animal_applied_for = application.animal_applied_for
        doc.status = application.status
        doc.submitted_at = application.submitted_at or datetime.now()

        # Save using AsyncDocument
        await doc.save(using=es_client.client)

        logger.info(f"Application created with ID: {application_id}")

        return ApplicationResponse(id=application_id, **application.model_dump())
    except Exception as e:
        logger.error(f"Error creating application: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating application: {str(e)}")


# 2. Get an application by ID
# ~~~~worked! testing done by with postman.
@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(application_id: str):
    """Get an application by ID"""
    try:
        doc = await Application.get(id=application_id, using=es_client.client)

        return ApplicationResponse(
            id=application_id,
            applicant_name=doc.applicant_name,
            phone=doc.phone,
            email=doc.email,
            gender=doc.gender if hasattr(doc, "gender") else None,
            address=doc.address if hasattr(doc, "address") else None,
            housing_type=doc.housing_type,
            has_yard=doc.has_yard,
            yard_size_sqm=doc.yard_size_sqm if hasattr(doc, "yard_size_sqm") else None,
            family_members=doc.family_members if hasattr(doc, "family_members") else None,
            all_family_members_agree=doc.all_family_members_agree,
            experience_level=doc.experience_level,
            has_other_pets=doc.has_other_pets,
            other_pets_description=(
                doc.other_pets_description if hasattr(doc, "other_pets_description") else None
            ),
            motivation=doc.motivation,
            animal_applied_for=(
                doc.animal_applied_for if hasattr(doc, "animal_applied_for") else None
            ),
            status=doc.status,
            submitted_at=doc.submitted_at if hasattr(doc, "submitted_at") else None,
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Application not found: {str(e)}")


# 3. List all applications with filters
# ~~~~worked! testing done by with postman.
@router.get("", response_model=List[ApplicationResponse])
async def list_applications(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, description="Filter by application status"),
    experience_level: Optional[str] = Query(None, description="Filter by experience level"),
):
    """List applications with filters and pagination"""
    try:
        s = AsyncSearch(using=es_client.client, index=settings.applications_index)
        s = s.query("match_all")

        # Add filters
        if status:
            s = s.filter("term", status=status)
        if experience_level:
            s = s.filter("term", experience_level=experience_level)

        # Sort and paginate
        s = s.sort("-submitted_at")
        s = s[offset : offset + limit]

        response = await s.execute()

        applications = []
        for hit in response:
            applications.append(
                ApplicationResponse(
                    id=hit.meta.id,
                    applicant_name=hit.applicant_name,
                    phone=hit.phone,
                    email=hit.email,
                    gender=hit.gender if hasattr(hit, "gender") else None,
                    address=hit.address if hasattr(hit, "address") else None,
                    housing_type=hit.housing_type,
                    has_yard=hit.has_yard,
                    yard_size_sqm=hit.yard_size_sqm if hasattr(hit, "yard_size_sqm") else None,
                    family_members=hit.family_members if hasattr(hit, "family_members") else None,
                    all_family_members_agree=hit.all_family_members_agree,
                    experience_level=hit.experience_level,
                    has_other_pets=hit.has_other_pets,
                    other_pets_description=(
                        hit.other_pets_description
                        if hasattr(hit, "other_pets_description")
                        else None
                    ),
                    motivation=hit.motivation,
                    animal_applied_for=(
                        hit.animal_applied_for if hasattr(hit, "animal_applied_for") else None
                    ),
                    status=hit.status,
                    submitted_at=hit.submitted_at if hasattr(hit, "submitted_at") else None,
                )
            )

        return applications
    except Exception as e:
        logger.error(f"Error listing applications: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing applications: {str(e)}")


# 4. Update an application
# ~~~~worked! testing done by with postman.
@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: str,
    application: ApplicationCreate = Body(...),
):
    """Update an application"""
    try:
        doc = await Application.get(id=application_id, using=es_client.client)

        # Update flat structure fields
        doc.applicant_name = application.applicant_name
        doc.phone = application.phone
        doc.email = application.email
        doc.gender = application.gender
        doc.address = application.address
        doc.housing_type = application.housing_type
        doc.has_yard = application.has_yard
        doc.yard_size_sqm = application.yard_size_sqm
        doc.family_members = application.family_members
        doc.all_family_members_agree = application.all_family_members_agree
        doc.experience_level = application.experience_level
        doc.has_other_pets = application.has_other_pets
        doc.other_pets_description = application.other_pets_description
        doc.motivation = application.motivation
        doc.animal_applied_for = application.animal_applied_for
        doc.status = application.status

        await doc.save(using=es_client.client)

        logger.info(f"Application {application_id} updated successfully")

        return ApplicationResponse(id=application_id, **application.model_dump())
    except Exception as e:
        logger.error(f"Error updating application: {e}")
        raise HTTPException(status_code=404, detail=f"Application not found: {str(e)}")


# 5. Delete an application
# ~~~~worked! testing done by with postman.
@router.delete("/{application_id}")
async def delete_application(application_id: str):
    """Delete an application"""
    try:
        doc = await Application.get(id=application_id, using=es_client.client)
        await doc.delete(using=es_client.client)

        logger.info(f"Application {application_id} deleted successfully")
        return {"message": "Application deleted successfully", "application_id": application_id}
    except Exception as e:
        logger.error(f"Error deleting application: {e}")
        raise HTTPException(status_code=404, detail=f"Application not found: {str(e)}")


# ==================== CSV BULK UPLOAD ENDPOINTS ====================


# STEP 2: Validate CSV file
@router.post("/csv/validate")
async def validate_csv(file: UploadFile = File(...)):
    """
    Step 2: VALIDATION (automatic)
    - Check file format
    - Validate columns
    - Count rows
    Returns validation results without indexing
    """
    try:
        # Check file extension
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="File must be a CSV file")

        # Read CSV content
        content = await file.read()
        csv_string = content.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(csv_string))

        # Required columns for application data (flat structure)
        required_columns = ["applicant_name", "email", "phone", "housing_type", "motivation"]

        # Get actual columns from CSV
        fieldnames = csv_reader.fieldnames
        if not fieldnames:
            raise HTTPException(status_code=400, detail="CSV file is empty or has no headers")

        # Check for required columns
        missing_columns = [col for col in required_columns if col not in fieldnames]
        extra_columns = [col for col in fieldnames if col not in required_columns and col]

        # Count rows
        rows = list(csv_reader)
        row_count = len(rows)

        # Validation results
        validation_result = {
            "valid": len(missing_columns) == 0,
            "filename": file.filename,
            "row_count": row_count,
            "column_count": len(fieldnames),
            "columns_found": fieldnames,
            "required_columns": required_columns,
            "missing_columns": missing_columns,
            "extra_columns": extra_columns,
            "errors": [],
            "warnings": [],
        }

        # Add errors if validation failed
        if missing_columns:
            validation_result["errors"].append(
                f"Missing required columns: {', '.join(missing_columns)}"
            )

        # Add warnings for extra columns
        if extra_columns:
            validation_result["warnings"].append(
                f"Extra columns found (will be ignored): {', '.join(extra_columns)}"
            )

        if row_count == 0:
            validation_result["errors"].append("CSV file contains no data rows")
            validation_result["valid"] = False

        logger.info(
            f"Validated CSV: {file.filename} - Valid: {validation_result['valid']}, Rows: {row_count}"
        )

        return validation_result

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400, detail="File encoding error. Please ensure the file is UTF-8 encoded"
        )
    except csv.Error as e:
        raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(e)}")
    except Exception as e:
        logger.error(f"Error validating CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Error validating CSV: {str(e)}")


# STEP 3: Preview CSV data
@router.post("/csv/preview")
async def preview_csv(file: UploadFile = File(...)):
    """
    Step 3: PREVIEW MODAL (requires user confirmation)
    - Show first 5 rows
    - Display validation results
    User will click "Upload & Index" button to proceed to Step 4
    """
    try:
        # Read CSV content
        content = await file.read()
        csv_string = content.decode("utf-8")

        # Validate
        csv_reader = csv.DictReader(io.StringIO(csv_string))
        fieldnames = csv_reader.fieldnames

        required_columns = ["applicant_name", "email", "phone", "housing_type", "motivation"]

        missing_columns = [col for col in required_columns if col not in fieldnames]
        rows = list(csv_reader)

        validation_result = {
            "valid": len(missing_columns) == 0 and len(rows) > 0,
            "filename": file.filename,
            "row_count": len(rows),
            "missing_columns": missing_columns,
        }

        # Get first 5 rows for preview
        preview_rows = rows[:5]

        return {
            "validation": validation_result,
            "preview_rows": preview_rows,
            "total_rows": len(rows),
            "message": "Review the data below. Click 'Upload & Index' to proceed with indexing.",
        }

    except Exception as e:
        logger.error(f"Error previewing CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Error previewing CSV: {str(e)}")


# STEP 4: Upload and Index CSV (requires confirmation)
@router.post("/csv/upload")
async def upload_and_index_csv(file: UploadFile = File(...)):
    """
    Step 4: INDEXING (automatic after user confirmation)
    - Parse CSV data
    - Generate embeddings (via ES inference endpoint)
    - Index to Elasticsearch
    Returns summary of indexed applications
    """
    try:
        # Read and parse CSV
        content = await file.read()
        csv_string = content.decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(csv_string))
        rows = list(csv_reader)

        indexed_count = 0
        failed_count = 0
        errors = []
        indexed_ids = []

        for idx, row in enumerate(rows):
            try:
                application_id = str(uuid.uuid4())

                # Create AsyncDocument instance with flat structure
                doc = Application(meta={"id": application_id})

                # Map CSV columns to flat structure
                doc.applicant_name = row.get("applicant_name", "")
                doc.phone = row.get("phone", "")
                doc.email = row.get("email", "")
                doc.gender = row.get("gender", None)
                doc.address = row.get("address", None)

                doc.housing_type = row.get("housing_type", "Unknown")
                doc.has_yard = row.get("has_yard", "").lower() in ["true", "yes", "1"]
                doc.yard_size_sqm = (
                    int(row.get("yard_size_sqm", 0)) if row.get("yard_size_sqm") else None
                )

                doc.family_members = row.get("family_members", None)
                doc.all_family_members_agree = row.get("all_family_members_agree", "").lower() in [
                    "true",
                    "yes",
                    "1",
                    "",
                ]

                doc.experience_level = row.get("experience_level", "Intermediate")
                doc.has_other_pets = row.get("has_other_pets", "").lower() in ["true", "yes", "1"]
                doc.other_pets_description = row.get("other_pets_description", None)

                doc.motivation = row.get("motivation", "")

                doc.animal_applied_for = row.get("animal_applied_for", None)
                doc.status = row.get("status", "Pending")
                doc.submitted_at = datetime.now()
                
                # Detect language from motivation text
                doc.language = await detect_language(doc.motivation)

                # Save to Elasticsearch
                await doc.save(using=es_client.client)

                indexed_count += 1
                indexed_ids.append(application_id)
                logger.info(f"Indexed application {application_id} from CSV row {idx + 1}")

            except Exception as e:
                failed_count += 1
                error_msg = f"Row {idx + 1}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Error indexing row {idx + 1}: {e}")

        # Return summary
        return {
            "success": True,
            "filename": file.filename,
            "total_rows": len(rows),
            "indexed_count": indexed_count,
            "failed_count": failed_count,
            "indexed_ids": indexed_ids[:10],  # Return first 10 IDs
            "errors": errors[:5],  # Return first 5 errors
            "message": f"Successfully indexed {indexed_count} out of {len(rows)} applications",
        }

    except Exception as e:
        logger.error(f"Error uploading CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading CSV: {str(e)}")


# Semantic Search Endpoint
# ~~~~worked! testing done by with postman.
@router.post("/search", response_model=List[ApplicationResponse])
async def search_applications_semantic(
    query: str = Body(..., embed=True),
    limit: int = Body(10, embed=True, ge=1, le=100),
    status_filter: Optional[str] = Body(None, embed=True),
):
    """
    Semantic search for applications using ES inference endpoint.
    Searches the motivation field using embeddings to find similar applicants.

    Args:
        query: Natural language search query (e.g., "experienced with anxious dogs")
        limit: Number of results to return
        status_filter: Optional filter by application status (Pending, Approved, Rejected)
    """
    try:
        # Build semantic search using AsyncSearch
        s = AsyncSearch(using=es_client.client, index="applications")
        s = s.query("semantic", field="motivation", query=query)

        # Add status filter if provided
        if status_filter:
            s = s.filter("term", status=status_filter)

        s = s[0:limit]

        response = await s.execute()

        applications = []
        for hit in response:
            applications.append(
                ApplicationResponse(
                    id=hit.meta.id,
                    applicant_name=hit.applicant_name,
                    phone=hit.phone,
                    email=hit.email,
                    gender=hit.gender if hasattr(hit, "gender") else None,
                    address=hit.address if hasattr(hit, "address") else None,
                    housing_type=hit.housing_type,
                    has_yard=hit.has_yard,
                    yard_size_sqm=hit.yard_size_sqm if hasattr(hit, "yard_size_sqm") else None,
                    family_members=hit.family_members if hasattr(hit, "family_members") else None,
                    all_family_members_agree=hit.all_family_members_agree,
                    experience_level=hit.experience_level,
                    has_other_pets=hit.has_other_pets,
                    other_pets_description=(
                        hit.other_pets_description
                        if hasattr(hit, "other_pets_description")
                        else None
                    ),
                    motivation=hit.motivation,
                    animal_applied_for=(
                        hit.animal_applied_for if hasattr(hit, "animal_applied_for") else None
                    ),
                    status=hit.status,
                    submitted_at=hit.submitted_at if hasattr(hit, "submitted_at") else None,
                )
            )

        logger.info(f"Semantic search for '{query}' returned {len(applications)} applications")
        return applications

    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")
