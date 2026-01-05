# Deployment Guide

This document provides instructions for deploying the Multi-Modal Content Analytics platform to various environments.

## Production Deployment Overview

The platform is designed for containerized deployment with Docker and supports multiple deployment strategies:

- Single server deployment with Docker Compose
- Container orchestration with Kubernetes
- Cloud deployment (AWS, GCP, Azure)
- Edge deployment for privacy-sensitive environments

## Docker Compose Deployment

### Prerequisites

- Docker Engine (20.10+)
- Docker Compose (2.0+)
- At least 8GB RAM and 50GB disk space
- SSL certificate for HTTPS (recommended)

### Configuration

1. Create a production environment file:

```bash
# .env.production
OPENAI_API_KEY=your_production_api_key
DATABASE_URL=postgresql://user:password@db:5432/multi_modal_content
VECTOR_DB_URL=http://vector-db:8080
UPLOAD_FOLDER=/app/uploads
MAX_FILE_SIZE=104857600  # 100MB
DEFAULT_LLM_MODEL=gpt-4-turbo
EMBEDDING_MODEL=text-embedding-ada-002
```

2. Update docker-compose.yml for production:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ../
      dockerfile: infra/docker/Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - VECTOR_DB_URL=${VECTOR_DB_URL}
    depends_on:
      - vector-db
      - postgres-db
    restart: unless-stopped
    # Add health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ../
      dockerfile: infra/docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=https://your-domain.com/api
    depends_on:
      - backend
    restart: unless-stopped

  postgres-db:
    image: postgres:15
    environment:
      POSTGRES_DB: multi_modal_content
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  vector-db:
    image: semitechnologies/weaviate:1.22.5
    environment:
      - QUERY_DEFAULTS_LIMIT=25
      - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=false
      - AUTHENTICATION_APIKEY_ENABLED=true
      - AUTHENTICATION_APIKEY_USERS=your-username@your-domain.com
      - PERSISTENCE_DATA_PATH=/var/lib/weaviate
      - DEFAULT_VECTORIZER_MODULE=text2vec-transformers
      - TRANSFORMERS_INFERENCE_API=http://t2v-transformers:8080
      - ENABLE_MODULES=backup-filesystem,generative-openai,qna-openai
      - BACKUP_FILESYSTEM_PATH=/tmp/backups
    volumes:
      - weaviate_data:/var/lib/weaviate
    restart: unless-stopped

volumes:
  postgres_data:
  weaviate_data:
```

### Deployment Steps

1. Transfer files to your server:
```bash
scp -r multi-model-content-analytics user@your-server:/opt/
```

2. Navigate to the project directory:
```bash
cd /opt/multi-model-content-analytics
```

3. Set up environment:
```bash
cp .env.production .env
# Edit .env to include your actual production values
```

4. Start the services:
```bash
docker-compose -f docker-compose.yml up -d
```

5. Verify the deployment:
```bash
docker-compose ps
docker-compose logs backend
docker-compose logs frontend
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (v1.20+)
- kubectl configured
- Helm (optional, for easier deployment)

### Configuration

Create Kubernetes manifests in `infra/kubernetes/`:

**namespace.yaml**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: multi-modal-content-analytics
```

**secrets.yaml**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: multi-modal-content-analytics
type: Opaque
data:
  openai-api-key: <base64-encoded-api-key>
  postgres-password: <base64-encoded-password>
```

**deployment.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: multi-modal-content-analytics
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/multi-modal-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: openai-api-key
        - name: DATABASE_URL
          value: "postgresql://user:$(POSTGRES_PASSWORD)@postgres:5432/multi_modal_content"
        envFrom:
        - secretRef:
            name: app-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Deployment Steps

1. Apply the Kubernetes manifests:
```bash
kubectl apply -f infra/kubernetes/
```

2. Verify the deployment:
```bash
kubectl get pods -n multi-modal-content-analytics
kubectl get services -n multi-modal-content-analytics
kubectl logs -f deployment/backend -n multi-modal-content-analytics
```

## Cloud Deployment

### AWS Deployment

1. Use AWS ECS for container orchestration
2. Use RDS for PostgreSQL database
3. Use Elastic File System for persistent storage
4. Use Application Load Balancer for traffic distribution

### GCP Deployment

1. Use Google Cloud Run for container deployment
2. Use Cloud SQL for database
3. Use Cloud Storage for file storage
4. Use Cloud Load Balancing for traffic management

### Azure Deployment

1. Use Azure Container Instances or AKS
2. Use Azure Database for PostgreSQL
3. Use Azure Blob Storage for file storage
4. Use Azure Application Gateway for load balancing

## Monitoring and Logging

### Setup Monitoring

1. Add Prometheus metrics endpoint to the backend
2. Configure logging to structured formats
3. Set up alerts for key metrics

### Key Metrics to Monitor

- API response times
- Error rates
- File processing times
- Vector database performance
- Resource utilization

## Security Considerations

### Network Security

- Use HTTPS with valid SSL certificates
- Implement API rate limiting
- Use firewall rules to restrict access
- Implement proper authentication/authorization

### Data Security

- Encrypt data at rest and in transit
- Regular security audits
- Secure API key management
- Regular backups with encryption

## Backup and Recovery

### Database Backup

```bash
# PostgreSQL backup
pg_dump -h postgres -U user -d multi_modal_content > backup.sql

# Weaviate backup
curl -X POST http://vector-db:8080/v1/backups/filesystem/create \
  -H "Content-Type: application/json" \
  -d '{
    "id": "backup-'$(date +%Y%m%d-%H%M%S)'",
    "config": {
      "filesystemConfig": {
        "path": "/tmp/backups"
      }
    }
  }'
```

### File Backup

Regularly backup the uploads directory and vector database storage.

## Scaling Guidelines

### Horizontal Scaling

- Scale backend services based on API load
- Scale vector database independently if needed
- Use load balancers for traffic distribution

### Vertical Scaling

- Increase container resources for heavy processing
- Upgrade database hardware for better performance
- Add more storage for growing content library

## Troubleshooting

### Common Issues

1. **High Memory Usage**: Increase container memory limits
2. **Slow Processing**: Optimize file processing pipeline
3. **Database Connection Issues**: Check connection pooling
4. **API Rate Limits**: Implement retry logic and backoff strategies