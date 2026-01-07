# Evaluation Quickstart Guide

This guide provides a quick introduction to using the evaluation and reliability features of the AI Content Analytics platform.

## Quick Setup

1. **Install notebook dependencies:**
```bash
cd notebooks
pip install -r requirements.txt
```

2. **Start Jupyter:**
```bash
jupyter notebook
```

## Running Evaluations

### 1. Basic RAG Evaluation
Open `notebooks/evaluation/rag_evaluation_demo.ipynb` to:
- Upload sample documents
- Test RAG pipeline with various queries  
- Generate performance metrics and visualizations
- Export results for analysis

### 2. Hallucination Detection Analysis
Open `notebooks/evaluation/hallucination_detection_analysis.ipynb` to:
- Test hallucination detection capabilities
- Analyze false positive/negative rates
- Optimize detection thresholds
- Generate detailed performance reports

## API Usage Examples

### Evaluate RAG Performance
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/evaluation/rag",
    json={
        "query": "What are the impacts of climate change?",
        "top_k": 5
    }
)
metrics = response.json()
print(f"Precision: {metrics['rag_metrics']['precision']}")
print(f"Hallucination Score: {metrics['hallucination_metrics']['hallucination_score']}")
```

### Check for Hallucinations
```python
response = requests.post(
    "http://localhost:8000/api/v1/evaluation/hallucination",
    json={
        "response": "The Earth is flat and climate change is a hoax",
        "retrieved_docs": [...]  # Your retrieved documents
    }
)
hallucination_result = response.json()
print(f"Hallucination Risk: {hallucination_result['hallucination_score']}")
print(f"Alerts: {hallucination_result['alerts']}")
```

## Key Metrics to Monitor

### RAG Performance Indicators
- **Precision ≥ 0.8**: Good retrieval quality
- **Recall ≥ 0.8**: Good coverage of relevant documents
- **F1-Score ≥ 0.8**: Balanced performance

### Hallucination Risk Indicators
- **Hallucination Score ≤ 0.1**: Low risk
- **Factuality Score ≥ 0.9**: High factual accuracy
- **Confidence ≥ 0.8**: Reliable responses

## Alert Thresholds

Default alert thresholds can be adjusted:
```python
# In evaluation_service.py or via API
evaluation_service.alert_thresholds = {
    'hallucination_score': 0.3,    # Trigger alert if > 30%
    'low_precision': 0.5,          # Alert for precision < 50%
    'low_recall': 0.5,             # Alert for recall < 50%
    'low_confidence': 0.7          # Alert for confidence < 70%
}
```

## Best Practices

1. **Regular Monitoring**: Run evaluations weekly on production queries
2. **Baseline Establishment**: Capture metrics during normal operation
3. **Threshold Calibration**: Adjust based on your specific use case
4. **Human Review**: Validate high-risk detections manually
5. **Continuous Improvement**: Use false positive/negative analysis to refine detection

## Troubleshooting

### Common Issues

**High Hallucination Scores:**
- Check if retrieved documents are relevant to the query
- Verify document quality and completeness
- Consider expanding the document corpus

**Low Precision/Recall:**
- Review embedding quality and similarity thresholds
- Check if documents contain relevant information
- Consider retraining with better ground truth data

**Excessive Alerts:**
- Review and adjust alert thresholds
- Check for systematic issues in document processing
- Validate that thresholds match your risk tolerance

### Getting Help

- Check the detailed documentation in `docs/README.md`
- Review example notebooks for implementation patterns
- Examine evaluation logs for detailed error information