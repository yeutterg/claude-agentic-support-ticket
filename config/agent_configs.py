from typing import Dict, Any


class AgentConfig:
    TICKET_ANALYZER = {
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.2,
        "max_tokens": 1000,
        "retry_attempts": 3,
        "timeout_seconds": 30
    }
    
    KNOWLEDGE_RETRIEVAL = {
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.3,
        "max_tokens": 1500,
        "embedding_model": "all-MiniLM-L6-v2",
        "top_k_articles": 5,
        "relevance_threshold": 0.7
    }
    
    SYSTEM_STATUS = {
        "model": "claude-haiku-4-20250514",
        "temperature": 0.1,
        "max_tokens": 1000,
        "api_timeout": 10,
        "cache_ttl_seconds": 300
    }
    
    RESPONSE_SYNTHESIS = {
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.7,
        "max_tokens": 1500,
        "tone_mapping": {
            "angry": "apologetic",
            "negative": "apologetic",
            "neutral": "professional",
            "positive": "friendly"
        }
    }


class PipelineConfig:
    MAX_PROCESSING_TIME_SECONDS = 30
    ESCALATION_THRESHOLDS = {
        "sentiment_score": -0.8,
        "confidence_score": 0.3,
        "priority": ["critical"],
        "keywords": ["legal", "lawsuit", "security breach", "data loss"]
    }
    
    QUALITY_THRESHOLDS = {
        "min_confidence_score": 0.6,
        "min_relevance_score": 0.5,
        "max_response_length": 500,
        "min_response_length": 50
    }


class EvaluationConfig:
    METRICS_TO_TRACK = [
        "classification_accuracy",
        "response_quality",
        "processing_latency",
        "cost_per_ticket",
        "escalation_rate",
        "resolution_rate"
    ]
    
    AB_TEST_PARAMETERS = {
        "models": {
            "A": "claude-sonnet-4-20250514",
            "B": "claude-haiku-4-20250514"
        },
        "temperatures": {
            "A": 0.7,
            "B": 0.5
        },
        "prompts": {
            "A": "standard",
            "B": "chain_of_thought"
        }
    }
    
    REGRESSION_TEST_SUITE = [
        "test_classification_accuracy",
        "test_response_completeness",
        "test_escalation_detection",
        "test_error_handling",
        "test_latency_requirements"
    ]


def get_environment_config(env: str = "development") -> Dict[str, Any]:
    configs = {
        "development": {
            "use_mock_data": True,
            "enable_caching": True,
            "log_level": "DEBUG",
            "max_concurrent_requests": 5,
            "rate_limit_per_minute": 60
        },
        "staging": {
            "use_mock_data": False,
            "enable_caching": True,
            "log_level": "INFO",
            "max_concurrent_requests": 10,
            "rate_limit_per_minute": 100
        },
        "production": {
            "use_mock_data": False,
            "enable_caching": True,
            "log_level": "WARNING",
            "max_concurrent_requests": 20,
            "rate_limit_per_minute": 200
        }
    }
    
    return configs.get(env, configs["development"])