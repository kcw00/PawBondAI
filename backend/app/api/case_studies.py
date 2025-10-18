from fastapi import APIRouter, HTTPException, Path, Query, Body
from typing import List
from datetime import datetime
import uuid

from app.models.schemas import CaseStudyResponse, CaseStudyCreate, SearchRequest
from app.models.es_documents import CaseStudy
from app.services.elasticsearch_client import es_client
from app.services.elasticsearch_service import es_service
from app.core.config import get_settings
from app.core.logger import setup_logger
from elasticsearch.dsl import AsyncSearch

settings = get_settings()
router = APIRouter()
logger = setup_logger(__name__)


# 1. Create a case study
# ~~~~worked! testing done by with postman.
@router.post("", response_model=CaseStudyResponse)
async def create_case_study(case: CaseStudyCreate = Body(...)):
    """Create a new case study using AsyncDocument"""
    case_id = str(uuid.uuid4())

    try:
        # Create AsyncDocument instance
        doc = CaseStudy(meta={'id': case_id})

        # Map all fields from Pydantic to AsyncDocument
        doc.title = case.title
        doc.diagnosis = case.diagnosis
        doc.treatment_plan = case.treatment_plan
        doc.outcome = case.outcome
        doc.presenting_complaint = case.presenting_complaint
        doc.clinical_history = case.clinical_history
        doc.physical_examination = case.physical_examination
        doc.diagnostic_tests = case.diagnostic_tests
        doc.follow_up = case.follow_up
        doc.learning_points = case.learning_points

        # Patient info
        doc.patient_species = case.patient_species
        doc.patient_breed = case.patient_breed
        doc.patient_age_years = case.patient_age_years
        doc.patient_age_months = case.patient_age_months
        doc.patient_age_category = case.patient_age_category
        doc.patient_sex = case.patient_sex
        doc.patient_weight_kg = case.patient_weight_kg
        doc.patient_weight_category = case.patient_weight_category
        doc.is_juvenile = case.is_juvenile
        doc.is_geriatric = case.is_geriatric

        # Organization & Location
        doc.rescue_organization = case.rescue_organization
        doc.organization_contact = case.organization_contact
        doc.country = case.country
        doc.region = case.region

        # Cost & Classification
        doc.estimated_cost = case.estimated_cost
        doc.cost_breakdown = case.cost_breakdown
        doc.disease_category = case.disease_category
        doc.urgency_level = case.urgency_level

        # Metadata
        doc.tags = case.tags
        doc.references = case.references
        doc.visibility = case.visibility
        doc.is_shareable = case.is_shareable
        if case.date_published:
            doc.date_published = datetime.fromisoformat(case.date_published)

        # Save using AsyncDocument (auto-sets created_at/updated_at)
        await doc.save(using=es_client.client)

        logger.info(f"Case study created and indexed with ID: {case_id}")

        # Build response from saved document
        return CaseStudyResponse(
            id=case_id,
            created_at=doc.created_at.isoformat() if doc.created_at else datetime.now().isoformat(),
            updated_at=doc.updated_at.isoformat() if doc.updated_at else datetime.now().isoformat(),
            **case.model_dump()
        )
    except Exception as e:
        logger.error(f"Error creating case study: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating case study: {str(e)}")


# 2. Get a case study by ID
# ~~~~worked! testing done by with postman.
@router.get("/{case_id}", response_model=CaseStudyResponse)
async def get_case_study(case_id: str):
    """Get a specific case study by ID using AsyncDocument.get()"""
    try:
        # Use AsyncDocument.get() - cleaner and more direct
        doc = await CaseStudy.get(id=case_id, using=es_client.client)

        # Convert to response model
        return CaseStudyResponse(
            id=case_id,
            title=doc.title,
            diagnosis=doc.diagnosis,
            treatment_plan=doc.treatment_plan,
            outcome=doc.outcome,
            presenting_complaint=doc.presenting_complaint,
            clinical_history=doc.clinical_history,
            physical_examination=doc.physical_examination,
            diagnostic_tests=doc.diagnostic_tests,
            follow_up=doc.follow_up,
            learning_points=doc.learning_points,
            patient_species=doc.patient_species,
            patient_breed=doc.patient_breed,
            patient_age_years=doc.patient_age_years,
            patient_age_months=doc.patient_age_months,
            patient_age_category=doc.patient_age_category,
            patient_sex=doc.patient_sex,
            patient_weight_kg=doc.patient_weight_kg,
            patient_weight_category=doc.patient_weight_category,
            is_juvenile=doc.is_juvenile,
            is_geriatric=doc.is_geriatric,
            rescue_organization=doc.rescue_organization,
            organization_contact=doc.organization_contact,
            country=doc.country,
            region=doc.region,
            estimated_cost=doc.estimated_cost,
            cost_breakdown=doc.cost_breakdown,
            disease_category=doc.disease_category,
            urgency_level=doc.urgency_level,
            tags=doc.tags or [],
            references=doc.references,
            visibility=doc.visibility,
            is_shareable=doc.is_shareable,
            date_published=doc.date_published.isoformat() if doc.date_published else None,
            created_at=doc.created_at.isoformat() if doc.created_at else None,
            updated_at=doc.updated_at.isoformat() if doc.updated_at else None,
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Case study not found: {str(e)}")


# 3. List all case studies
# ~~~~worked! testing done by with postman.
@router.get("", response_model=List[CaseStudyResponse])
async def list_case_studies(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    urgency_level: str = Query(None, description="Filter by urgency level"),
    country: str = Query(None, description="Filter by country"),
):
    """List case studies with filters and pagination using AsyncSearch"""
    try:
        # Build AsyncSearch query
        s = AsyncSearch(using=es_client.client, index=settings.case_studies_index)
        s = s.query("match_all")

        # Add filters if provided
        if urgency_level:
            s = s.filter("term", urgency_level=urgency_level)
        if country:
            s = s.filter("term", country=country)

        # Sort by created_at descending
        s = s.sort("-created_at")

        # Pagination
        s = s[offset:offset + limit]

        response = await s.execute()

        cases = []
        for hit in response:
            case_data = hit.to_dict()
            # Add id from meta if not in the document
            if "id" not in case_data:
                case_data["id"] = hit.meta.id
            cases.append(CaseStudyResponse(**case_data))

        return cases
    except Exception as e:
        logger.error(f"Error listing case studies: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing case studies: {str(e)}")


# 4. Update a case study
@router.put("/{case_id}", response_model=CaseStudyResponse)
async def update_case_study(
    case_id: str,
    case: CaseStudyCreate = Body(...),
):
    """Update a case study using AsyncDocument.update()"""
    try:
        # Get the existing document
        doc = await CaseStudy.get(id=case_id, using=es_client.client)

        # Update all fields
        doc.title = case.title
        doc.diagnosis = case.diagnosis
        doc.treatment_plan = case.treatment_plan
        doc.outcome = case.outcome
        doc.presenting_complaint = case.presenting_complaint
        doc.clinical_history = case.clinical_history
        doc.physical_examination = case.physical_examination
        doc.diagnostic_tests = case.diagnostic_tests
        doc.follow_up = case.follow_up
        doc.learning_points = case.learning_points
        doc.patient_species = case.patient_species
        doc.patient_breed = case.patient_breed
        doc.patient_age_years = case.patient_age_years
        doc.patient_age_months = case.patient_age_months
        doc.patient_age_category = case.patient_age_category
        doc.patient_sex = case.patient_sex
        doc.patient_weight_kg = case.patient_weight_kg
        doc.patient_weight_category = case.patient_weight_category
        doc.is_juvenile = case.is_juvenile
        doc.is_geriatric = case.is_geriatric
        doc.rescue_organization = case.rescue_organization
        doc.organization_contact = case.organization_contact
        doc.country = case.country
        doc.region = case.region
        doc.estimated_cost = case.estimated_cost
        doc.cost_breakdown = case.cost_breakdown
        doc.disease_category = case.disease_category
        doc.urgency_level = case.urgency_level
        doc.tags = case.tags
        doc.references = case.references
        doc.visibility = case.visibility
        doc.is_shareable = case.is_shareable
        if case.date_published:
            doc.date_published = datetime.fromisoformat(case.date_published)

        # Save updates (auto-updates updated_at timestamp)
        await doc.save(using=es_client.client)

        logger.info(f"Case study {case_id} updated successfully")

        return CaseStudyResponse(
            id=case_id,
            created_at=doc.created_at.isoformat() if doc.created_at else None,
            updated_at=doc.updated_at.isoformat() if doc.updated_at else None,
            **case.model_dump()
        )
    except Exception as e:
        logger.error(f"Error updating case study: {e}")
        raise HTTPException(status_code=404, detail=f"Case study not found: {str(e)}")


# 5. Delete a case study
@router.delete("/{case_id}")
async def delete_case_study(case_id: str):
    """Delete a case study using AsyncDocument.delete()"""
    try:
        # Get and delete the document
        doc = await CaseStudy.get(id=case_id, using=es_client.client)
        await doc.delete(using=es_client.client)

        logger.info(f"Case study {case_id} deleted successfully")
        return {"message": "Case study deleted successfully", "case_id": case_id}
    except Exception as e:
        logger.error(f"Error deleting case study: {e}")
        raise HTTPException(status_code=404, detail=f"Case study not found: {str(e)}")


# 6. Search case studies
# testing needed
@router.get("/search")
async def search_similar_cases(
    symptoms: List[str] = Query(..., description="List of symptoms"),
    species: str = Query("dog", description="Animal species"),
    size: int = Query(5, ge=1, le=20),
):
    """Search for similar cases using vector search"""
    cases = await es_service.vector_search_cases(symptoms, size)

    # Filter by species
    cases = [c for c in cases if c.get("species", "dog") == species]

    return {
        "query_symptoms": symptoms,
        "species": species,
        "cases_found": len(cases),
        "cases": cases,
    }
