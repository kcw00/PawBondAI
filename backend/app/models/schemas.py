from datetime import datetime
from typing import Optional, Dict, Any, List, Literal, TypedDict
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


# Medical Event Model
class MedicalEvent(BaseModel):
    date: Optional[str] = None
    event_type: str  # vaccination, surgery, diagnosis, treatment, checkup, injury, other
    condition: str
    treatment: Optional[str] = None
    severity: str  # mild, moderate, severe
    outcome: str  # resolved, ongoing, improved, worsened
    description: Optional[str] = None
    location: Optional[str] = None


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
    medical_history: Optional[str] = None  # Free-text medical history for AI extraction


class DogResponse(DogBase):
    id: str
    medical_history: Optional[str] = None  # Free-text medical history
    medical_events: Optional[List[MedicalEvent]] = None
    past_conditions: Optional[List[str]] = None
    active_treatments: Optional[List[str]] = None
    severity_score: Optional[int] = None
    adoption_readiness: Optional[str] = None  # ready, needs_treatment, long_term_care
    medical_document_ids: Optional[List[str]] = None
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
    intent: Optional[str] = None  # Intent type (find_adopters, analyze_application, etc.)
    metadata: Optional[Dict[str, Any]] = None  # Matches, analysis results, etc.
    tool_calls: Optional[List[dict]] = None
    intent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """
    Unified chat request model supporting both general chat and dog-specific queries
    """
    message: str
    context: Optional[Dict[str, Any]] = None  # General context (session_id, etc.)
    dog_id: Optional[str] = None  # Specific dog being discussed
    image_url: Optional[str] = None  # Optional image for analysis
    conversation_history: List[ChatMessage] = []  # Chat history


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


# FLAT APPLICATION SCHEMA (matches current ES mapping)
class ApplicationCreate(BaseModel):
    """Schema for creating a new application - FLAT structure"""

    # Applicant basic info
    applicant_name: str
    phone: str
    email: str
    gender: Optional[str] = None
    address: Optional[str] = None

    # Housing info
    housing_type: str  # "Apartment", "Townhouse", "House", etc.
    has_yard: bool = False
    yard_size_sqm: Optional[int] = None

    # Family info
    family_members: Optional[str] = None  # Description of family members
    all_family_members_agree: bool = True

    # Pet experience
    experience_level: str  # "Beginner", "Intermediate", "Experienced"
    has_other_pets: bool = False
    other_pets_description: Optional[str] = None

    # Long-form answer
    motivation: str  # Main motivation essay

    # Application metadata
    animal_applied_for: Optional[str] = None  # e.g., "A77889-Scout"
    status: str = "Pending"  # "Pending", "Approved", "Rejected"
    submitted_at: Optional[datetime] = None


class ApplicationResponse(BaseModel):
    """Schema for application response - FLAT structure"""

    id: str

    # Applicant basic info
    applicant_name: str
    phone: str
    email: str
    gender: Optional[str] = None
    address: Optional[str] = None

    # Housing info
    housing_type: str
    has_yard: bool
    yard_size_sqm: Optional[int] = None

    # Family info
    family_members: Optional[str] = None
    all_family_members_agree: bool

    # Pet experience
    experience_level: str
    has_other_pets: bool
    other_pets_description: Optional[str] = None

    # Long-form answer
    motivation: str

    # Application metadata
    animal_applied_for: Optional[str] = None
    status: str
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

        @classmethod
        def from_es_hit(cls, hit):
            doc_id = hit.meta.id
            data = {key: getattr(hit, key, None) for key in cls.model_fields if key != "id"}
            return cls(id=doc_id, **data)


# Rescue Adoption Outcome Models
class OutcomeCreate(BaseModel):
    dog_id: str
    application_id: str
    outcome: str  # "success", "returned", "foster_to_adopt", "ongoing"
    outcome_reason: str
    success_factors: Optional[str] = None
    failure_factors: Optional[str] = None
    adoption_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    adopter_satisfaction_score: Optional[int] = None
    dog_difficulty_level: Optional[str] = "moderate"
    adopter_experience_level: Optional[str] = "intermediate"
    match_score: Optional[float] = None
    created_by: str = "system"


class OutcomeResponse(BaseModel):
    outcome_id: str
    dog_id: str
    application_id: str
    outcome: str
    outcome_reason: Optional[str] = None
    success_factors: Optional[str] = None
    failure_factors: Optional[str] = None
    adoption_date: Optional[str] = None
    return_date: Optional[str] = None
    days_until_return: Optional[int] = None
    adopter_satisfaction_score: Optional[int] = None
    dog_difficulty_level: Optional[str] = None
    adopter_experience_level: Optional[str] = None
    match_score_at_adoption: Optional[float] = None
    created_at: Optional[str] = None
    created_by: Optional[str] = None


class OutcomeStatsResponse(BaseModel):
    total_outcomes: int
    successful_adoptions: int
    returned_adoptions: int
    success_rate: float


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


# Bulk Upload Models
class BulkDogUpload(BaseModel):
    name: str
    breed: Optional[str] = None
    age: Optional[int] = None
    medical_history: Optional[str] = None
    weight_kg: Optional[float] = None
    sex: Optional[str] = None


class BulkUploadResponse(BaseModel):
    total_processed: int
    successful: int
    failed: int
    dog_ids: List[str]
    errors: List[Dict[str, Any]]


# Sentiment Models
class MotivationRequest(BaseModel):
    motivation_text: str = Field(
        ..., min_length=20, description="The adopter's motivation essay or text."
    )


class SentimentResponse(BaseModel):
    score: float
    magnitude: float
    interpretation: str


class EntityResponse(BaseModel):
    name: str
    type: str
    salience: float
    mentions: List[str]


class CommitmentResponse(BaseModel):
    commitment_score: int
    commitment_level: str
    word_count: int
    positive_indicators: int
    red_flags: int


# Analytics Models
class AnalysisResponse(BaseModel):
    sentiment: SentimentResponse
    key_entities: List[EntityResponse]
    key_themes: List[str]
    commitment_assessment: CommitmentResponse
    text_length: int
    recommendation: str


class PredictionRequest(BaseModel):
    adopter_experience: str  # "beginner", "intermediate", "expert"
    dog_difficulty: str  # "easy", "moderate", "challenging"
    match_score: float  # 0.0 to 1.0


# Additional Chat Models
class AnalyzeApplicationRequest(BaseModel):
    application_text: str


# Medical Extraction Models
class MedicalEvent(TypedDict):
    date: Optional[str]
    event_type: Literal[
        "vaccination", "surgery", "diagnosis", "treatment", "checkup", "injury", "other"
    ]
    condition: str
    treatment: Optional[str]
    severity: Literal["mild", "moderate", "severe"]
    outcome: Literal["resolved", "ongoing", "improved", "worsened"]
    description: str
    location: Optional[str]


class ExtractedMedicalData(TypedDict):
    medical_events: List[MedicalEvent]


# Chat History Models
class ChatSession(BaseModel):
    """Represents a chat session with message history"""
    session_id: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = []
    metadata: Optional[Dict[str, Any]] = None  # User info, tags, etc.


class ChatHistoryResponse(BaseModel):
    """Response for fetching chat history"""
    session_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    messages: List[ChatMessage]
    metadata: Optional[Dict[str, Any]] = None


class ChatSessionListResponse(BaseModel):
    """Response for listing all chat sessions"""
    sessions: List[Dict[str, Any]]  # [{session_id, created_at, message_count, preview}]
    total: int


class SaveMessageRequest(BaseModel):
    """Request to save a chat message"""
    session_id: str
    role: Literal["user", "assistant"]
    content: str
    intent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class UpdateChatNameRequest(BaseModel):
    """Request to update chat session name"""
    name: str = Field(..., min_length=1, max_length=100, description="New name for the chat session")


# Translation Models
class TranslationRequest(BaseModel):
    """Request to translate text using Gemini's multilingual capabilities"""
    text: str = Field(..., description="Text to translate")
    target_language: str = Field(default="English", description="Target language name (e.g., 'English', 'Spanish', 'Korean', 'Chinese')")
    source_language: Optional[str] = Field(None, description="Source language name (if None, will auto-detect)")


class TranslationResponse(BaseModel):
    """Response from translation service"""
    translated_text: str = Field(..., description="The translated text")
    source_language: str = Field(..., description="Detected or provided source language")
    target_language: str = Field(..., description="Target language")
    confidence: float = Field(..., description="Translation confidence score (0.0-1.0)")
    error: Optional[str] = Field(None, description="Error message if translation failed")
