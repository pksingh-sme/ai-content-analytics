# Multi-Modal Content Analytics Platform

A production-ready full-stack platform for processing documents, images, audio, and video with AI-powered analytics, semantic search (RAG), and agentic multi-step workflows.

## 🚀 Features

- **Multi-Modal Processing**: Handle documents (PDF, DOCX, etc.), images (JPG, PNG, etc.), audio (MP3, WAV, etc.), and video (MP4, MOV, etc.)
- **AI-Powered Analytics**: Extract intelligence from various content types using state-of-the-art AI models
- **Vision-Language Understanding**: Advanced image analysis using BLIP-2 for captioning, question answering, and detailed descriptions
- **Advanced RAG Pipeline**: Comprehensive Retrieval Augmented Generation with Pinecone vector database
- **Semantic Search**: Vector-based search with RAG (Retrieval Augmented Generation) for contextual understanding
- **Advanced Agentic Workflows**: Multi-step AI workflows with orchestration for complex analytical tasks
- **Agent Orchestrator**: Sophisticated agent system with workflow creation, execution, and management
- **Evaluation & Reliability**: Comprehensive evaluation metrics including RAG relevance (precision/recall), hallucination detection, and confidence scoring
- **Logging & Observability**: Structured JSON logging for all operations with metrics tracking and visualization dashboard
- **Interactive Chat**: AI-powered Q&A with citations to source documents
- **Scalable Architecture**: Containerized microservices with Docker and Kubernetes support

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI/ML**: OpenAI API, Sentence Transformers, Whisper, PyTorch
- **Vector Databases**: Pinecone, Weaviate, FAISS for semantic search
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
- **RAG Pipeline Service**: Advanced Retrieval Augmented Generation with Pinecone integration
- **Agent Orchestrator Service**: Multi-step agent workflows with planning and execution capabilities
- **Evaluation Service**: RAG relevance metrics, hallucination detection, and confidence scoring
- **Logging Service**: Structured JSON logging, metrics tracking, and observability dashboard
- **Vector Database**: Pinecone for scalable semantic search capabilities

## 🔍 Logging & Observability Features

The platform includes comprehensive logging and observability features for production monitoring:

### Structured Logging

All system operations are logged using structured JSON format with rich contextual information:

#### Core Logging Categories
- **File Upload Operations**: Filename, size, content type, upload duration, user ID
- **RAG Queries**: Query text, top-k parameter, results count, response time, user ID
- **Agent Workflows**: Workflow ID, steps executed, execution time, status, user ID
- **API Requests**: HTTP method, endpoint, status code, response time, user ID
- **Error Tracking**: Error type, message, context, stack trace, user ID

#### Structured Log Format
```json
{
  "timestamp": "2024-01-06T15:30:45.123456Z",
  "level": "INFO",
  "logger": "rag_query",
  "message": "RAG query executed: What is machine learning?",
  "event_type": "rag_query",
  "query": "What is machine learning?",
  "top_k": 5,
  "results_count": 3,
  "response_time": 1.245,
  "user_id": "user_123",
  "operation": "query"
}
```

### Metrics Tracking

Automatic collection and tracking of key performance indicators:

#### Core Metrics
- **Query Processing**: Total queries, average response time, response time percentiles (50th, 90th, 95th, 99th)
- **Throughput**: Requests per second, successful vs failed requests
- **Resource Utilization**: Active users, peak concurrent users, processing time
- **Error Analysis**: Error counts by type, failure rates by endpoint
- **Operation Counts**: File uploads, RAG retrievals, agent workflows, API requests

#### Advanced Metrics
- **Endpoint Performance**: Per-endpoint success rates, response times, request volumes
- **User Analytics**: Active user tracking, concurrent user peaks
- **Historical Trends**: Request history with timestamps and metadata
- **Performance Percentiles**: Detailed response time distributions

### Real-time Dashboard

A comprehensive Streamlit dashboard provides real-time visualization at `dashboard/observability_dashboard.py`:

#### Dashboard Features
- **Overview Tab**: Key metrics summary, response time percentiles, operation distribution
- **Performance Metrics**: Processing times, concurrency tracking, success/failure rates
- **Error Analysis**: Error type breakdown, recent error logs, failure patterns
- **Endpoint Metrics**: Per-endpoint performance, success rates, response time analysis

#### Dashboard Requirements
```bash
cd dashboard
pip install -r requirements.txt
streamlit run observability_dashboard.py
```

### Logging API Endpoints

#### Core Logging Endpoints
- `GET /api/v1/logging/metrics` - Basic metrics summary
- `GET /api/v1/logging/metrics/detailed` - Comprehensive metrics with percentiles
- `GET /api/v1/logging/metrics/history` - Recent metrics history (last 100 entries)
- `GET /api/v1/logging/metrics/performance` - Performance-specific metrics
- `GET /api/v1/logging/metrics/endpoints` - Per-endpoint metrics breakdown
- `GET /api/v1/logging/metrics/errors` - Error metrics and type analysis
- `GET /api/v1/logging/health` - System health check
- `DELETE /api/v1/logging/metrics/reset` - Reset all metrics (admin only)

#### Example API Usage

```bash
# Get detailed metrics with percentiles
curl "http://localhost:8000/api/v1/logging/metrics/detailed"

# Get performance metrics
curl "http://localhost:8000/api/v1/logging/metrics/performance"

# Get endpoint-specific metrics
curl "http://localhost:8000/api/v1/logging/metrics/endpoints"

# Check system health
curl "http://localhost:8000/api/v1/logging/health"
```

### Python Integration Examples

#### Using Structured Logging Functions
```python
from backend.logging import (
    log_file_upload,
    log_rag_query,
    log_agent_workflow,
    log_error,
    log_api_request
)

# Log file upload
log_file_upload(
    filename="document.pdf",
    file_size=1024000,
    content_type="application/pdf",
    user_id="user_123",
    duration=2.5
)

# Log RAG query
log_rag_query(
    query="Explain quantum computing",
    top_k=5,
    results_count=3,
    response_time=1.8,
    user_id="user_123"
)

# Log agent workflow
log_agent_workflow(
    workflow_id="wf_001",
    steps=[{"step_id": "step_1"}, {"step_id": "step_2"}],
    execution_time=15.2,
    status="completed",
    user_id="user_123"
)

# Log error
log_error(
    error_type="ValueError",
    error_message="Invalid input parameter provided",
    context={"parameter": "query", "value": ""},
    user_id="user_123"
)

# Log API request
log_api_request(
    method="POST",
    url="/api/v1/query",
    status_code=200,
    response_time=1.2,
    user_id="user_123"
)
```

#### Accessing Metrics Programmatically
```python
from backend.logging.metrics import metrics_tracker

# Get metrics summary
metrics = metrics_tracker.get_metrics_summary()
print(f"Average response time: {metrics['average_response_time']}s")
print(f"Success rate: {metrics['success_rate']}%")

# Get response time percentiles
percentiles = metrics_tracker.get_response_time_percentiles()
print(f"95th percentile: {percentiles['p95']}s")

# Log custom metrics
metrics_tracker.log_query(
    query="Sample query",
    response_time=1.5,
    user_id="user_123"
)
```

### Log Storage and Management

#### Log File Structure
```
logs/
├── app_20240106.log          # Main application logs (JSON format)
├── metrics.json              # Persistent metrics storage
└── archived/
    └── app_20240105.log      # Archived logs
```

#### Log Rotation
- Daily log file rotation
- JSON format for easy parsing and analysis
- Automatic cleanup of old archived logs
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Monitoring Best Practices

1. **Production Monitoring**:
   - Enable INFO level logging for operational monitoring
   - Set up log aggregation (ELK stack, Splunk, etc.)
   - Configure alerts for error spikes and performance degradation

2. **Development Debugging**:
   - Use DEBUG level for detailed troubleshooting
   - Enable console logging for immediate feedback
   - Monitor specific loggers for targeted debugging

3. **Performance Optimization**:
   - Regularly review response time percentiles
   - Monitor endpoint performance trends
   - Track user concurrency patterns

4. **Security Auditing**:
   - Log all authentication and authorization events
   - Track file access patterns
   - Monitor for unusual activity patterns

## 📊 Evaluation & Reliability Features

The platform includes comprehensive evaluation and reliability features for monitoring AI system performance:

### Core Evaluation Capabilities

#### RAG Relevance Metrics
- **Precision**: Proportion of retrieved documents that are relevant
- **Recall**: Proportion of relevant documents that were retrieved
- **F1-Score**: Harmonic mean of precision and recall
- **MRR (Mean Reciprocal Rank)**: Ranking quality metric
- **NDCG (Normalized Discounted Cumulative Gain)**: Ranking effectiveness
- **Average Relevance Score**: Overall document relevance assessment
- **Quality Level Assessment**: Categorical quality ratings (excellent/good/fair/poor)

#### Hallucination Detection
- **Hallucination Score**: Quantified hallucination risk (0-1 scale)
- **Factuality Assessment**: Verification of factual claims against source documents
- **Contradiction Detection**: Identification of contradictory statements
- **Sentence-Level Analysis**: Per-sentence support verification
- **Confidence Scoring**: Confidence metrics for each response
- **Factual Claim Identification**: Automatic detection of factual assertions

#### Advanced Monitoring
- **Real-time Alerting**: Automated alerts for performance degradation
- **Health Scoring**: Overall system health metrics
- **Performance Trends**: Historical performance analysis
- **Threshold-Based Monitoring**: Configurable alert thresholds
- **Multi-dimensional Evaluation**: Comprehensive assessment framework

### Evaluation API Endpoints

#### Core Evaluation Endpoints
- `POST /api/v1/evaluation/rag` - Full RAG pipeline evaluation with comprehensive metrics
- `POST /api/v1/evaluation/rag-relevance` - Detailed RAG relevance analysis
- `POST /api/v1/evaluation/hallucination` - Advanced hallucination detection
- `GET /api/v1/evaluation/summary` - Aggregated evaluation metrics and health summary
- `GET /api/v1/evaluation/logs` - Detailed evaluation logs and history
- `GET /api/v1/evaluation/trends` - Performance trends over time

#### Example API Usage

```bash
# Evaluate full RAG pipeline
curl -X POST "http://localhost:8000/api/v1/evaluation/rag" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is machine learning?", "top_k": 5}'

# Check hallucination in LLM response
curl -X POST "http://localhost:8000/api/v1/evaluation/hallucination" \
  -H "Content-Type: application/json" \
  -d '{
    "response": "Machine learning was invented in 1950 by Alan Turing",
    "retrieved_docs": [...]
  }'

# Get evaluation summary
curl "http://localhost:8000/api/v1/evaluation/summary"
```

### Jupyter Notebook Analysis Tools

The platform includes comprehensive Jupyter notebooks for evaluation analysis:

#### `notebooks/evaluation/rag_evaluation_demo.ipynb`
- Complete RAG pipeline evaluation workflow
- Performance metrics visualization
- Statistical analysis of evaluation results
- System health dashboard generation
- Export capabilities for reports and data

#### `notebooks/evaluation/hallucination_detection_analysis.ipynb`
- Advanced hallucination detection analysis
- False positive/negative evaluation
- Detection accuracy metrics
- Threshold optimization recommendations
- Detailed scenario-based testing

### Evaluation Metrics Reference

#### RAG Metrics Interpretation
| Metric | Good Range | Warning Range | Critical Range |
|--------|------------|---------------|----------------|
| Precision | ≥ 0.8 | 0.6-0.8 | < 0.6 |
| Recall | ≥ 0.8 | 0.6-0.8 | < 0.6 |
| F1-Score | ≥ 0.8 | 0.6-0.8 | < 0.6 |
| Avg Relevance | ≥ 0.7 | 0.5-0.7 | < 0.5 |

#### Hallucination Metrics Interpretation
| Metric | Good Range | Warning Range | Critical Range |
|--------|------------|---------------|----------------|
| Hallucination Score | ≤ 0.1 | 0.1-0.3 | > 0.3 |
| Factuality Score | ≥ 0.9 | 0.7-0.9 | < 0.7 |
| Confidence | ≥ 0.8 | 0.6-0.8 | < 0.6 |
| Contradiction Score | ≤ 0.05 | 0.05-0.15 | > 0.15 |

### Alert System

The evaluation system generates automated alerts for:
- **Low Precision/Recall**: Poor retrieval quality
- **High Hallucination Risk**: Unreliable responses
- **Low Confidence**: Uncertain predictions
- **Contradictions Detected**: Conflicting information
- **Performance Degradation**: Trend-based alerts
- **High Alert Volume**: System instability indicators

### Integration Examples

#### Python Client Integration
```python
from backend.evaluation.evaluation_service import evaluation_service

# Evaluate RAG performance
rag_metrics = await evaluation_service.evaluate_rag_relevance(
    query="Your query here",
    retrieved_docs=document_list,
    top_k=5
)

# Detect hallucinations
hallucination_metrics = await evaluation_service.detect_hallucination(
    response="LLM response here",
    retrieved_docs=document_list
)

# Log evaluation results
log_id = await evaluation_service.log_evaluation_metrics(
    query=query,
    response=response,
    retrieved_docs=document_list,
    rag_metrics=rag_metrics,
    hallucination_metrics=hallucination_metrics
)
```

#### Continuous Monitoring Setup
```python
# Configure alert thresholds
evaluation_service.alert_thresholds.update({
    'hallucination_score': 0.2,  # Stricter threshold
    'low_precision': 0.7,        # Higher precision requirement
    'low_confidence': 0.8        # Higher confidence requirement
})

# Get performance trends
trends = evaluation_service.get_performance_trends(hours=24)

# Generate health report
summary = evaluation_service.get_evaluation_summary()
```

### Best Practices

1. **Regular Evaluation**: Run evaluations on production queries periodically
2. **Threshold Tuning**: Adjust alert thresholds based on your use case
3. **Ground Truth Maintenance**: Keep ground truth datasets updated for accurate evaluation
4. **Performance Baseline**: Establish baseline metrics for anomaly detection
5. **Human Validation**: Use human reviewers for critical high-risk detections
6. **Continuous Improvement**: Regularly review false positives/negatives to improve detection

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.8+
- Node.js 16+

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/pksingh-sme/ai-content-analytics.git
cd multi-model-content-analytics
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env to add your API keys
```

3. Configure your `.env` file with appropriate values:
   - `OPENAI_API_KEY`: Your OpenAI API key for LLM functionality
   - `PINECONE_API_KEY`: Your Pinecone API key for vector database
   - `HUGGINGFACE_API_KEY`: Your Hugging Face API key (if using Hugging Face models)
   - Adjust other settings as needed (database URLs, file storage, etc.)

### Local Development

1. Start the services:
```bash
docker-compose up --build
```

2. Access the application:
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
│   │   ├── evaluation/     # Evaluation API endpoints
│   │   └── logging/        # Logging API endpoints
│   ├── evaluation/         # Evaluation services
│   │   ├── __init__.py
│   │   ├── api.py          # Evaluation REST API
│   │   └── evaluation_service.py  # Core evaluation logic
│   ├── logging/            # Logging and metrics services
│   │   ├── __init__.py     # Structured logging functions
│   │   ├── api.py          # Logging REST API
│   │   └── metrics.py      # Metrics tracking service
│   ├── models/             # Pydantic models
│   ├── services/           # Business logic
│   ├── utils/              # Utility functions
│   └── config/             # Configuration
├── frontend/               # React frontend
│   ├── src/                # Source code
│   ├── components/         # React components
│   ├── public/             # Static assets
│   └── utils/              # Utility functions
├── dashboard/              # Observability dashboard
│   ├── observability_dashboard.py  # Streamlit dashboard
│   └── requirements.txt    # Dashboard dependencies
├── notebooks/              # Jupyter notebooks
│   └── evaluation/         # Evaluation analysis notebooks
│       ├── rag_evaluation_demo.ipynb
│       └── hallucination_detection_analysis.ipynb
├── infra/                  # Infrastructure files
│   ├── docker/             # Docker configurations
│   ├── kubernetes/         # Kubernetes manifests
│   └── terraform/          # Infrastructure as code
├── logs/                   # Log storage directory
│   ├── app_20240106.log    # Current day logs
│   ├── metrics.json        # Metrics persistence
│   └── archived/           # Archived logs
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