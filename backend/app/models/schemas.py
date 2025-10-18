from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class UrgencyLevel(str, Enum):
    EMERGENCY = "emergency"
    URGENT = "urgent"
    ROUTINE = "routine"


class Language(str, Enum):
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    RUSSIAN = "ru"
    HINDI = "hi"


# Dog Models
class DogBase(BaseModel):
    name: str
    breed: Optional[str] = None
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    sex: Optional[str] = None
    rescue_date: Optional[str] = None
    adoption_status: Optional[str] = None
    behavioral_notes: Optional[str] = None
    combined_profile: Optional[str] = None


class DogCreate(DogBase):
    pass


class DogResponse(DogBase):
    id: str
    medical_history: Optional[List[str]] = None
    photos: Optional[List[str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# Article Models
class ArticleBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None
    language: Language = Language.ENGLISH
    tags: List[str] = []


class ArticleCreate(ArticleBase):
    pass


class ArticleResponse(ArticleBase):
    id: str
    upload_date: datetime

    class Config:
        from_attributes = True


# Case Study Models
class CaseStudyBase(BaseModel):
    title: str
    diagnosis: str
    treatment_plan: str
    outcome: str
    presenting_complaint: Optional[str] = None
    clinical_history: Optional[str] = None
    physical_examination: Optional[str] = None
    diagnostic_tests: Optional[str] = None
    follow_up: Optional[str] = None
    learning_points: Optional[str] = None

    # Patient info
    patient_species: str = "canine"
    patient_breed: Optional[str] = None
    patient_age_years: Optional[int] = None
    patient_age_months: Optional[int] = None
    patient_age_category: Optional[str] = None
    patient_sex: Optional[str] = None
    patient_weight_kg: Optional[float] = None
    patient_weight_category: Optional[str] = None
    is_juvenile: bool = False
    is_geriatric: bool = False

    # Organization & Location
    rescue_organization: Optional[str] = None
    organization_contact: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None

    # Cost & Classification
    estimated_cost: Optional[float] = None
    cost_breakdown: Optional[str] = None
    disease_category: Optional[str] = None
    urgency_level: Optional[str] = None

    # Metadata
    tags: List[str] = []
    references: Optional[str] = None
    visibility: str = "public"
    is_shareable: bool = True
    date_published: Optional[str] = None


class CaseStudyCreate(CaseStudyBase):
    pass


class CaseStudyResponse(CaseStudyBase):
    id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# Chat Models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    tool_calls: Optional[List[dict]] = None


class ChatRequest(BaseModel):
    message: str
    dog_id: Optional[str] = None
    image_url: Optional[str] = None
    conversation_history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    message: str
    urgency: Optional[UrgencyLevel] = None
    sources: List[dict] = []
    tool_calls: List[dict] = []


# Search Models
class SearchRequest(BaseModel):
    query: str
    limit: int = 5


class SearchResult(BaseModel):
    id: str
    title: str
    content: str
    score: float
    source: Optional[str] = None


# Application Models - Nested Structure
class ApplicantInfoSchema(BaseModel):
    """Applicant information schema"""
    name: str
    phone: str
    email: str
    gender: Optional[str] = None
    age: Optional[int] = None
    home_address_full_text: Optional[str] = None
    home_address_location: Optional[dict] = None  # {"lat": float, "lon": float}
    social_media_platform: Optional[str] = None
    social_media_handle: Optional[str] = None
    occupation: Optional[str] = None
    marital_status: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    emergency_contact_phone: Optional[str] = None


class HouseholdInfoSchema(BaseModel):
    """Household information schema"""
    household_size: int = 1
    members_description: Optional[str] = None
    all_members_agree: Optional[str] = None
    has_allergies: bool = False
    allergy_details: Optional[str] = None


class HousingInfoSchema(BaseModel):
    """Housing information schema"""
    type: str  # Apartment, Detached House, etc.
    ownership_status: str  # Owned, Leased, etc.
    size_sqm: Optional[int] = None
    landlord_permission_granted: str = "Not_Applicable"  # Yes, No, Not_Applicable
    photo_urls: List[str] = []
    has_yard_or_balcony: bool = False


class PetExperienceSchema(BaseModel):
    """Pet experience schema"""
    has_current_or_past_pets: bool = False
    pet_history_details: Optional[str] = None
    new_pet_introduction_plan: Optional[str] = None
    ever_surrendered_pet: bool = False
    surrender_reason: Optional[str] = None
    volunteer_experience_details: Optional[str] = None


class LongFormAnswersSchema(BaseModel):
    """Long-form essay answers schema"""
    motivation_for_this_animal: str
    general_adoption_motivation: str
    behavioral_issue_plan: str
    life_changes_plan: str
    opinion_on_off_leash: str
    opinion_on_neutering: str


class ApplicationMetaSchema(BaseModel):
    """Application metadata schema"""
    status: str = "Pending"  # Pending, Approved, Rejected, On-Hold
    type: str  # Adoption or Foster
    animal_name_applied_for: Optional[str] = None
    animal_id_applied_for: Optional[str] = None
    source: Optional[str] = None
    is_kara_donor: bool = False
    language: str = "ko"  # Default to Korean
    submitted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ApplicationCreate(BaseModel):
    """Schema for creating a new application"""
    applicant_info: ApplicantInfoSchema
    household_info: HouseholdInfoSchema
    housing_info: HousingInfoSchema
    pet_experience: PetExperienceSchema
    long_form_answers: LongFormAnswersSchema
    application_meta: ApplicationMetaSchema


class ApplicationResponse(BaseModel):
    """Schema for application response"""
    id: str
    applicant_info: ApplicantInfoSchema
    household_info: HouseholdInfoSchema
    housing_info: HousingInfoSchema
    pet_experience: PetExperienceSchema
    long_form_answers: LongFormAnswersSchema
    application_meta: ApplicationMetaSchema

    class Config:
        from_attributes = True


# Matching Models
class DimensionScore(BaseModel):
    experience: float
    housing: float
    lifestyle: float
    household: float
    motivation: float


class CompatibilityResult(BaseModel):
    overall_score: float
    dimension_scores: DimensionScore
    recommendation: str  # approve, review, reject
    concerns: List[str]
    application_id: str
    dog_id: str


class RankedApplication(BaseModel):
    application: ApplicationResponse
    compatibility: CompatibilityResult


class MatchingResponse(BaseModel):
    dog_id: str
    total_applications: int
    ranked_applications: List[RankedApplication]


# Intake Assessment Models
class IntakeAssessmentRequest(BaseModel):
    dog_name: str
    breed: Optional[str] = None
    approximate_age: Optional[int] = None
    rescue_notes: Optional[str] = None


class IntakeAssessmentResponse(BaseModel):
    dog_id: str
    visual_analysis: str  # Results from Gemini Vision
    behavioral_assessment: str
    medical_concerns: List[str]
    recommended_actions: List[str]
    urgency_level: str  # low, medium, high
    created_at: datetime
