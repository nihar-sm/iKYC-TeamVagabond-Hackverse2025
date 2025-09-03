try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import Optional
import os

class AIServicesConfig(BaseSettings):
    # IBM Granite Configuration
    ibm_granite_api_key: Optional[str] = None
    ibm_granite_url: Optional[str] = "https://us-south.ml.cloud.ibm.com"
    ibm_project_id: Optional[str] = None
    
    # AWS Bedrock Configuration  
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    aws_bedrock_model_id: str = "amazon.nova-lite-v1:0"
    
    # Fraud Detection Thresholds
    fraud_threshold_high: float = 0.8
    fraud_threshold_medium: float = 0.5
    fraud_threshold_low: float = 0.3
    
    # AI Service Settings
    enable_ibm_granite: bool = True
    enable_aws_bedrock: bool = True
    ai_timeout_seconds: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False

ai_config = AIServicesConfig()
