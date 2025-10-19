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
    DenseVector,
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
    content_embedding = DenseVector(dims=768)  # Adjust dims based on your embedding model

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

    # Vector embeddings
    symptoms_embedding = DenseVector(dims=768)

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

    # Timestamps
    created_at = Date()
    updated_at = Date()

    class Index:
        name = "dogs"
        # No settings for serverless - managed by Elasticsearch

    def save(self, **kwargs):
        """Override save to set timestamps"""
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
        return super().save(**kwargs)


# Inner document classes for nested objects
class ApplicantInfo(InnerDoc):
    """Nested applicant information"""
    name = Text(fields={"raw": Keyword()})
    phone = Keyword()
    email = Keyword()
    gender = Keyword()
    age = Integer()
    home_address_full_text = Text()
    home_address_location = GeoPoint()
    social_media_platform = Keyword()
    social_media_handle = Keyword()
    occupation = Text()
    marital_status = Keyword()
    emergency_contact_relationship = Text()
    emergency_contact_phone = Keyword()


class HouseholdInfo(InnerDoc):
    """Nested household information"""
    household_size = Integer()
    members_description = Text()
    all_members_agree = Text()
    has_allergies = Boolean()
    allergy_details = Text()


class HousingInfo(InnerDoc):
    """Nested housing information"""
    type = Keyword()  # Apartment, Detached House, etc.
    ownership_status = Keyword()  # Owned, Leased, etc.
    size_sqm = Integer()
    landlord_permission_granted = Keyword()  # Yes, No, Not_Applicable
    photo_urls = Keyword(multi=True)
    has_yard_or_balcony = Boolean()


class PetExperience(InnerDoc):
    """Nested pet experience information"""
    has_current_or_past_pets = Boolean()
    pet_history_details = Text()
    new_pet_introduction_plan = Text()
    ever_surrendered_pet = Boolean()
    surrender_reason = Text()
    volunteer_experience_details = Text()


class LongFormAnswers(InnerDoc):
    """Nested long-form essay answers"""
    motivation_for_this_animal = Text(analyzer="standard")
    general_adoption_motivation = Text(analyzer="standard")
    behavioral_issue_plan = Text(analyzer="standard")
    life_changes_plan = Text(analyzer="standard")
    opinion_on_off_leash = Text(analyzer="standard")
    opinion_on_neutering = Text(analyzer="standard")


class ApplicationMeta(InnerDoc):
    """Nested application metadata"""
    status = Keyword()  # Pending, Approved, Rejected, On-Hold
    type = Keyword()  # Adoption or Foster
    animal_name_applied_for = Keyword()
    animal_id_applied_for = Keyword()
    source = Keyword()  # How they heard about the animal
    is_kara_donor = Boolean()
    language = Keyword()  # e.g., "ko", "en"
    submitted_at = Date()
    updated_at = Date()


class Application(AsyncDocument):
    """Elasticsearch Document model for foster/adoption applications with nested structure"""

    # Nested objects
    applicant_info = Object(ApplicantInfo)
    household_info = Object(HouseholdInfo)
    housing_info = Object(HousingInfo)
    pet_experience = Object(PetExperience)
    long_form_answers = Object(LongFormAnswers)
    application_meta = Object(ApplicationMeta)

    # Core field for hybrid search with dense vector
    application_summary_embedding = DenseVector(dims=768, index=True, similarity="cosine")

    class Index:
        name = "applications"
        # No settings for serverless - managed by Elasticsearch

    def save(self, **kwargs):
        """Override save to set timestamps"""
        if not self.application_meta:
            self.application_meta = ApplicationMeta()
        if not self.application_meta.submitted_at:
            self.application_meta.submitted_at = datetime.now()
        self.application_meta.updated_at = datetime.now()
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
    created_at = Date()
    created_by = Keyword()

    class Index:
        name = "rescue-adoption-outcomes"
        # No settings for serverless - managed by Elasticsearch

    def save(self, **kwargs):
        """Override save to set timestamps"""
        if not self.created_at:
            self.created_at = datetime.now()
        return super().save(**kwargs)
