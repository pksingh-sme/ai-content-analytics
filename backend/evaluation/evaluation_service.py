import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import json
from collections import defaultdict
from ..utils.embeddings import semantic_search
from ..utils.llm_client import get_llm_response
from ..services.pinecone_service import pinecone_service

logger = logging.getLogger(__name__)

class EvaluationService:
    def __init__(self):
        self.metrics_log = []
        self.evaluation_history = []
        self.alert_thresholds = {
            'hallucination_score': 0.3,
            'low_precision': 0.5,
            'low_recall': 0.5,
            'low_confidence': 0.7
        }
    
    async def evaluate_rag_relevance(
        self, 
        query: str, 
        retrieved_docs: List[Dict[str, Any]], 
        top_k: int = 5,
        ground_truth: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Enhanced RAG retrieval relevance evaluation with multiple metrics
        """
        query_lower = query.lower()
        query_keywords = set(query_lower.split())
        
        relevant_retrieved = 0
        total_retrieved = len(retrieved_docs)
        
        # Enhanced relevance checking
        relevance_scores = []
        for i, doc in enumerate(retrieved_docs):
            doc_content = doc.get('content', '').lower()
            doc_keywords = set(doc_content.split())
            
            # Multiple relevance signals
            keyword_overlap = len(query_keywords.intersection(doc_keywords))
            semantic_similarity = self._calculate_semantic_similarity(query_lower, doc_content)
            position_bonus = 1.0 / (i + 1)  # Higher score for top-ranked documents
            
            # Combined relevance score (0-1)
            relevance_score = (
                0.4 * (keyword_overlap / len(query_keywords) if query_keywords else 0) +
                0.4 * semantic_similarity +
                0.2 * position_bonus
            )
            relevance_scores.append(relevance_score)
            
            # Consider relevant if score exceeds threshold
            if relevance_score > 0.3:
                relevant_retrieved += 1
        
        # Core metrics
        precision = relevant_retrieved / total_retrieved if total_retrieved > 0 else 0
        recall = relevant_retrieved / top_k if top_k > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Additional metrics
        avg_relevance_score = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        mrr_score = self._calculate_mrr(relevance_scores)
        ndcg_score = self._calculate_ndcg(relevance_scores, ground_truth)
        
        # Quality assessment
        quality_level = self._assess_quality(precision, recall, avg_relevance_score)
        alerts = self._generate_rag_alerts(precision, recall, quality_level)
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'mrr_score': mrr_score,
            'ndcg_score': ndcg_score,
            'avg_relevance_score': avg_relevance_score,
            'relevant_retrieved': relevant_retrieved,
            'total_retrieved': total_retrieved,
            'quality_level': quality_level,
            'alerts': alerts,
            'relevance_scores': relevance_scores[:5],  # Top 5 scores
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def detect_hallucination(
        self, 
        response: str, 
        retrieved_docs: List[Dict[str, Any]],
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enhanced hallucination detection with multiple analysis techniques
        """
        if not response.strip():
            return {
                'hallucination_score': 0,
                'supported_sentences': 0,
                'total_sentences': 0,
                'confidence': 1.0,
                'factuality_score': 1.0,
                'contradiction_score': 0,
                'alerts': [],
                'analysis_details': {}
            }
        
        # Parse response into sentences
        sentences = self._parse_sentences(response)
        total_sentences = len(sentences)
        supported_sentences = 0
        contradiction_count = 0
        fact_claims = []
        
        # Analyze each sentence
        sentence_analysis = []
        for i, sentence in enumerate(sentences):
            analysis = self._analyze_sentence_support(sentence, retrieved_docs, query)
            sentence_analysis.append(analysis)
            
            if analysis['is_supported']:
                supported_sentences += 1
            if analysis['contradicts_source']:
                contradiction_count += 1
            if analysis['contains_factual_claim']:
                fact_claims.append(analysis)
        
        # Calculate scores
        hallucination_score = (total_sentences - supported_sentences) / total_sentences if total_sentences > 0 else 0
        factuality_score = supported_sentences / total_sentences if total_sentences > 0 else 1.0
        contradiction_score = contradiction_count / total_sentences if total_sentences > 0 else 0
        confidence = 1.0 - hallucination_score
        
        # Generate alerts
        alerts = self._generate_hallucination_alerts(
            hallucination_score, 
            contradiction_score, 
            confidence,
            fact_claims
        )
        
        return {
            'hallucination_score': hallucination_score,
            'supported_sentences': supported_sentences,
            'total_sentences': total_sentences,
            'confidence': confidence,
            'factuality_score': factuality_score,
            'contradiction_score': contradiction_score,
            'contradiction_count': contradiction_count,
            'alerts': alerts,
            'analysis_details': {
                'sentence_analysis': sentence_analysis[:5],  # Top 5 analyses
                'fact_claims_count': len(fact_claims),
                'support_ratio': f"{supported_sentences}/{total_sentences}"
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts (placeholder)"""
        # In a real implementation, this would use embedding similarity
        words1 = set(text1.split())
        words2 = set(text2.split())
        if not words1 or not words2:
            return 0.0
        return len(words1.intersection(words2)) / len(words1.union(words2))
    
    def _calculate_mrr(self, relevance_scores: List[float]) -> float:
        """Calculate Mean Reciprocal Rank"""
        for i, score in enumerate(relevance_scores):
            if score > 0.3:  # Threshold for relevant
                return 1.0 / (i + 1)
        return 0.0
    
    def _calculate_ndcg(self, relevance_scores: List[float], ground_truth: Optional[List[str]] = None) -> float:
        """Calculate Normalized Discounted Cumulative Gain"""
        if not relevance_scores:
            return 0.0
        
        # Simplified NDCG calculation
        dcg = sum(score / (i + 1) for i, score in enumerate(relevance_scores))
        idcg = sum(1.0 / (i + 1) for i in range(len(relevance_scores)))
        return dcg / idcg if idcg > 0 else 0.0
    
    def _assess_quality(self, precision: float, recall: float, avg_relevance: float) -> str:
        """Assess overall quality level"""
        if precision >= 0.8 and recall >= 0.8 and avg_relevance >= 0.7:
            return "excellent"
        elif precision >= 0.6 and recall >= 0.6 and avg_relevance >= 0.5:
            return "good"
        elif precision >= 0.4 and recall >= 0.4:
            return "fair"
        else:
            return "poor"
    
    def _generate_rag_alerts(self, precision: float, recall: float, quality_level: str) -> List[str]:
        """Generate alerts based on RAG performance"""
        alerts = []
        if precision < self.alert_thresholds['low_precision']:
            alerts.append(f"Low precision ({precision:.2f}) - retrieved documents may not be relevant")
        if recall < self.alert_thresholds['low_recall']:
            alerts.append(f"Low recall ({recall:.2f}) - relevant documents may be missing")
        if quality_level in ['fair', 'poor']:
            alerts.append(f"Overall quality is {quality_level}")
        return alerts
    
    def _parse_sentences(self, text: str) -> List[str]:
        """Enhanced sentence parsing"""
        # Split by sentence endings and clean
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        return sentences
    
    def _analyze_sentence_support(self, sentence: str, docs: List[Dict], query: Optional[str] = None) -> Dict[str, Any]:
        """Analyze if a sentence is supported by documents"""
        sentence_lower = sentence.lower()
        is_supported = False
        contradicts_source = False
        contains_factual_claim = self._contains_factual_claim(sentence)
        
        # Check support in documents
        max_similarity = 0
        for doc in docs:
            doc_content = doc.get('content', '').lower()
            similarity = self._calculate_semantic_similarity(sentence_lower, doc_content)
            max_similarity = max(max_similarity, similarity)
            
            # Check for contradictions (simplified)
            if self._detect_contradiction(sentence_lower, doc_content):
                contradicts_source = True
        
        is_supported = max_similarity > 0.4
        
        return {
            'sentence': sentence[:100] + '...' if len(sentence) > 100 else sentence,
            'is_supported': is_supported,
            'contradicts_source': contradicts_source,
            'similarity_score': max_similarity,
            'contains_factual_claim': contains_factual_claim
        }
    
    def _contains_factual_claim(self, sentence: str) -> bool:
        """Detect if sentence contains factual claims"""
        factual_indicators = [
            r'\d+(?:\.\d+)?',  # Numbers
            r'(first|second|third|one|two|three)',  # Ordinals
            r'(increase|decrease|change|improve|decline)',  # Changes
            r'(according to|based on|reported by)',  # Attribution
        ]
        return any(re.search(pattern, sentence.lower()) for pattern in factual_indicators)
    
    def _detect_contradiction(self, sentence: str, content: str) -> bool:
        """Simple contradiction detection (placeholder)"""
        # In a real implementation, this would be more sophisticated
        negation_words = ['not', 'never', 'no', 'none', 'nothing']
        sentence_words = set(sentence.split())
        content_words = set(content.split())
        
        # Very basic check
        return bool(sentence_words.intersection(negation_words) and 
                   content_words.intersection(negation_words))
    
    async def log_evaluation_metrics(
        self,
        query: str,
        response: str,
        retrieved_docs: List[Dict[str, Any]],
        rag_metrics: Dict[str, Any],
        hallucination_metrics: Dict[str, Any],
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Enhanced logging with alert generation and persistence
        """
        timestamp = datetime.utcnow().isoformat()
        log_id = f"eval_{len(self.metrics_log) + 1}_{int(datetime.utcnow().timestamp())}"
        
        # Generate system alerts
        alerts = self._generate_system_alerts(rag_metrics, hallucination_metrics)
        
        log_entry = {
            'log_id': log_id,
            'timestamp': timestamp,
            'query': query,
            'response': response,
            'retrieved_doc_count': len(retrieved_docs),
            'rag_metrics': rag_metrics,
            'hallucination_metrics': hallucination_metrics,
            'alerts': alerts,
            'overall_health': self._calculate_overall_health(rag_metrics, hallucination_metrics),
            'metadata': additional_metadata or {},
            'version': '1.0'
        }
        
        self.metrics_log.append(log_entry)
        self.evaluation_history.append({
            'timestamp': timestamp,
            'log_id': log_id,
            'health_score': log_entry['overall_health'],
            'alert_count': len(alerts)
        })
        
        # Persist to file (in production, this would go to a database)
        self._persist_metrics(log_entry)
        
        return log_id
    
    async def evaluate_full_rag_pipeline(
        self, 
        query: str, 
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Evaluate the full RAG pipeline: query -> retrieval -> generation -> evaluation
        """
        # Step 1: Retrieve documents
        retrieved_docs = await semantic_search(query, top_k)
        
        # Step 2: Generate response using LLM
        context = "\n\n".join([doc.content for doc in retrieved_docs])
        response = await get_llm_response(query, context)
        
        # Step 3: Evaluate retrieval relevance
        rag_metrics = await self.evaluate_rag_relevance(query, retrieved_docs, top_k)
        
        # Step 4: Detect hallucinations in the response
        hallucination_metrics = await self.detect_hallucination(response, retrieved_docs)
        
        # Step 5: Log the evaluation
        log_id = await self.log_evaluation_metrics(
            query=query,
            response=response,
            retrieved_docs=retrieved_docs,
            rag_metrics=rag_metrics,
            hallucination_metrics=hallucination_metrics
        )
        
        return {
            'log_id': log_id,
            'query': query,
            'response': response,
            'retrieved_docs': retrieved_docs,
            'rag_metrics': rag_metrics,
            'hallucination_metrics': hallucination_metrics,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _generate_hallucination_alerts(self, hallucination_score: float, contradiction_score: float, 
                                     confidence: float, fact_claims: List) -> List[str]:
        """Generate alerts for hallucination detection"""
        alerts = []
        if hallucination_score > self.alert_thresholds['hallucination_score']:
            alerts.append(f"High hallucination risk ({hallucination_score:.2f})")
        if contradiction_score > 0.1:
            alerts.append(f"Contradictions detected ({contradiction_score:.2f})")
        if confidence < self.alert_thresholds['low_confidence']:
            alerts.append(f"Low confidence ({confidence:.2f})")
        if len(fact_claims) > 5:
            alerts.append(f"High number of factual claims ({len(fact_claims)}) - increased hallucination risk")
        return alerts
    
    def _generate_system_alerts(self, rag_metrics: Dict, hallucination_metrics: Dict) -> List[str]:
        """Generate system-wide alerts"""
        alerts = []
        alerts.extend(rag_metrics.get('alerts', []))
        alerts.extend(hallucination_metrics.get('alerts', []))
        return alerts
    
    def _calculate_overall_health(self, rag_metrics: Dict, hallucination_metrics: Dict) -> float:
        """Calculate overall system health score (0-1)"""
        # Weighted combination of key metrics
        precision = rag_metrics.get('precision', 0)
        recall = rag_metrics.get('recall', 0)
        hallucination_score = hallucination_metrics.get('hallucination_score', 1)
        confidence = hallucination_metrics.get('confidence', 0)
        
        # Lower hallucination score is better, so we invert it
        health_score = (
            0.3 * precision +
            0.3 * recall +
            0.2 * (1 - hallucination_score) +
            0.2 * confidence
        )
        return min(1.0, max(0.0, health_score))
    
    def _persist_metrics(self, log_entry: Dict):
        """Persist metrics to file (placeholder for database integration)"""
        try:
            # In production, this would save to a database
            pass
        except Exception as e:
            logger.warning(f"Failed to persist metrics: {e}")
    
    def get_evaluation_summary(self) -> Dict[str, Any]:
        """
        Enhanced evaluation summary with health metrics
        """
        if not self.metrics_log:
            return {
                'total_evaluations': 0,
                'metrics': {},
                'health_summary': {},
                'alert_summary': {}
            }
        
        # Aggregate metrics
        metrics_sum = defaultdict(float)
        metric_counts = defaultdict(int)
        
        for entry in self.metrics_log:
            # RAG metrics
            for key, value in entry['rag_metrics'].items():
                if isinstance(value, (int, float)):
                    metrics_sum[f'rag_{key}'] += value
                    metric_counts[f'rag_{key}'] += 1
            
            # Hallucination metrics
            for key, value in entry['hallucination_metrics'].items():
                if isinstance(value, (int, float)):
                    metrics_sum[f'hallucination_{key}'] += value
                    metric_counts[f'hallucination_{key}'] += 1
        
        # Calculate averages
        averages = {}
        for key, total in metrics_sum.items():
            count = metric_counts[key]
            averages[key] = total / count if count > 0 else 0
        
        # Health summary
        health_scores = [entry['overall_health'] for entry in self.metrics_log]
        alert_counts = [len(entry['alerts']) for entry in self.metrics_log]
        
        health_summary = {
            'average_health_score': sum(health_scores) / len(health_scores),
            'min_health_score': min(health_scores),
            'max_health_score': max(health_scores),
            'unhealthy_queries': len([s for s in health_scores if s < 0.7]),
            'average_alerts_per_query': sum(alert_counts) / len(alert_counts)
        }
        
        # Alert summary
        all_alerts = []
        for entry in self.metrics_log:
            all_alerts.extend(entry['alerts'])
        
        alert_summary = {
            'total_alerts': len(all_alerts),
            'unique_alert_types': len(set(all_alerts)),
            'most_common_alerts': self._get_most_common_items(all_alerts, 5)
        }
        
        return {
            'total_evaluations': len(self.metrics_log),
            'metrics': averages,
            'health_summary': health_summary,
            'alert_summary': alert_summary,
            'recent_evaluations': len([e for e in self.evaluation_history 
                                     if datetime.fromisoformat(e['timestamp']) > 
                                        datetime.utcnow().replace(tzinfo=None) - 
                                        datetime.timedelta(hours=24)])
        }
    
    def _get_most_common_items(self, items: List[str], n: int) -> List[Dict[str, Any]]:
        """Get most common items with counts"""
        from collections import Counter
        counter = Counter(items)
        return [{'item': item, 'count': count} for item, count in counter.most_common(n)]
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance trends over time"""
        cutoff_time = datetime.utcnow().replace(tzinfo=None) - datetime.timedelta(hours=hours)
        recent_evaluations = [
            entry for entry in self.evaluation_history 
            if datetime.fromisoformat(entry['timestamp']) > cutoff_time
        ]
        
        if not recent_evaluations:
            return {'message': 'No recent evaluations found'}
        
        # Group by hour
        hourly_data = defaultdict(list)
        for entry in recent_evaluations:
            hour = datetime.fromisoformat(entry['timestamp']).hour
            hourly_data[hour].append(entry)
        
        trends = {}
        for hour, entries in hourly_data.items():
            avg_health = sum(e['health_score'] for e in entries) / len(entries)
            avg_alerts = sum(e['alert_count'] for e in entries) / len(entries)
            trends[hour] = {
                'average_health': avg_health,
                'average_alerts': avg_alerts,
                'evaluation_count': len(entries)
            }
        
        return {
            'timeframe_hours': hours,
            'hourly_trends': dict(sorted(trends.items())),
            'total_evaluations': len(recent_evaluations)
        }

# Global evaluation service instance
evaluation_service = EvaluationService()