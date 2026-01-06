import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from ..utils.embeddings import semantic_search
from ..utils.llm_client import get_llm_response
from ..services.pinecone_service import pinecone_service

logger = logging.getLogger(__name__)

class EvaluationService:
    def __init__(self):
        self.metrics_log = []
    
    async def evaluate_rag_relevance(
        self, 
        query: str, 
        retrieved_docs: List[Dict[str, Any]], 
        top_k: int = 5
    ) -> Dict[str, float]:
        """
        Evaluate RAG retrieval relevance using precision and recall metrics
        """
        # For now, we'll implement a simple evaluation based on keyword overlap
        # In a real implementation, you would have ground truth data to compare against
        
        query_keywords = set(query.lower().split())
        
        relevant_retrieved = 0
        total_retrieved = len(retrieved_docs)
        
        for doc in retrieved_docs:
            doc_content = doc.get('content', '').lower()
            doc_keywords = set(doc_content.split())
            
            # Simple relevance check: if there's overlap in keywords, consider it relevant
            if query_keywords.intersection(doc_keywords):
                relevant_retrieved += 1
        
        # Calculate metrics
        precision = relevant_retrieved / total_retrieved if total_retrieved > 0 else 0
        recall = relevant_retrieved / top_k if top_k > 0 else 0  # Assuming top_k represents total relevant docs
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'relevant_retrieved': relevant_retrieved,
            'total_retrieved': total_retrieved
        }
    
    async def detect_hallucination(
        self, 
        response: str, 
        retrieved_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Simple hallucination detection by checking if response content is supported by retrieved documents
        """
        response_sentences = re.split(r'[.!?]+', response)
        supported_sentences = 0
        total_sentences = len(response_sentences)
        
        # Remove empty sentences
        response_sentences = [s.strip() for s in response_sentences if s.strip()]
        total_sentences = len(response_sentences)
        
        if total_sentences == 0:
            return {
                'hallucination_score': 0,
                'supported_sentences': 0,
                'total_sentences': 0,
                'confidence': 1.0
            }
        
        # Check if each sentence in the response is supported by retrieved docs
        for sentence in response_sentences:
            sentence = sentence.lower().strip()
            if not sentence:
                continue
                
            is_supported = False
            for doc in retrieved_docs:
                doc_content = doc.get('content', '').lower()
                # Check if sentence content appears in any of the retrieved documents
                if sentence in doc_content or self._sentence_matches_content(sentence, doc_content):
                    is_supported = True
                    break
            
            if is_supported:
                supported_sentences += 1
        
        hallucination_score = (total_sentences - supported_sentences) / total_sentences if total_sentences > 0 else 0
        confidence = supported_sentences / total_sentences if total_sentences > 0 else 1.0
        
        return {
            'hallucination_score': hallucination_score,
            'supported_sentences': supported_sentences,
            'total_sentences': total_sentences,
            'confidence': confidence
        }
    
    def _sentence_matches_content(self, sentence: str, content: str) -> bool:
        """
        Check if sentence content is present in the document content with some tolerance for variations
        """
        # Simple word overlap check
        sentence_words = set(sentence.split())
        content_words = set(content.split())
        
        # If at least 50% of sentence words appear in content, consider it a match
        if len(sentence_words) == 0:
            return True
        
        overlap = len(sentence_words.intersection(content_words))
        return overlap / len(sentence_words) >= 0.5
    
    async def log_evaluation_metrics(
        self,
        query: str,
        response: str,
        retrieved_docs: List[Dict[str, Any]],
        rag_metrics: Dict[str, float],
        hallucination_metrics: Dict[str, Any],
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log evaluation metrics for a query-response pair
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'query': query,
            'response': response,
            'retrieved_doc_count': len(retrieved_docs),
            'rag_metrics': rag_metrics,
            'hallucination_metrics': hallucination_metrics,
            'metadata': additional_metadata or {}
        }
        
        self.metrics_log.append(log_entry)
        
        # For now, just return the log ID
        log_id = f"eval_{len(self.metrics_log)}_{datetime.utcnow().timestamp()}"
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
    
    def get_evaluation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all evaluations
        """
        if not self.metrics_log:
            return {
                'total_evaluations': 0,
                'average_precision': 0,
                'average_recall': 0,
                'average_f1_score': 0,
                'average_hallucination_score': 0,
                'average_confidence': 0
            }
        
        total_precision = sum(entry['rag_metrics']['precision'] for entry in self.metrics_log)
        total_recall = sum(entry['rag_metrics']['recall'] for entry in self.metrics_log)
        total_f1 = sum(entry['rag_metrics']['f1_score'] for entry in self.metrics_log)
        total_hallucination = sum(entry['hallucination_metrics']['hallucination_score'] for entry in self.metrics_log)
        total_confidence = sum(entry['hallucination_metrics']['confidence'] for entry in self.metrics_log)
        
        count = len(self.metrics_log)
        
        return {
            'total_evaluations': count,
            'average_precision': total_precision / count,
            'average_recall': total_recall / count,
            'average_f1_score': total_f1 / count,
            'average_hallucination_score': total_hallucination / count,
            'average_confidence': total_confidence / count
        }

# Global evaluation service instance
evaluation_service = EvaluationService()