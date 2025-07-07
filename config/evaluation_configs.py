from typing import Dict, List, Any


class EvaluationThresholds:
    TICKET_ANALYZER = {
        "classification_accuracy": 0.85,
        "extraction_completeness": 0.90,
        "sentiment_accuracy": 0.80,
        "priority_accuracy": 0.75,
        "entity_extraction_f1": 0.85
    }
    
    KNOWLEDGE_RETRIEVAL = {
        "avg_relevance_score": 0.70,
        "high_relevance_ratio": 0.60,
        "coverage_metric": 0.80,
        "retrieval_speed_ms": 500
    }
    
    SYSTEM_STATUS = {
        "status_accuracy": 0.95,
        "false_positive_rate": 0.05,
        "api_response_time_ms": 200,
        "incident_detection_rate": 0.90
    }
    
    RESPONSE_SYNTHESIS = {
        "customer_satisfaction": 0.80,
        "response_completeness": 0.85,
        "tone_appropriateness": 0.90,
        "resolution_rate": 0.70,
        "readability_score": 8.0  
    }


class TestScenarios:
    EDGE_CASES = [
        {
            "name": "empty_ticket",
            "ticket": {"subject": "", "body": ""},
            "expected_behavior": "graceful_degradation"
        },
        {
            "name": "extremely_long_ticket",
            "ticket": {"subject": "Issue", "body": "x" * 10000},
            "expected_behavior": "truncation_handling"
        },
        {
            "name": "multiple_languages",
            "ticket": {"subject": "Problem", "body": "Hello, Bonjour, Hola, 你好"},
            "expected_behavior": "language_detection"
        },
        {
            "name": "sql_injection_attempt",
            "ticket": {"subject": "'; DROP TABLE users; --", "body": "test"},
            "expected_behavior": "security_handling"
        }
    ]
    
    PERFORMANCE_SCENARIOS = [
        {
            "name": "single_ticket",
            "ticket_count": 1,
            "max_latency_ms": 5000
        },
        {
            "name": "batch_processing",
            "ticket_count": 10,
            "max_latency_ms": 30000
        },
        {
            "name": "concurrent_processing",
            "ticket_count": 50,
            "max_latency_ms": 60000
        }
    ]


class MetricDefinitions:
    BUSINESS_METRICS = {
        "first_contact_resolution_rate": {
            "formula": "tickets_resolved_without_escalation / total_tickets",
            "target": 0.75,
            "unit": "percentage"
        },
        "average_handle_time": {
            "formula": "sum(processing_times) / ticket_count",
            "target": 30,
            "unit": "seconds"
        },
        "cost_per_resolution": {
            "formula": "total_api_costs / resolved_tickets",
            "target": 0.50,
            "unit": "dollars"
        },
        "customer_effort_score": {
            "formula": "1 - (escalations + follow_ups) / total_tickets",
            "target": 0.85,
            "unit": "score"
        }
    }
    
    TECHNICAL_METRICS = {
        "api_availability": {
            "formula": "successful_api_calls / total_api_calls",
            "target": 0.999,
            "unit": "percentage"
        },
        "cache_hit_rate": {
            "formula": "cache_hits / (cache_hits + cache_misses)",
            "target": 0.80,
            "unit": "percentage"
        },
        "token_efficiency": {
            "formula": "useful_tokens / total_tokens_used",
            "target": 0.85,
            "unit": "percentage"
        }
    }


def get_evaluation_profile(profile_name: str) -> Dict[str, Any]:
    profiles = {
        "quick_test": {
            "sample_size": 10,
            "iterations": 1,
            "metrics": ["classification_accuracy", "response_quality"],
            "thresholds": "relaxed"
        },
        "daily_regression": {
            "sample_size": 100,
            "iterations": 3,
            "metrics": "all",
            "thresholds": "standard"
        },
        "full_evaluation": {
            "sample_size": 1000,
            "iterations": 10,
            "metrics": "all",
            "thresholds": "strict",
            "include_ab_testing": True,
            "include_cost_analysis": True
        }
    }
    
    return profiles.get(profile_name, profiles["quick_test"])