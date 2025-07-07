import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import promptlayer
from functools import wraps
import time
import json


class PromptLayerEvaluator:
    def __init__(self, api_key: str, anthropic_api_key: str):
        self.promptlayer_client = promptlayer.PromptLayer(api_key=api_key)
        self.anthropic = self.promptlayer_client.anthropic
        self.anthropic.api_key = anthropic_api_key
        self.evaluation_tags = []
        
    def track_request(self, agent_name: str, operation: str):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                metadata = {
                    "agent": agent_name,
                    "operation": operation,
                    "timestamp": datetime.now().isoformat(),
                    "args": str(args[:2]) if args else "",  
                }
                
                try:
                    result = func(*args, **kwargs)
                    latency = time.time() - start_time
                    
                    metadata.update({
                        "status": "success",
                        "latency_ms": int(latency * 1000),
                        "result_type": type(result).__name__
                    })
                    
                    self.promptlayer_client.track.metadata(
                        request_id=getattr(result, '_pl_request_id', None),
                        metadata=metadata
                    )
                    
                    return result
                    
                except Exception as e:
                    latency = time.time() - start_time
                    metadata.update({
                        "status": "error",
                        "error": str(e),
                        "latency_ms": int(latency * 1000)
                    })
                    
                    self.promptlayer_client.track.metadata(
                        request_id=None,
                        metadata=metadata
                    )
                    
                    raise
                    
            return wrapper
        return decorator
    
    def score_response(self, request_id: str, scores: Dict[str, float], metadata: Optional[Dict] = None):
        for metric_name, score in scores.items():
            self.promptlayer_client.track.score(
                request_id=request_id,
                score=score,
                score_name=metric_name
            )
            
        if metadata:
            self.promptlayer_client.track.metadata(
                request_id=request_id,
                metadata=metadata
            )
    
    def create_tracked_anthropic_client(self):
        return self.anthropic.Anthropic()


class AgentEvaluationMetrics:
    @staticmethod
    def evaluate_ticket_analyzer(analysis_result: Dict, ground_truth: Optional[Dict] = None) -> Dict[str, float]:
        metrics = {}
        
        metrics['extraction_completeness'] = sum([
            1 if analysis_result.get('category') else 0,
            1 if analysis_result.get('priority') else 0,
            1 if analysis_result.get('sentiment') else 0,
            1 if analysis_result.get('key_issues') else 0,
            1 if analysis_result.get('customer_intent') else 0,
        ]) / 5.0
        
        metrics['issue_count'] = len(analysis_result.get('key_issues', []))
        metrics['error_code_extraction'] = 1.0 if analysis_result.get('error_codes') else 0.0
        
        if ground_truth:
            metrics['category_accuracy'] = 1.0 if analysis_result.get('category') == ground_truth.get('category') else 0.0
            metrics['priority_accuracy'] = 1.0 if analysis_result.get('priority') == ground_truth.get('priority') else 0.0
            metrics['sentiment_accuracy'] = 1.0 if analysis_result.get('sentiment') == ground_truth.get('sentiment') else 0.0
        
        return metrics
    
    @staticmethod
    def evaluate_knowledge_retrieval(retrieval_result: Dict, relevance_threshold: float = 0.7) -> Dict[str, float]:
        metrics = {}
        
        articles = retrieval_result.get('relevant_articles', [])
        metrics['articles_found'] = len(articles)
        
        if articles:
            relevance_scores = [article.get('relevance_score', 0) for article in articles]
            metrics['avg_relevance_score'] = sum(relevance_scores) / len(relevance_scores)
            metrics['high_relevance_ratio'] = sum(1 for score in relevance_scores if score >= relevance_threshold) / len(relevance_scores)
        else:
            metrics['avg_relevance_score'] = 0.0
            metrics['high_relevance_ratio'] = 0.0
        
        metrics['solution_count'] = len(retrieval_result.get('recommended_solutions', []))
        metrics['has_solutions'] = 1.0 if retrieval_result.get('recommended_solutions') else 0.0
        
        return metrics
    
    @staticmethod
    def evaluate_system_status(status_result: Dict, actual_status: Optional[Dict] = None) -> Dict[str, float]:
        metrics = {}
        
        system_status = status_result.get('system_status', {})
        metrics['status_detected'] = 1.0 if system_status.get('overall') else 0.0
        metrics['incident_count'] = len(system_status.get('current_incidents', []))
        metrics['affected_services_count'] = len(system_status.get('affected_services', []))
        
        if system_status.get('overall') == 'operational':
            metrics['health_score'] = 1.0
        elif system_status.get('overall') == 'degraded':
            metrics['health_score'] = 0.5
        else:
            metrics['health_score'] = 0.0
        
        if actual_status:
            metrics['status_accuracy'] = 1.0 if system_status.get('overall') == actual_status.get('overall') else 0.0
        
        return metrics
    
    @staticmethod
    def evaluate_response_synthesis(response_result: Dict, customer_feedback: Optional[Dict] = None) -> Dict[str, float]:
        metrics = {}
        
        metrics['confidence_score'] = response_result.get('confidence_score', 0.0)
        metrics['action_count'] = len(response_result.get('suggested_actions', []))
        metrics['requires_follow_up'] = 1.0 if response_result.get('follow_up_required') else 0.0
        metrics['needs_escalation'] = 1.0 if response_result.get('escalation_needed') else 0.0
        
        response_text = response_result.get('response_text', '')
        words = response_text.split()
        metrics['response_length'] = len(words)
        metrics['response_completeness'] = min(len(words) / 50, 1.0)  
        
        if customer_feedback:
            metrics['customer_satisfaction'] = customer_feedback.get('satisfaction_score', 0.0) / 5.0
            metrics['issue_resolved'] = 1.0 if customer_feedback.get('issue_resolved') else 0.0
        
        return metrics


class EvaluationOrchestrator:
    def __init__(self, promptlayer_evaluator: PromptLayerEvaluator):
        self.evaluator = promptlayer_evaluator
        self.metrics_calculator = AgentEvaluationMetrics()
        
    def evaluate_full_pipeline(self, 
                             ticket: str,
                             analysis_result: Dict,
                             retrieval_result: Dict,
                             status_result: Dict,
                             response_result: Dict,
                             ground_truth: Optional[Dict] = None) -> Dict[str, Any]:
        
        pipeline_metrics = {
            "ticket_analyzer": self.metrics_calculator.evaluate_ticket_analyzer(
                analysis_result, ground_truth.get('analysis') if ground_truth else None
            ),
            "knowledge_retrieval": self.metrics_calculator.evaluate_knowledge_retrieval(retrieval_result),
            "system_status": self.metrics_calculator.evaluate_system_status(
                status_result, ground_truth.get('status') if ground_truth else None
            ),
            "response_synthesis": self.metrics_calculator.evaluate_response_synthesis(
                response_result, ground_truth.get('feedback') if ground_truth else None
            )
        }
        
        overall_score = sum([
            sum(metrics.values()) / len(metrics) if metrics else 0
            for metrics in pipeline_metrics.values()
        ]) / 4
        
        return {
            "overall_score": overall_score,
            "agent_metrics": pipeline_metrics,
            "timestamp": datetime.now().isoformat(),
            "ticket_preview": ticket[:100] + "..." if len(ticket) > 100 else ticket
        }