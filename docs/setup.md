# Setup Guide

This document provides detailed instructions for setting up the Multi-Modal Content Analytics platform in various environments.

## Prerequisites

Before installing the platform, ensure you have the following software installed:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git** (version 2.0 or higher)
- **Python** (version 3.8 or higher) - for local development
- **Node.js** (version 16 or higher) - for local development

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Optional
HUGGINGFACE_API_KEY=your_huggingface_api_key_here  # Optional
PINECONE_API_KEY=your_pinecone_api_key_here  # For Pinecone vector database

# Database Configuration
DATABASE_URL=sqlite:///./multi_modal_content.db
VECTOR_DB_URL=http://localhost:8080

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-west1-gcp-free  # or your region
PINECONE_INDEX_NAME=content-embeddings

# Application Settings
UPLOAD_FOLDER=./uploads
MAX_FILE_SIZE=52428800  # 50MB in bytes
MAX_CONCURRENT_UPLOADS=5

# Processing Settings
DEFAULT_LLM_MODEL=gpt-4-turbo
EMBEDDING_MODEL=text-embedding-ada-002
```

## Docker Setup (Recommended)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/multi-model-content-analytics.git
cd multi-model-content-analytics
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env to add your actual API keys
```

### 3. Build and start services

```bash
docker-compose up --build
```

### 4. Access the application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Vector Database: http://localhost:8080/v1

## Manual Setup (Development)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

## Kubernetes Setup

For production deployments, the platform includes Kubernetes manifests:

1. Navigate to the Kubernetes directory:
```bash
cd infra/kubernetes
```

2. Apply the manifests:
```bash
kubectl apply -f .
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Ensure ports 3000, 8000, and 8080 are available
2. **Docker build failures**: Check Docker daemon is running and you have sufficient disk space
3. **API key errors**: Verify your API keys are correctly set in the .env file
4. **File upload issues**: Check file size limits and supported formats

### Verification Steps

1. Check if all services are running:
```bash
docker-compose ps
```

2. Verify API connectivity:
```bash
curl http://localhost:8000/health
```

3. Check frontend accessibility:
```bash
curl http://localhost:3000
```

## Next Steps

After successful setup:

1. Upload your first document, image, audio, or video file
2. Perform a semantic search to test the RAG functionality
3. Try the AI-powered chat interface
4. Experiment with the agentic workflows