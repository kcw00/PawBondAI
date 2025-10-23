from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from typing import List, Optional
from datetime import datetime
import uuid
import io
import PyPDF2

from app.models.es_documents import MedicalDocument, Dog
from app.services.elasticsearch_client import es_client
from app.core.config import get_settings
from app.core.logger import setup_logger
from elasticsearch.dsl import AsyncSearch, Q

settings = get_settings()
router = APIRouter()
logger = setup_logger(__name__)


# 1. Create a medical document
@router.post("/upload")
async def upload_medical_document(
    file: UploadFile = File(...),
    dog_id: Optional[str] = Form(None),
    dog_name: Optional[str] = Form(None),
    document_type: str = Form("other"),
    title: Optional[str] = Form(None),
    document_date: Optional[str] = Form(None),
    severity: str = Form("routine"),
    category: str = Form("diagnostic"),
    veterinarian_name: Optional[str] = Form(None),
    clinic_name: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    """Upload a medical document (PDF, image, etc.)"""
    document_id = str(uuid.uuid4())

    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Extract text from PDF if applicable
        extracted_text = ""
        if file.filename.lower().endswith('.pdf'):
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                for page in pdf_reader.pages:
                    extracted_text += page.extract_text() + "\n"
            except Exception as e:
                logger.warning(f"Could not extract text from PDF: {e}")
                extracted_text = "PDF text extraction failed"
        else:
            # For images or other formats, we could use OCR here
            extracted_text = f"Binary file: {file.filename}"

        # Create document instance
        doc = MedicalDocument(meta={"id": document_id})
        
        doc.title = title or file.filename
        doc.document_type = document_type
        doc.content = extracted_text
        doc.dog_id = dog_id
        doc.dog_name = dog_name
        doc.filename = file.filename
        doc.file_type = file.filename.split('.')[-1].lower() if '.' in file.filename else 'unknown'
        doc.file_size = file_size
        doc.severity = severity
        doc.category = category
        doc.veterinarian_name = veterinarian_name
        doc.clinic_name = clinic_name
        doc.notes = notes
        
        # Parse document date
        if document_date:
            try:
                doc.document_date = datetime.fromisoformat(document_date.replace('Z', '+00:00'))
            except:
                doc.document_date = datetime.now()
        else:
            doc.document_date = datetime.now()

        # Save to Elasticsearch
        await doc.save(using=es_client.client)

        logger.info(f"Medical document uploaded with ID: {document_id}")

        return {
            "id": document_id,
            "filename": file.filename,
            "file_size": file_size,
            "extracted_text_length": len(extracted_text),
            "message": "Medical document uploaded successfully"
        }
    except Exception as e:
        logger.error(f"Error uploading medical document: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


# 2. Get medical document by ID
@router.get("/{document_id}")
async def get_medical_document(document_id: str):
    """Get a medical document by ID"""
    try:
        doc = await MedicalDocument.get(id=document_id, using=es_client.client)
        
        return {
            "id": document_id,
            "title": doc.title,
            "document_type": doc.document_type,
            "content": doc.content,
            "dog_id": doc.dog_id,
            "dog_name": doc.dog_name,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "document_date": doc.document_date.isoformat() if doc.document_date else None,
            "upload_date": doc.upload_date.isoformat() if doc.upload_date else None,
            "severity": doc.severity,
            "category": doc.category,
            "veterinarian_name": doc.veterinarian_name,
            "clinic_name": doc.clinic_name,
            "notes": doc.notes,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Medical document not found: {str(e)}")


# 3. List medical documents with filters
@router.get("")
async def list_medical_documents(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    dog_id: Optional[str] = Query(None),
    document_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
):
    """List medical documents with optional filters"""
    try:
        # Build search query
        search = AsyncSearch(using=es_client.client, index=settings.medical_documents_index)
        
        # Apply filters
        if dog_id:
            search = search.filter("term", dog_id=dog_id)
        if document_type:
            search = search.filter("term", document_type=document_type)
        if severity:
            search = search.filter("term", severity=severity)
        
        # Sort by upload timestamp descending (matches existing schema)
        search = search.sort("-upload_timestamp")
        
        # Pagination
        search = search[offset:offset + limit]
        
        response = await search.execute()
        
        documents = []
        dog_ids_to_lookup = set()
        
        # First pass: collect all unique dog_ids
        for hit in response.hits:
            dog_id = hit.dog_id if hasattr(hit, 'dog_id') else None
            if dog_id:
                dog_ids_to_lookup.add(dog_id)
        
        # Lookup dog names from dogs index
        dog_names = {}
        if dog_ids_to_lookup:
            try:
                logger.info(f"Looking up dog IDs: {dog_ids_to_lookup}")
                dog_search = AsyncSearch(using=es_client.client, index=settings.dogs_index)
                dog_search = dog_search.filter("terms", _id=list(dog_ids_to_lookup))
                dog_search = dog_search[:len(dog_ids_to_lookup)]
                dog_response = await dog_search.execute()
                
                for dog_hit in dog_response.hits:
                    dog_names[dog_hit.meta.id] = dog_hit.name if hasattr(dog_hit, 'name') else None
                    logger.info(f"Found dog: {dog_hit.meta.id} -> {dog_hit.name if hasattr(dog_hit, 'name') else 'NO NAME'}")
                
                logger.info(f"Looked up {len(dog_names)} dog names out of {len(dog_ids_to_lookup)} requested")
                
                # Log which dog IDs were not found
                missing_ids = dog_ids_to_lookup - set(dog_names.keys())
                if missing_ids:
                    logger.warning(f"Dog IDs not found in dogs index: {missing_ids}")
            except Exception as e:
                logger.warning(f"Could not lookup dog names: {e}")
        
        # Second pass: build documents with enriched dog names
        for hit in response.hits:
            dog_id = hit.dog_id if hasattr(hit, 'dog_id') else None
            documents.append({
                "id": hit.meta.id,
                "document_id": hit.document_id if hasattr(hit, 'document_id') else hit.meta.id,
                "title": hit.source_filename if hasattr(hit, 'source_filename') else "Unknown",
                "document_type": hit.document_type if hasattr(hit, 'document_type') else "other",
                "dog_id": dog_id,
                "dog_name": dog_names.get(dog_id) if dog_id else None,  # Enriched from dogs index
                "content": hit.document_text if hasattr(hit, 'document_text') else None,
                "filename": hit.source_filename if hasattr(hit, 'source_filename') else None,
                "file_type": hit.file_type if hasattr(hit, 'file_type') else None,
                "file_size": hit.file_size if hasattr(hit, 'file_size') else None,
                "document_date": hit.visit_date if hasattr(hit, 'visit_date') else None,
                "upload_date": hit.upload_timestamp if hasattr(hit, 'upload_timestamp') else None,
                "severity": hit.severity if hasattr(hit, 'severity') else None,
                "category": hit.category if hasattr(hit, 'category') else None,
                "veterinarian_name": hit.veterinarian_name if hasattr(hit, 'veterinarian_name') else None,
                "clinic_name": hit.vet_clinic_name if hasattr(hit, 'vet_clinic_name') else None,
                "medications": hit.medications if hasattr(hit, 'medications') else [],
                "procedures": hit.procedures if hasattr(hit, 'procedures') else [],
                "vaccinations": hit.vaccinations if hasattr(hit, 'vaccinations') else [],
                "notes": hit.notes if hasattr(hit, 'notes') else None,
            })
        
        return documents
    except Exception as e:
        logger.error(f"Error listing medical documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


# 4. Delete medical document
@router.delete("/{document_id}")
async def delete_medical_document(document_id: str):
    """Delete a medical document by ID"""
    try:
        doc = await MedicalDocument.get(id=document_id, using=es_client.client)
        await doc.delete(using=es_client.client)
        
        logger.info(f"Medical document deleted: {document_id}")
        return {"message": "Medical document deleted successfully", "id": document_id}
    except Exception as e:
        logger.error(f"Error deleting medical document: {e}")
        raise HTTPException(status_code=404, detail=f"Error deleting document: {str(e)}")


# 5. Search medical documents by content
@router.get("/search/content")
async def search_medical_documents(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
):
    """Search medical documents by content"""
    try:
        search = AsyncSearch(using=es_client.client, index=settings.medical_documents_index)
        
        # Multi-field search
        search = search.query(
            "multi_match",
            query=query,
            fields=["content", "title", "diagnosis", "treatment", "dog_name"],
            type="best_fields"
        )
        
        search = search[:limit]
        response = await search.execute()
        
        documents = []
        for hit in response.hits:
            documents.append({
                "id": hit.meta.id,
                "title": hit.title,
                "dog_name": hit.dog_name if hasattr(hit, 'dog_name') else None,
                "document_type": hit.document_type,
                "severity": hit.severity if hasattr(hit, 'severity') else None,
                "score": hit.meta.score,
            })
        
        return {
            "query": query,
            "total": response.hits.total.value,
            "documents": documents
        }
    except Exception as e:
        logger.error(f"Error searching medical documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")
