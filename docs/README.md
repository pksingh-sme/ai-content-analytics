# Multi-Modal Content Analytics Platform

A production-ready full-stack platform for processing documents, images, audio, and video with AI-powered analytics, semantic search (RAG), and agentic multi-step workflows.

## 🚀 Features

- **Multi-Modal Processing**: Handle documents (PDF, DOCX, etc.), images (JPG, PNG, etc.), audio (MP3, WAV, etc.), and video (MP4, MOV, etc.)
- **AI-Powered Analytics**: Extract intelligence from various content types using state-of-the-art AI models
- **Vision-Language Understanding**: Advanced image analysis using BLIP-2 for captioning, question answering, and detailed descriptions
- **Semantic Search**: Vector-based search with RAG (Retrieval Augmented Generation) for contextual understanding
- **Agentic Workflows**: Multi-step AI workflows for complex analytical tasks
- **Interactive Chat**: AI-powered Q&A with citations to source documents
- **Scalable Architecture**: Containerized microservices with Docker and Kubernetes support

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI/ML**: OpenAI API, Sentence Transformers, Whisper, PyTorch
- **Database**: SQLite (default), with support for Weaviate vector database
- **Processing**: PyPDF2, pytesseract, pdf2image, OpenCV, MoviePy

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: styled-components
- **UI Components**: Custom-built components with responsive design
- **File Upload**: react-dropzone for drag-and-drop functionality

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Deployment**: Kubernetes-ready configuration
- **Load Balancing**: NGINX
- **Monitoring**: Ready for integration with Prometheus/Grafana

## 📊 System Architecture

The platform follows a microservices architecture with clear separation of concerns:

```
Client Layer -> API Gateway -> Service Layer -> AI/ML Layer -> Data Layer
```

Key components:
- **Upload Service**: Handles file ingestion and initial processing
- **Processing Service**: Content extraction and transformation
- **Query Service**: Semantic search and RAG implementation
- **Agent Service**: Multi-step workflow orchestration
- **BLIP-2 Service**: Vision-language understanding for image analysis
- **Vector Database**: For semantic search capabilities

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.8+
- Node.js 16+

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/your-username/multi-model-content-analytics.git
cd multi-model-content-analytics
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env to add your API keys
```

3. Start the services:
```bash
docker-compose up --build
```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - BLIP-2 Image Analysis: http://localhost:8000/api/v1/blip2/image

### Manual Setup

1. Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

2. Frontend:
```bash
cd frontend
npm install
npm start
```

## 📁 Project Structure

```
multi-model-content-analytics/
├── backend/                 # FastAPI backend
│   ├── api/                # API routes
│   ├── models/             # Pydantic models
│   ├── services/           # Business logic
│   ├── utils/              # Utility functions
│   └── config/             # Configuration
├── frontend/               # React frontend
│   ├── src/                # Source code
│   ├── components/         # React components
│   ├── public/             # Static assets
│   └── utils/              # Utility functions
├── infra/                  # Infrastructure files
│   ├── docker/             # Docker configurations
│   ├── kubernetes/         # Kubernetes manifests
│   └── terraform/          # Infrastructure as code
├── notebooks/              # Experiment notebooks
├── architecture/           # Architecture diagrams
└── docs/                   # Documentation
```

## 🔐 Security Considerations

- API key management through environment variables
- Input validation and sanitization
- Rate limiting to prevent abuse
- File type and size restrictions
- Secure file upload handling
- HTTPS in production deployments

## 📈 Scaling & Production Deployment

The platform is designed for production deployment with:

- Containerized services for easy scaling
- Health check endpoints
- Configuration management
- Monitoring and logging ready
- Database connection pooling
- Caching strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please open an issue in the GitHub repository.