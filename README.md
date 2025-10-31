# 🐾 PawBondAI

**AI-powered platform connecting rescue dogs with adopters and providing veterinary decision support for animal rescue organizations.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

---

## 📋 Table of Contents

- [Problem & Solution](#-problem--solution)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started)
- [Deployment](#-deployment)
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

### Three Core Indices

#### 1. **dogs** - Rescue Dog Profiles
Semantic search on medical history, behavioral notes, and combined profiles for intelligent matching.

<details>
<summary>View full schema</summary>

```json
PUT dogs
{
  "mappings": {
    "properties": {
      "dog_id": {"type": "keyword"},
      "name": {"type": "text"},
      "breed": {"type": "keyword"},
      "age": {"type": "integer"},
      "age_display": {"type": "keyword"},
      "weight_kg": {"type": "float"},
      "sex": {"type": "keyword"},
      "reproductive_status": {
        "properties": {
          "sterilized": {"type": "boolean"},
          "procedure": {"type": "keyword"},
          "date": {"type": "date"},
          "location": {"type": "text"}
        }
      },
      "rescue_date": {"type": "date"},
      "medical_history": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "current_conditions": {"type": "text"},
      "medications": {"type": "text"},
      "vaccinations": {
        "type": "nested",
        "properties": {
          "vaccine_name": {"type": "keyword"},
          "date_administered": {"type": "date"}
        }
      },
      "behavioral_notes": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "combined_profile": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "adoption_status": {"type": "keyword"},
      "created_at": {"type": "date"},
      "updated_at": {"type": "date"}
    }
  }
}
```
</details>

#### 2. **veterinary_knowledge** - RAG Knowledge Base
PDF documents chunked and embedded for precise veterinary information retrieval.

<details>
<summary>View full schema</summary>

```json
PUT veterinary_knowledge
{
  "mappings": {
    "properties": {
      "attachment": {
        "properties": {
          "title": {"type": "text"},
          "content_chunk": {
            "type": "semantic_text",
            "inference_id": "google_vertex_ai_embedding"
          }
        }
      },
      "filename": {"type": "keyword"},
      "chunk_number": {"type": "integer"},
      "total_chunks": {"type": "integer"},
      "source": {"type": "keyword"},
      "upload_date": {"type": "date"},
      "processed_date": {"type": "date"},
      "metadata": {
        "type": "object",
        "dynamic": true
      }
    }
  }
}
```
</details>

#### 3. **case_studies** - Rescue Network Knowledge Sharing
Real medical cases with semantic search, geo-discovery, and privacy controls.

<details>
<summary>View full schema</summary>

```json
PUT case_studies
{
  "mappings": {
    "properties": {
      "case_id": {"type": "keyword"},
      "title": {"type": "text"},
      "rescue_organization": {"type": "keyword"},
      "organization_contact": {"type": "keyword"},
      "date_published": {"type": "date"},
      "visibility": {"type": "keyword"},
      "is_shareable": {"type": "boolean"},
      "geographic_location": {"type": "geo_point"},
      "country": {"type": "keyword"},
      "region": {"type": "keyword"},
      "patient_species": {"type": "keyword"},
      "patient_breed": {"type": "keyword"},
      "patient_age_years": {"type": "integer"},
      "patient_age_months": {"type": "integer"},
      "patient_age_category": {"type": "keyword"},
      "patient_sex": {"type": "keyword"},
      "patient_weight_kg": {"type": "float"},
      "patient_weight_category": {"type": "keyword"},
      "is_juvenile": {"type": "boolean"},
      "is_geriatric": {"type": "boolean"},
      "presenting_complaint": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "clinical_history": {"type": "text"},
      "physical_examination": {"type": "text"},
      "diagnostic_tests": {"type": "text"},
      "diagnosis": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "treatment_plan": {"type": "text"},
      "outcome": {"type": "text"},
      "follow_up": {"type": "text"},
      "combined_case_text": {
        "type": "semantic_text",
        "inference_id": "google_vertex_ai_embedding"
      },
      "learning_points": {"type": "text"},
      "tags": {"type": "keyword"},
      "disease_category": {"type": "keyword"},
      "urgency_level": {"type": "keyword"},
      "references": {"type": "text"},
      "estimated_cost": {"type": "float"},
      "cost_breakdown": {"type": "text"},
      "created_at": {"type": "date"},
      "updated_at": {"type": "date"}
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
- **Netlify** - Frontend hosting (planned)
- **Cloud Run** - Backend containerized deployment (planned)
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

## 📦 Deployment

### Frontend Deployment (Netlify)

**Prerequisites:**
- Netlify account ([Sign up](https://app.netlify.com/signup))
- Netlify CLI installed: `npm install -g netlify-cli`

**Deploy:**

```bash
cd frontend

# Build the app
npm run build

# Login to Netlify
netlify login

# Deploy
netlify deploy --prod

# Follow prompts:
# - Site name: pawbondai (or your choice)
# - Publish directory: dist
```

**Set environment variables in Netlify:**

1. Go to Site settings → Environment variables
2. Add: `VITE_API_URL=https://your-backend-url.run.app/api/v1`

Your frontend will be live at: `https://pawbondai.netlify.app`

### Backend Deployment (Google Cloud Run)

**Prerequisites:**
- Google Cloud SDK installed ([Install](https://cloud.google.com/sdk/docs/install))
- Docker installed ([Install](https://docs.docker.com/get-docker/))
- GCP project with billing enabled

**1. Create Dockerfile:**

Already included at `/backend/Dockerfile`

**2. Deploy to Cloud Run:**

```bash
cd backend

# Authenticate with GCP
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud run deploy pawbondai-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT_ID \
  --set-env-vars VERTEX_AI_LOCATION=us-central1 \
  --set-env-vars GEMINI_MODEL=gemini-1.5-flash \
  --set-env-vars ELASTICSEARCH_URL=YOUR_ES_URL \
  --set-env-vars ELASTICSEARCH_API_KEY=YOUR_ES_KEY \
  --set-env-vars GCS_BUCKET_NAME=YOUR_BUCKET_NAME \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300

# Note: Replace YOUR_* with actual values
```

**3. Get your backend URL:**

```bash
gcloud run services describe pawbondai-backend --region us-central1 --format 'value(status.url)'
```

**4. Update frontend environment:**

Update Netlify environment variable `VITE_API_URL` with your Cloud Run URL.

---

## 📚 API Documentation

### Key Endpoints

#### Chat & Search

```http
POST /api/v1/chat/message
Content-Type: application/json

{
  "message": "Find experienced adopters with yards",
  "context": {
    "session_id": "uuid"
  }
}
```

#### Application Analysis

```http
POST /api/v1/chat/analyze-application
Content-Type: application/json

{
  "application_text": "I've had dogs my whole life..."
}
```

#### Dog Profiles

```http
GET /api/v1/dogs/{dog_id}
GET /api/v1/dogs?limit=10&offset=0
POST /api/v1/dogs
```

#### Medical Documents

```http
POST /api/v1/medical-documents/upload
GET /api/v1/medical-documents?dog_id={id}
```

#### Analytics

```http
GET /api/v1/analytics/adoption-trends
GET /api/v1/analytics/medical-conditions
```

**Full API documentation:** Visit `/docs` on your running backend

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
