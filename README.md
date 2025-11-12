# 🐾 PawBondAI

**AI-powered platform connecting rescue dogs with adopters and providing veterinary decision support for animal rescue organizations.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

---

## 📷 Live Demo

Try it here: https://pawbondai.netlify.app/

![ScreenRecording2025-11-04at12 59 38-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/3437900e-51e3-453d-93a7-eb26485162fb)
![ezgif com-video-to-gif-converter (3)](https://github.com/user-attachments/assets/30e2874b-5639-498e-a3fb-f2559c1365e8)


---

## 📋 Table of Contents

- [Problem & Solution](#-problem--solution)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)

---

## 🎯 Problem & Solution

### The Challenge

Animal rescue organizations face critical challenges:

1. **Inefficient Matching**: Basic filters (age, breed, size) miss behavioral and lifestyle compatibility
2. **Limited Veterinary Access**: Small rescues lack on-call veterinary expertise for medical decisions
3. **Knowledge Silos**: Rescues can't easily learn from each other's experiences with similar cases
4. **Language Barriers**: International rescue networks struggle with multilingual medical documents

### Our Solution

A **RAG (Retrieval-Augmented Generation)** system built on **Elasticsearch** and **Google Vertex AI** that provides:

✅ **Semantic Adopter Matching** - AI-powered compatibility scoring beyond basic filters  
✅ **Conversational AI Assistant** - Natural language queries for finding adopters and analyzing applications  
✅ **Veterinary Knowledge Base** - Instant access to medical literature and similar case studies  
✅ **Multilingual Support** - Translation and entity extraction for international collaboration  
✅ **Predictive Analytics** - Success prediction based on historical adoption outcomes

## ✨ Key Features

### 🔍 Intelligent Search & Matching

- **Semantic Search**: Uses Google Vertex AI embeddings for nuanced matching beyond keywords
- **Hybrid Queries**: Combines semantic similarity with structured filters (housing, experience, location)
- **Behavioral Compatibility**: Matches adopter lifestyle with dog personality and medical needs
- **Multi-field Scoring**: Weighs motivation, experience, and housing suitability

### 💬 Conversational AI Assistant

- **Natural Language Queries**: "Find experienced adopters with large yards for anxious dogs"
- **Intent Detection**: Automatically routes to search, analysis, or general Q&A
- **Application Analysis**: Evaluates adoption applications with sentiment and commitment scoring
- **Chat History**: Persistent conversations with session management via Google Cloud Storage

### 🏥 Veterinary Decision Support

- **Medical Document Processing**: OCR + entity extraction from vet records
- **Case Study Database**: Searchable repository of medical cases with geo-discovery
- **Similar Cases Search**: Find relevant treatment protocols and outcomes
- **Cost Estimation**: Predict treatment costs based on historical data

### 📊 Analytics & Insights

- **Adoption Success Prediction**: ML-based scoring using historical outcomes
- **Trend Analysis**: Track adoption rates, medical conditions, and applicant demographics
- **Performance Metrics**: Query timing, match quality, and system health monitoring

### 🌐 Multilingual Support

- **Auto-Translation**: Korean, Spanish, Chinese → English
- **Entity Extraction**: Structured data from translated medical documents
- **Cross-Border Collaboration**: International rescue network coordination

## 📊 Elasticsearch Architecture

### Four Core Indices

#### 1. **dogs** - Rescue Dog Profiles
Semantic search on medical history, behavioral notes, and combined profiles for intelligent matching.

<details>
<summary>View full schema</summary>

```json
PUT dogs
{
  "mappings": {
    "properties": {
      "name": {"type": "text", "fields": {"raw": {"type": "keyword"}}},
      "breed": {"type": "keyword"},
      "age": {"type": "integer"},
      "weight_kg": {"type": "float"},
      "sex": {"type": "keyword"},
      "rescue_date": {"type": "date"},
      "adoption_status": {"type": "keyword"},
      "rescue_organization": {"type": "keyword"},
      "behavioral_notes": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "medical_history": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "combined_profile": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "photos": {"type": "keyword"},
      "language": {"type": "keyword"},
      "created_at": {"type": "date"},
      "updated_at": {"type": "date"}
    }
  }
}
```
</details>

#### 2. **applications** - Adoption Applications
Hybrid search combining semantic analysis of motivation essays with structured filters for housing, experience, and pet compatibility.

<details>
<summary>View full schema</summary>

```json
PUT applications
{
  "mappings": {
    "properties": {
      "applicant_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
      "phone": {"type": "keyword"},
      "email": {"type": "keyword"},
      "gender": {"type": "keyword"},
      "address": {"type": "text"},
      "housing_type": {"type": "keyword"},
      "has_yard": {"type": "boolean"},
      "yard_size_sqm": {"type": "integer"},
      "family_members": {"type": "text"},
      "all_family_members_agree": {"type": "boolean"},
      "experience_level": {"type": "keyword"},
      "has_other_pets": {"type": "boolean"},
      "other_pets_description": {"type": "text"},
      "motivation": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "animal_applied_for": {"type": "keyword"},
      "status": {"type": "keyword"},
      "language": {"type": "keyword"},
      "submitted_at": {"type": "date"}
    }
  }
}
```
</details>

#### 3. **medical_documents** - Veterinary Records
OCR-processed medical documents with multilingual support and semantic search for finding similar cases.

<details>
<summary>View full schema</summary>

```json
PUT medical_documents
{
  "mappings": {
    "properties": {
      "title": {"type": "text", "fields": {"raw": {"type": "keyword"}}},
      "document_type": {"type": "keyword"},
      "content": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "dog_id": {"type": "keyword"},
      "dog_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
      "diagnosis": {"type": "text"},
      "treatment": {"type": "text"},
      "medications": {"type": "keyword"},
      "procedures": {"type": "keyword"},
      "veterinarian_name": {"type": "text"},
      "clinic_name": {"type": "text"},
      "clinic_location": {"type": "text"},
      "document_date": {"type": "date"},
      "upload_date": {"type": "date"},
      "filename": {"type": "keyword"},
      "file_type": {"type": "keyword"},
      "file_size": {"type": "integer"},
      "severity": {"type": "keyword"},
      "category": {"type": "keyword"},
      "tags": {"type": "keyword"},
      "notes": {"type": "text"},
      "language": {"type": "keyword"},
      "created_at": {"type": "date"},
      "updated_at": {"type": "date"}
    }
  }
}
```
</details>

#### 4. **rescue-adoption-outcomes** - Adoption Success Tracking
ML-powered pattern learning from successful and failed adoptions for predictive matching.

<details>
<summary>View full schema</summary>

```json
PUT rescue-adoption-outcomes
{
  "mappings": {
    "properties": {
      "outcome_id": {"type": "keyword"},
      "dog_id": {"type": "keyword"},
      "application_id": {"type": "keyword"},
      "outcome": {"type": "keyword"},
      "outcome_reason": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "success_factors": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "failure_factors": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "follow_up_notes": {"type": "text"},
      "adoption_date": {"type": "date"},
      "return_date": {"type": "date"},
      "follow_up_date": {"type": "date"},
      "days_until_return": {"type": "integer"},
      "adopter_satisfaction_score": {"type": "integer"},
      "dog_difficulty_level": {"type": "keyword"},
      "adopter_experience_level": {"type": "keyword"},
      "match_score_at_adoption": {"type": "float"},
      "language": {"type": "keyword"},
      "created_at": {"type": "date"},
      "created_by": {"type": "keyword"}
    }
  }
}
```
</details>

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework for APIs
- **Python 3.11+** - Core programming language
- **Elasticsearch 8.x** - Search engine with semantic_text support
- **Google Vertex AI** - Gemini 1.5 for embeddings and chat
- **BigQuery** - Data warehousing and ML predictions
- **Google Cloud Storage** - Chat history persistence
- **Pydantic** - Data validation and settings management

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **shadcn/ui** - Accessible component library
- **TanStack Query** - Data fetching and caching
- **Lucide Icons** - Beautiful icon set

### Infrastructure
- **Google Cloud Platform** - Primary cloud provider
- **Netlify** - Frontend hosting
- **Cloud Run** - Backend containerized deployment
- **Application Default Credentials** - GCP authentication

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Elasticsearch 8.x** (Local or Cloud)
- **Google Cloud Account** with Vertex AI API enabled
- **GCP Application Default Credentials** configured

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/PawBondAI.git
cd PawBondAI
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

**Edit `.env` with your credentials:**

```env
# GCP Configuration
GCP_PROJECT_ID=your-project-id
VERTEX_AI_LOCATION=us-central1
GEMINI_MODEL=gemini-1.5-flash

# Elasticsearch Configuration
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_API_KEY=your-api-key

# Google Cloud Storage
GCS_BUCKET_NAME=your-bucket-name

# App Configuration
DEBUG=True
APP_NAME=PawBondAI
```

**Start the backend server:**

```bash
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: **http://localhost:8000**  
API docs: **http://localhost:8000/docs**

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
```

**Edit `.env`:**

```env
VITE_API_URL=http://localhost:8000/api/v1
```

**Start the dev server:**

```bash
npm run dev
```

Frontend will be available at: **http://localhost:5173**

### 4. Elasticsearch Setup

**Option A: Local Elasticsearch**

```bash
# Download and run Elasticsearch 8.x
# Follow: https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html
```

**Option B: Elastic Cloud**

1. Sign up at [cloud.elastic.co](https://cloud.elastic.co)
2. Create a deployment
3. Copy the Cloud ID and API key to your `.env`

**Create indices:**

```bash
# From backend directory
python scripts/setup_indices.py
```

### 5. Load Sample Data

```bash
# From backend directory
python scripts/load_sample_data.py
```

---

## 📚 API Documentation

### Key Endpoints

#### 💬 Chat & AI Assistant

```http
POST /api/v1/chat/message
Content-Type: application/json

{
  "message": "Find experienced adopters with yards for anxious dogs",
  "context": {
    "session_id": "uuid"
  },
  "dog_id": "optional_dog_id"
}
```

```http
POST /api/v1/chat/analyze-application
Content-Type: application/json

{
  "application_text": "I've had dogs my whole life and work from home..."
}
```

#### 🐕 Dog Profiles

```http
# CRUD Operations
GET    /api/v1/dogs?limit=10&offset=0
GET    /api/v1/dogs/{dog_id}
POST   /api/v1/dogs
PUT    /api/v1/dogs/{dog_id}
DELETE /api/v1/dogs/{dog_id}

# Search & Matching
POST   /api/v1/dogs/search              # Semantic search
GET    /api/v1/dogs/{dog_id}/matches    # Find compatible adopters
POST   /api/v1/dogs/bulk-upload         # CSV bulk upload

# Medical History
GET    /api/v1/dogs/{dog_id}/history
```

#### 📝 Applications

```http
# CRUD Operations
GET    /api/v1/applications?limit=10&offset=0
GET    /api/v1/applications/{application_id}
POST   /api/v1/applications
PUT    /api/v1/applications/{application_id}
DELETE /api/v1/applications/{application_id}

# Search & Bulk Upload
POST   /api/v1/applications/search      # Semantic search on motivation
POST   /api/v1/applications/csv/validate
POST   /api/v1/applications/csv/preview
POST   /api/v1/applications/csv/upload
```

#### 🏥 Medical Documents

```http
POST   /api/v1/medical-documents/upload
GET    /api/v1/medical-documents?dog_id={id}
GET    /api/v1/medical-documents/{document_id}
GET    /api/v1/medical-documents/search/content
DELETE /api/v1/medical-documents/{document_id}
```

#### 📊 Adoption Outcomes

```http
# Outcome Tracking
GET    /api/v1/outcomes?limit=10
POST   /api/v1/outcomes
GET    /api/v1/outcomes/{outcome_id}
GET    /api/v1/outcomes/dog/{dog_id}

# Statistics & Pattern Learning
GET    /api/v1/outcomes/stats           # Success rate calculations
GET    /api/v1/outcomes/successful
GET    /api/v1/outcomes/failed
POST   /api/v1/outcomes/search          # Semantic pattern search

# Bulk Upload
POST   /api/v1/outcomes/csv/upload
```

#### 📈 Analytics & Predictions

```http
GET    /api/v1/analytics/success-rates
POST   /api/v1/analytics/predict        # Predict adoption success
POST   /api/v1/analytics/sentiment      # Analyze motivation text
GET    /api/v1/analytics/dashboard
GET    /api/v1/analytics/index-stats
```

#### 💭 Chat History

```http
POST   /api/v1/chat/history/new
GET    /api/v1/chat/history/sessions?limit=10
GET    /api/v1/chat/history/{session_id}
PATCH  /api/v1/chat/history/{session_id}/name
DELETE /api/v1/chat/history/{session_id}
POST   /api/v1/chat/history/save
```

**Full API documentation:** Visit `/docs` on your running backend (Swagger UI at http://localhost:8000/docs)

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 📁 Project Structure

```
PawBondAI/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Config, logging, agent
│   │   ├── models/        # Pydantic models & ES documents
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI app
│   ├── tests/             # Backend tests
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Container config
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Route pages
│   │   ├── services/      # API clients
│   │   └── contexts/      # React contexts
│   ├── package.json       # Node dependencies
│   └── netlify.toml       # Netlify config
├── data/                  # Sample data & PDFs
├── scripts/               # Utility scripts
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---

## 🙏 Acknowledgments

- **Elasticsearch** for powerful search capabilities
- **Google Cloud** for Vertex AI and infrastructure
- **FastAPI** for excellent API framework
- **shadcn/ui** for beautiful UI components
- Animal rescue organizations for inspiration and feedback

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/PawBondAI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/PawBondAI/discussions)
