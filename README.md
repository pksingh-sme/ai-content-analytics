# AI Content Analytics Platform

A comprehensive multi-modal content analytics platform built with FastAPI and React, featuring AI-powered document processing, semantic search, and RAG (Retrieval Augmented Generation) capabilities.

## 🚀 Quick Start

### Automated Setup (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd ai-content-analytics

# Run the quick start script
python quick_start.py
```

### Manual Setup
Follow the detailed steps in [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)

## 🎯 Key Features

### ✅ Core Functionality
- **Multi-modal Processing**: Documents, images, audio, and video
- **Semantic Search**: AI-powered content discovery
- **RAG Pipeline**: Retrieval Augmented Generation for intelligent Q&A
- **Llama Embeddings**: Optimized llama-text-embed-v2 (1024 dimensions)

### ✅ Advanced Capabilities
- **Evaluation Metrics**: Precision, recall, F1-score, MRR, NDCG
- **Hallucination Detection**: Sentence-level factuality analysis
- **Structured Logging**: JSON-formatted observability
- **Real-time Monitoring**: Performance metrics dashboard

### ✅ Developer Experience
- **Modern Stack**: FastAPI + React + TypeScript
- **Professional Structure**: Well-organized codebase
- **Docker Support**: Containerized deployment
- **Comprehensive Testing**: Unit and integration tests

## 🏗️ Architecture Overview

```
ai-content-analytics/
├── backend/           # FastAPI backend services
│   ├── api/          # REST API endpoints
│   ├── config/       # Configuration management
│   ├── evaluation/   # RAG metrics and evaluation
│   ├── logging/      # Structured logging system
│   ├── models/       # Pydantic data models
│   ├── services/     # Business logic services
│   └── utils/        # Utility functions
├── frontend/         # React frontend application
├── infra/           # Infrastructure and deployment
└── docs/            # Documentation
```

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Environment Variables
Copy `.env.example` to `.env` and configure:
```env
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
EMBEDDING_MODEL=llama-text-embed-v2
EMBEDDING_DIMENSION=1024
```

### Running the Application

**Backend:**
```bash
cd backend
python run_backend.py
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

**Frontend:**
```bash
cd frontend
npm start
# App available at http://localhost:3000
```

## 📊 API Endpoints

### Core Endpoints
- `POST /api/v1/upload` - Upload content files
- `POST /api/v1/query` - Semantic search and Q&A
- `GET /api/v1/metadata/{file_id}` - Get file metadata
- `GET /api/v1/search` - Content search

### Advanced Endpoints
- `POST /api/v1/evaluation/metrics` - RAG performance metrics
- `POST /api/v1/evaluation/hallucination` - Hallucination detection
- `GET /api/v1/logging/metrics` - System metrics
- `GET /api/v1/health` - Health check

## 🧪 Testing

```bash
# Backend functionality test
python test_backend_functionality.py

# Run specific tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

## 🚢 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Cloud Deployment
The application is ready for deployment to:
- **AWS**: ECS, Lambda, or EC2
- **Google Cloud**: Cloud Run or Compute Engine
- **Azure**: App Service or Container Instances

## 📈 Monitoring and Observability

- **Structured Logging**: JSON-formatted logs for easy parsing
- **Metrics Dashboard**: Real-time performance monitoring
- **Health Checks**: Automated system health monitoring
- **Error Tracking**: Comprehensive error logging and alerting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📚 Documentation

- [Development Guide](DEVELOPMENT_GUIDE.md) - Complete step-by-step development instructions
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)
- [Architecture Diagrams](architecture/) - System architecture visuals
- [Deployment Guide](docs/deployment.md) - Production deployment instructions

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
- Check the [Documentation](docs/)
- Review [Common Issues](docs/troubleshooting.md)
- Open a GitHub issue

---

**Ready to build the next generation of AI-powered content analytics?** 🚀