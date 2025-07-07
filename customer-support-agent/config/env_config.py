import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class EnvConfig:
    def __init__(self, env_file: str = ".env"):
        load_dotenv(env_file)
        self._validate_required_vars()
    
    def _validate_required_vars(self):
        required_vars = ["ANTHROPIC_API_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    @property
    def anthropic_api_key(self) -> str:
        return os.getenv("ANTHROPIC_API_KEY")
    
    @property
    def promptlayer_api_key(self) -> Optional[str]:
        return os.getenv("PROMPTLAYER_API_KEY")
    
    @property
    def environment(self) -> str:
        return os.getenv("ENVIRONMENT", "development")
    
    @property
    def use_mock_data(self) -> bool:
        return os.getenv("USE_MOCK_DATA", "true").lower() == "true"
    
    @property
    def enable_caching(self) -> bool:
        return os.getenv("ENABLE_CACHING", "true").lower() == "true"
    
    @property
    def log_level(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO").upper()
    
    @property
    def max_concurrent_requests(self) -> int:
        return int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    
    @property
    def rate_limit_per_minute(self) -> int:
        return int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "anthropic_api_key": self.anthropic_api_key,
            "promptlayer_api_key": self.promptlayer_api_key,
            "environment": self.environment,
            "use_mock_data": self.use_mock_data,
            "enable_caching": self.enable_caching,
            "log_level": self.log_level,
            "max_concurrent_requests": self.max_concurrent_requests,
            "rate_limit_per_minute": self.rate_limit_per_minute
        }
    
    def get_pipeline_config(self) -> Dict[str, Any]:
        return {
            "anthropic_api_key": self.anthropic_api_key,
            "promptlayer_api_key": self.promptlayer_api_key,
            "use_mock_data": self.use_mock_data
        }