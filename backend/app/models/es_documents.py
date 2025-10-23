from datetime import datetime
from typing import List, Optional
from elasticsearch.dsl import (
    AsyncDocument,
    Text,
    Keyword,
    Date,
    Float,
    Integer,
    Boolean,
    Nested,
    InnerDoc,
    Object,
    GeoPoint,
)
from app.core.config import get_settings

settings = get_settings()


class KnowledgeArticle(AsyncDocument):
    """Elasticsearch Document model for veterinary knowledge articles"""

    # Use dot notation for nested fields
    title = Text(fields={"raw": Keyword()})
    content_chunk = Text(analyzer="standard")
    # Note: content_embedding removed - ES handles embeddings via semantic_text in index mapping

    source = Keyword()
    filename = Keyword()
    upload_date = Date()
    updated_at = Date()

    tags = Keyword(multi=True)
    language = Keyword()

    class Index:
        name = settings.vet_knowledge_index
        # No settings for serverless - managed by Elasticsearch

    def save(self, **kwargs):
        """Override save to set upload_date"""
        if not self.upload_date:
            self.upload_date = datetime.now()
        return super().save(**kwargs)


class CaseStudy(AsyncDocument):
    """Elasticsearch Document model for case studies"""

    # Basic case info
    title = Text(fields={"raw": Keyword()})
    diagnosis = Text()
    treatment_plan = Text()
    outcome = Text()

    presenting_complaint = Text()
    clinical_history = Text()
    physical_examination = Text()
    diagnostic_tests = Text()
    follow_up = Text()
    learning_points = Text()

    # Note: symptoms_embedding removed - ES handles embeddings via semantic_text in index mapping

    # Patient information
    patient_species = Keyword()
    patient_breed = Keyword()
    patient_age_years = Integer()
    patient_age_months = Integer()
    patient_age_category = Keyword()
    patient_sex = Keyword()
    patient_weight_kg = Float()
    patient_weight_category = Keyword()
    is_juvenile = Boolean()
    is_geriatric = Boolean()

    # Organization & Location
    rescue_organization = Keyword()
    organization_contact = Keyword()
    country = Keyword()
    region = Keyword()

    # Cost & Classification
    estimated_cost = Float()
    cost_breakdown = Text()
    disease_category = Keyword()
    urgency_level = Keyword()

    # Metadata
    tags = Keyword(multi=True)
    references = Text()
    visibility = Keyword()
    is_shareable = Boolean()
    date_published = Date()
    language = Keyword()  # Detected language code (e.g., 'en', 'ko', 'es')

    created_at = Date()
    updated_at = Date()

    class Index:
        name = settings.case_studies_index
        # No settings for serverless - managed by Elasticsearch

    def save(self, **kwargs):
        """Override save to set timestamps"""
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
        return super().save(**kwargs)


class Dog(AsyncDocument):
    """Elasticsearch Document model for dog profiles"""

    # Basic info
    name = Text(fields={"raw": Keyword()})
    breed = Keyword()
    age = Integer()
    weight_kg = Float()
    sex = Keyword()

    # Adoption info
    rescue_date = Date()
    adoption_status = Keyword()
    rescue_organization = Keyword()

    # Details
    behavioral_notes = Text()
    medical_history = Text(multi=True)
    combined_profile = Text()

    # Media
    photos = Keyword(multi=True)

    # Language
    language = Keyword()  # Detected language code (e.g., 'en', 'ko', 'es')

    # Timestamps
    created_at = Date()
    updated_at = Date()

    class Index:
        name = settings.dogs_index
        # No settings for serverless - managed by Elasticsearch

    def save(self, **kwargs):
        """Override save to set timestamps"""
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
        return super().save(**kwargs)


class Application(AsyncDocument):
    """Elasticsearch Document model for foster/adoption applications - FLAT structure"""

    # Applicant basic info
    applicant_name = Text(fields={"keyword": Keyword()})
    phone = Keyword()
    email = Keyword()
    gender = Keyword()
    address = Text()

    # Housing info
    housing_type = Keyword()  # "Apartment", "Townhouse", "House", etc.
    has_yard = Boolean()
    yard_size_sqm = Integer()

    # Family info
    family_members = Text()  # Description of family members
    all_family_members_agree = Boolean()

    # Pet experience
    experience_level = Keyword()  # "Beginner", "Intermediate", "Experienced"
    has_other_pets = Boolean()
    other_pets_description = Text()

    # Long-form answer
    motivation = Text(analyzer="standard")  # Main motivation essay

    # Application metadata
    animal_applied_for = Keyword()  # e.g., "A77889-Scout"
    status = Keyword()  # "Pending", "Approved", "Rejected"
    language = Keyword()  # Detected language code (e.g., 'en', 'ko', 'es')
    submitted_at = Date()

    class Index:
        name = settings.applications_index

    def save(self, **kwargs):
        """Override save to set timestamps"""
        if not self.submitted_at:
            self.submitted_at = datetime.now()
        return super().save(**kwargs)


class RescueAdoptionOutcome(AsyncDocument):
    """
    Elasticsearch Document model for rescue-adoption outcomes
    Stores both SUCCESS and FAILURE cases for ML learning
    """

    # Core IDs
    outcome_id = Keyword()
    dog_id = Keyword()
    application_id = Keyword()

    # Outcome type
    outcome = Keyword()  # "success", "returned", "foster_to_adopt", "ongoing"

    # Semantic text fields with auto-embeddings via Elasticsearch inference
    outcome_reason = Text()  # Will use semantic_text in index mapping
    success_factors = Text()  # Factors that led to success
    failure_factors = Text()  # Factors that led to failure/return
    follow_up_notes = Text()  # General notes from follow-ups

    # Dates
    adoption_date = Date()
    return_date = Date()
    follow_up_date = Date()

    # Metrics
    days_until_return = Integer()  # null if success, number if returned
    adopter_satisfaction_score = Integer()  # 1-10 rating

    # Context for predictions
    dog_difficulty_level = Keyword()  # "easy", "moderate", "challenging"
    adopter_experience_level = Keyword()  # "beginner", "intermediate", "expert"
    match_score_at_adoption = Float()  # Original compatibility score

    # Metadata
    language = Keyword()  # Detected language code (e.g., 'en', 'ko', 'es')
    created_at = Date()
    created_by = Keyword()

    class Index:
        name = settings.outcomes_index
        # No settings for serverless - managed by Elasticsearch

    def save(self, **kwargs):
        """Override save to set timestamps"""
        if not self.created_at:
            self.created_at = datetime.now()
        return super().save(**kwargs)


class MedicalDocument(AsyncDocument):
    """
    Elasticsearch Document model for medical documents (vet records, prescriptions, etc.)
    """

    # Basic document info
    title = Text(fields={"raw": Keyword()})
    document_type = Keyword()  # "vet_record", "prescription", "lab_result", "vaccination", "surgery_report", "other"
    content = Text(analyzer="standard")  # Extracted text from document
    
    # Animal association
    dog_id = Keyword()  # Associated dog
    dog_name = Text(fields={"keyword": Keyword()})
    
    # Medical details
    diagnosis = Text()
    treatment = Text()
    medications = Keyword(multi=True)
    procedures = Keyword(multi=True)
    
    # Provider info
    veterinarian_name = Text()
    clinic_name = Text()
    clinic_location = Text()
    
    # Dates
    document_date = Date()  # Date of the medical event/visit
    upload_date = Date()
    
    # File metadata
    filename = Keyword()
    file_type = Keyword()  # "pdf", "image", "docx", etc.
    file_size = Integer()  # in bytes
    
    # Classification
    severity = Keyword()  # "routine", "moderate", "severe", "emergency"
    category = Keyword()  # "preventive", "diagnostic", "treatment", "follow_up"
    
    # Metadata
    tags = Keyword(multi=True)
    notes = Text()
    language = Keyword()  # Detected language code (e.g., 'en', 'ko', 'es')
    created_at = Date()
    updated_at = Date()

    class Index:
        name = settings.medical_documents_index
        # No settings for serverless - managed by Elasticsearch

    def save(self, **kwargs):
        """Override save to set timestamps"""
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
        if not self.upload_date:
            self.upload_date = datetime.now()
        return super().save(**kwargs)
