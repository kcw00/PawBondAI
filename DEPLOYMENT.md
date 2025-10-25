# 🚀 Deployment Guide

Complete step-by-step guide for deploying PawBondAI to production.

---

## 📋 Pre-Deployment Checklist

### Backend Requirements
- [ ] Google Cloud Project created with billing enabled
- [ ] Vertex AI API enabled
- [ ] Cloud Run API enabled
- [ ] Cloud Storage bucket created for chat history
- [ ] Elasticsearch cluster running (local or Elastic Cloud)
- [ ] Environment variables documented

### Frontend Requirements
- [ ] Netlify account created
- [ ] Netlify CLI installed: `npm install -g netlify-cli`
- [ ] Backend URL ready (will get from Cloud Run)
- [ ] Environment variables ready

---

## 🔧 Backend Deployment (Google Cloud Run)

### Step 1: Prepare GCP Environment

```bash
# Install Google Cloud SDK if not already installed
# https://cloud.google.com/sdk/docs/install

# Login to GCP
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

### Step 2: Create Cloud Storage Bucket

```bash
# Create bucket for chat history
gsutil mb -l us-central1 gs://pawbondai-chat-history

# Make it private
gsutil iam ch allUsers:objectViewer gs://pawbondai-chat-history
```

### Step 3: Set Environment Variables

Create a file `backend/.env.production` with your production values:

```env
GCP_PROJECT_ID=your-project-id
VERTEX_AI_LOCATION=us-central1
GEMINI_MODEL=gemini-1.5-flash
ELASTICSEARCH_URL=https://your-elasticsearch-url:9200
ELASTICSEARCH_API_KEY=your-elasticsearch-api-key
GCS_BUCKET_NAME=pawbondai-chat-history
DEBUG=False
APP_NAME=PawBondAI
```

### Step 4: Deploy to Cloud Run

```bash
cd backend

# Deploy with environment variables
gcloud run deploy pawbondai-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT_ID \
  --set-env-vars VERTEX_AI_LOCATION=us-central1 \
  --set-env-vars GEMINI_MODEL=gemini-1.5-flash \
  --set-env-vars ELASTICSEARCH_URL=YOUR_ES_URL \
  --set-env-vars ELASTICSEARCH_API_KEY=YOUR_ES_KEY \
  --set-env-vars GCS_BUCKET_NAME=pawbondai-chat-history \
  --set-env-vars DEBUG=False \
  --set-env-vars APP_NAME=PawBondAI \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0

# Note: This will build the Docker image and deploy it
# First deployment takes 3-5 minutes
```

### Step 5: Get Backend URL

```bash
# Get the service URL
gcloud run services describe pawbondai-backend \
  --region us-central1 \
  --format 'value(status.url)'

# Example output: https://pawbondai-backend-abc123-uc.a.run.app
```

### Step 6: Test Backend

```bash
# Test health endpoint
curl https://YOUR-BACKEND-URL.run.app/api/v1/health

# Test API docs
open https://YOUR-BACKEND-URL.run.app/docs
```

### Step 7: Configure CORS (if needed)

If you need to restrict CORS origins, update `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pawbondai.netlify.app",  # Your production frontend
        "http://localhost:5173",  # Local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy:

```bash
gcloud run deploy pawbondai-backend --source .
```

---

## 🌐 Frontend Deployment (Netlify)

### Step 1: Install Netlify CLI

```bash
npm install -g netlify-cli
```

### Step 2: Login to Netlify

```bash
netlify login
# This will open a browser for authentication
```

### Step 3: Build Frontend

```bash
cd frontend

# Update .env with production backend URL
echo "VITE_API_URL=https://YOUR-BACKEND-URL.run.app/api/v1" > .env.production

# Build the app
npm run build

# Verify build output
ls -la dist/
```

### Step 4: Deploy to Netlify

```bash
# Initialize Netlify site
netlify init

# Follow prompts:
# - Create & configure a new site
# - Team: Your team
# - Site name: pawbondai (or your choice)
# - Build command: npm run build
# - Publish directory: dist

# Deploy to production
netlify deploy --prod

# Or deploy in one command:
netlify deploy --prod --dir=dist
```

### Step 5: Configure Environment Variables in Netlify

**Option A: Via Netlify CLI**

```bash
netlify env:set VITE_API_URL "https://YOUR-BACKEND-URL.run.app/api/v1"
```

**Option B: Via Netlify Dashboard**

1. Go to https://app.netlify.com/
2. Select your site
3. Go to Site settings → Environment variables
4. Add variable:
   - Key: `VITE_API_URL`
   - Value: `https://YOUR-BACKEND-URL.run.app/api/v1`
5. Trigger a new deploy

### Step 6: Get Frontend URL

Your site will be available at:
- `https://pawbondai.netlify.app` (if name is available)
- Or: `https://random-name-123.netlify.app`

### Step 7: Custom Domain (Optional)

```bash
# Add custom domain
netlify domains:add yourdomain.com

# Follow DNS configuration instructions
# Add CNAME record: www.yourdomain.com → pawbondai.netlify.app
```

---

## 🔐 Security Considerations

### Backend Security

1. **API Keys**: Never commit API keys to git
   - Use Cloud Run environment variables
   - Rotate keys regularly

2. **CORS**: Restrict allowed origins in production
   ```python
   allow_origins=["https://pawbondai.netlify.app"]
   ```

3. **Authentication**: Consider adding API authentication
   - OAuth 2.0 for user auth
   - API keys for service-to-service

4. **Rate Limiting**: Add rate limiting middleware
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

### Frontend Security

1. **Environment Variables**: Only expose public variables
   - `VITE_API_URL` is safe (public)
   - Never expose API keys in frontend

2. **Content Security Policy**: Add CSP headers in Netlify
   ```toml
   [[headers]]
     for = "/*"
     [headers.values]
       Content-Security-Policy = "default-src 'self'"
   ```

---

## 📊 Monitoring & Logging

### Backend Monitoring (Cloud Run)

```bash
# View logs
gcloud run services logs read pawbondai-backend \
  --region us-central1 \
  --limit 50

# View metrics
gcloud run services describe pawbondai-backend \
  --region us-central1 \
  --format yaml
```

### Frontend Monitoring (Netlify)

1. Go to Netlify Dashboard
2. Select your site
3. View:
   - Analytics (page views, bandwidth)
   - Deploy logs
   - Function logs (if using Netlify Functions)

### Set Up Alerts

**Cloud Run Alerts:**

```bash
# Create alert for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05
```

---

## 🔄 CI/CD Setup (Optional)

### GitHub Actions for Backend

Create `.github/workflows/deploy-backend.yml`:

```yaml
name: Deploy Backend to Cloud Run

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - id: 'auth'
        uses: 'google-github-actions/auth@v1'
        with:
          credentials_json: '${{ secrets.GCP_SA_KEY }}'
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy pawbondai-backend \
            --source ./backend \
            --region us-central1
```

### GitHub Actions for Frontend

Create `.github/workflows/deploy-frontend.yml`:

```yaml
name: Deploy Frontend to Netlify

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install and Build
        run: |
          cd frontend
          npm install
          npm run build
      
      - name: Deploy to Netlify
        uses: netlify/actions/cli@master
        with:
          args: deploy --prod --dir=frontend/dist
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

---

## 🧪 Post-Deployment Testing

### Backend Tests

```bash
# Health check
curl https://YOUR-BACKEND-URL.run.app/api/v1/health

# Test chat endpoint
curl -X POST https://YOUR-BACKEND-URL.run.app/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Find adopters with yards", "context": {}}'

# Test analytics
curl https://YOUR-BACKEND-URL.run.app/api/v1/analytics/adoption-trends
```

### Frontend Tests

1. Open https://pawbondai.netlify.app
2. Test key features:
   - [ ] Chat interface loads
   - [ ] Can send messages
   - [ ] Search results display
   - [ ] Data management page works
   - [ ] Analytics dashboard loads

---

## 🐛 Troubleshooting

### Backend Issues

**Issue**: "Service Unavailable" error
- **Solution**: Check Cloud Run logs for errors
  ```bash
  gcloud run services logs read pawbondai-backend --region us-central1
  ```

**Issue**: "Authentication failed" for Vertex AI
- **Solution**: Ensure Cloud Run service account has Vertex AI permissions
  ```bash
  gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:YOUR-SERVICE-ACCOUNT" \
    --role="roles/aiplatform.user"
  ```

**Issue**: Elasticsearch connection timeout
- **Solution**: Check Elasticsearch URL and API key in environment variables

### Frontend Issues

**Issue**: "Failed to fetch" errors
- **Solution**: Check CORS configuration in backend
- **Solution**: Verify `VITE_API_URL` environment variable

**Issue**: Build fails on Netlify
- **Solution**: Check build logs in Netlify dashboard
- **Solution**: Ensure all dependencies are in `package.json`

---

## 💰 Cost Estimation

### Google Cloud Run
- **Free tier**: 2 million requests/month
- **After free tier**: ~$0.40 per million requests
- **Estimated**: $10-50/month for moderate traffic

### Netlify
- **Free tier**: 100GB bandwidth, 300 build minutes
- **Pro plan**: $19/month for more bandwidth
- **Estimated**: Free for development, $19/month for production

### Elasticsearch Cloud
- **Free trial**: 14 days
- **Basic**: $95/month
- **Standard**: $200+/month
- **Estimated**: $95-200/month

**Total Estimated Cost**: $105-270/month

---

## 📞 Support

If you encounter issues during deployment:

1. Check logs first (Cloud Run, Netlify)
2. Review environment variables
3. Test locally before deploying
4. Open an issue on GitHub

---

**Deployment completed! 🎉**

Your PawBondAI platform is now live and helping rescue organizations worldwide!
