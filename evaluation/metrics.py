from typing import Dict, List, Optional, Tuple
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
from dataclasses import dataclass
import json


@dataclass
class EvaluationDataset:
    tickets: List[Dict]
    ground_truth_analyses: List[Dict]
    expected_responses: List[Dict]
    customer_feedbacks: List[Dict]


class PerformanceMetrics:
    @staticmethod
    def calculate_classification_metrics(predictions: List[str], ground_truth: List[str]) -> Dict[str, float]:
        if not predictions or not ground_truth:
            return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0}
            
        accuracy = accuracy_score(ground_truth, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            ground_truth, predictions, average='weighted', zero_division=0
        )
        
        return {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1)
        }
    
    @staticmethod
    def calculate_response_quality_metrics(responses: List[Dict]) -> Dict[str, float]:
        if not responses:
            return {"avg_confidence": 0.0, "escalation_rate": 0.0, "resolution_rate": 0.0}
            
        confidences = [r.get('confidence_score', 0) for r in responses]
        escalations = [1 if r.get('escalation_needed', False) else 0 for r in responses]
        resolutions = [1 if not r.get('follow_up_required', True) else 0 for r in responses]
        
        return {
            "avg_confidence": float(np.mean(confidences)),
            "escalation_rate": float(np.mean(escalations)),
            "resolution_rate": float(np.mean(resolutions)),
            "confidence_std": float(np.std(confidences))
        }
    
    @staticmethod
    def calculate_latency_metrics(latencies: List[float]) -> Dict[str, float]:
        if not latencies:
            return {"mean_latency": 0.0, "p50_latency": 0.0, "p95_latency": 0.0, "p99_latency": 0.0}
            
        return {
            "mean_latency": float(np.mean(latencies)),
            "p50_latency": float(np.percentile(latencies, 50)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "p99_latency": float(np.percentile(latencies, 99)),
            "max_latency": float(np.max(latencies)),
            "min_latency": float(np.min(latencies))
        }


class ABTestFramework:
    def __init__(self):
        self.results_a = []
        self.results_b = []
        
    def add_result(self, variant: str, metrics: Dict[str, float]):
        if variant == 'A':
            self.results_a.append(metrics)
        elif variant == 'B':
            self.results_b.append(metrics)
        else:
            raise ValueError(f"Unknown variant: {variant}")
    
    def calculate_significance(self, metric_name: str) -> Dict[str, float]:
        if not self.results_a or not self.results_b:
            return {"significant": False, "p_value": 1.0, "improvement": 0.0}
            
        values_a = [r.get(metric_name, 0) for r in self.results_a]
        values_b = [r.get(metric_name, 0) for r in self.results_b]
        
        mean_a = np.mean(values_a)
        mean_b = np.mean(values_b)
        
        from scipy import stats
        t_stat, p_value = stats.ttest_ind(values_a, values_b)
        
        improvement = ((mean_b - mean_a) / mean_a) * 100 if mean_a != 0 else 0
        
        return {
            "significant": p_value < 0.05,
            "p_value": float(p_value),
            "improvement_percent": float(improvement),
            "mean_a": float(mean_a),
            "mean_b": float(mean_b),
            "sample_size_a": len(values_a),
            "sample_size_b": len(values_b)
        }
    
    def get_summary(self) -> Dict[str, Dict[str, float]]:
        if not self.results_a or not self.results_b:
            return {}
            
        all_metrics = set()
        for result in self.results_a + self.results_b:
            all_metrics.update(result.keys())
        
        summary = {}
        for metric in all_metrics:
            summary[metric] = self.calculate_significance(metric)
            
        return summary


class RegressionTester:
    def __init__(self, baseline_results: Dict[str, Dict]):
        self.baseline = baseline_results
        self.regression_threshold = 0.05  
        
    def check_regression(self, new_results: Dict[str, Dict]) -> Dict[str, List[str]]:
        regressions = {
            "critical": [],
            "warning": [],
            "passed": []
        }
        
        for test_name, baseline_metrics in self.baseline.items():
            if test_name not in new_results:
                regressions["critical"].append(f"{test_name}: Test missing in new results")
                continue
                
            new_metrics = new_results[test_name]
            
            for metric_name, baseline_value in baseline_metrics.items():
                if metric_name not in new_metrics:
                    regressions["warning"].append(f"{test_name}.{metric_name}: Metric missing")
                    continue
                    
                new_value = new_metrics[metric_name]
                
                if isinstance(baseline_value, (int, float)) and isinstance(new_value, (int, float)):
                    degradation = (baseline_value - new_value) / baseline_value if baseline_value != 0 else 0
                    
                    if degradation > self.regression_threshold:
                        regressions["critical"].append(
                            f"{test_name}.{metric_name}: {degradation*100:.1f}% degradation "
                            f"(baseline: {baseline_value:.3f}, new: {new_value:.3f})"
                        )
                    elif degradation > 0:
                        regressions["warning"].append(
                            f"{test_name}.{metric_name}: {degradation*100:.1f}% degradation"
                        )
                    else:
                        regressions["passed"].append(f"{test_name}.{metric_name}")
                        
        return regressions
    
    def update_baseline(self, new_results: Dict[str, Dict]):
        self.baseline = new_results.copy()


class CostCalculator:
    def __init__(self, model_costs: Optional[Dict[str, float]] = None):
        self.model_costs = model_costs or {
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
            "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125}
        }
        
    def calculate_agent_cost(self, agent_name: str, model: str, 
                           input_tokens: int, output_tokens: int) -> Dict[str, float]:
        if model not in self.model_costs:
            return {"error": f"Unknown model: {model}"}
            
        costs = self.model_costs[model]
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        total_cost = input_cost + output_cost
        
        return {
            "agent": agent_name,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost
        }
    
    def calculate_pipeline_cost(self, agent_costs: List[Dict[str, float]]) -> Dict[str, float]:
        total_input_tokens = sum(c.get("input_tokens", 0) for c in agent_costs)
        total_output_tokens = sum(c.get("output_tokens", 0) for c in agent_costs)
        total_cost = sum(c.get("total_cost", 0) for c in agent_costs)
        
        return {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_cost": total_cost,
            "cost_per_ticket": total_cost,
            "agent_breakdown": agent_costs
        }