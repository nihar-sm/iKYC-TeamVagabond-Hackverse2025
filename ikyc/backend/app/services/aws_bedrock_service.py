import boto3
import json
import base64
import logging
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError
from core.ai_config import ai_config

logger = logging.getLogger(__name__)

class AWSBedrockAnalyzer:
    """AWS Bedrock Nova service for document image analysis and fraud detection"""
    
    def __init__(self):
        self.region = ai_config.aws_region
        self.model_id = ai_config.aws_bedrock_model_id
        
        try:
            # Initialize Bedrock client
            if ai_config.aws_access_key_id and ai_config.aws_secret_access_key:
                self.client = boto3.client(
                    "bedrock-runtime",
                    region_name=self.region,
                    aws_access_key_id=ai_config.aws_access_key_id,
                    aws_secret_access_key=ai_config.aws_secret_access_key
                )
            else:
                # Use default credentials (IAM role, etc.)
                self.client = boto3.client("bedrock-runtime", region_name=self.region)
            
            self.enabled = True
            logger.info("AWS Bedrock service initialized")
            
        except (NoCredentialsError, Exception) as e:
            logger.warning(f"AWS Bedrock initialization failed: {e}")
            self.enabled = False
    
    def analyze_document_image(self, image_path: str, document_type: str = "aadhaar") -> Dict[str, Any]:
        """Analyze document image for fraud indicators using AWS Bedrock Nova"""
        
        if not self.enabled:
            return self._mock_analysis(image_path, "AWSBedrock")
        
        try:
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()
            
            # Create fraud detection prompt
            fraud_prompt = self._create_image_fraud_prompt(document_type)
            
            # Prepare conversation for Nova
            conversation = [
                {
                    "role": "user",
                    "content": [
                        {"text": fraud_prompt},
                        {
                            "image": {
                                "format": self._get_image_format(image_path),
                                "source": {"bytes": image_bytes}
                            }
                        }
                    ]
                }
            ]
            
            # Call AWS Bedrock Nova
            response = self.client.converse(
                modelId=self.model_id,
                messages=conversation,
                inferenceConfig={
                    "maxTokens": 1000,
                    "temperature": 0.1,
                    "topP": 0.9
                }
            )
            
            # Parse response
            analysis = self._parse_bedrock_response(response, image_path)
            logger.info(f"AWS Bedrock analysis completed - Risk: {analysis['risk_level']}")
            return analysis
            
        except ClientError as e:
            logger.error(f"AWS Bedrock API error: {e}")
            return self._mock_analysis(image_path, "AWSBedrock", error=True)
        except Exception as e:
            logger.error(f"AWS Bedrock analysis failed: {e}")
            return self._mock_analysis(image_path, "AWSBedrock", error=True)
    
    def _create_image_fraud_prompt(self, document_type: str) -> str:
        """Create specialized prompt for image fraud detection"""
        
        return f"""
You are an expert in document fraud detection. Analyze this {document_type} document image for signs of forgery, tampering, or fraud.

Look for these fraud indicators:
1. Image quality inconsistencies or digital manipulation
2. Misaligned text or formatting irregularities  
3. Color or font inconsistencies
4. Signs of photo editing or overlays
5. Unusual backgrounds or lighting
6. Pixelation or resolution inconsistencies
7. Missing security features typical of authentic documents
8. Text that appears pasted or artificially added

Provide your analysis in JSON format:
{{
    "risk_score": 0.0-1.0,
    "risk_level": "LOW|MEDIUM|HIGH", 
    "fraud_indicators": ["list of visual issues detected"],
    "confidence": 0.0-1.0,
    "explanation": "detailed explanation of findings",
    "authenticity_score": 0.0-1.0
}}

Analyze the image and respond with only the JSON:
"""
    
    def _parse_bedrock_response(self, response: Dict, image_path: str) -> Dict[str, Any]:
        """Parse AWS Bedrock response and extract fraud analysis"""
        
        try:
            # Extract response text
            response_text = response["output"]["message"]["content"][0]["text"]
            
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                analysis_json = json.loads(json_match.group())
                
                return {
                    "service": "AWSBedrock",
                    "risk_score": float(analysis_json.get("risk_score", 0.0)),
                    "risk_level": analysis_json.get("risk_level", "LOW"),
                    "fraud_indicators": analysis_json.get("fraud_indicators", []),
                    "confidence": float(analysis_json.get("confidence", 0.0)),
                    "explanation": analysis_json.get("explanation", ""),
                    "authenticity_score": float(analysis_json.get("authenticity_score", 1.0)),
                    "raw_response": response_text,
                    "success": True
                }
            else:
                # Fallback if JSON parsing fails
                return self._fallback_image_analysis(response_text, image_path)
                
        except Exception as e:
            logger.error(f"Failed to parse Bedrock response: {e}")
            return self._mock_analysis(image_path, "AWSBedrock", error=True)
    
    def _fallback_image_analysis(self, response_text: str, image_path: str) -> Dict[str, Any]:
        """Fallback analysis when JSON parsing fails"""
        
        # Simple keyword-based risk assessment
        risk_keywords = ["fraud", "fake", "tampered", "manipulated", "suspicious", "forged"]
        risk_score = sum(1 for keyword in risk_keywords if keyword.lower() in response_text.lower()) / len(risk_keywords)
        
        return {
            "service": "AWSBedrock",
            "risk_score": min(risk_score, 1.0),
            "risk_level": "HIGH" if risk_score > 0.6 else "MEDIUM" if risk_score > 0.3 else "LOW",
            "fraud_indicators": ["Fallback analysis - manual review recommended"],
            "confidence": 0.5,
            "explanation": "Analysis completed with fallback method",
            "authenticity_score": 1.0 - risk_score,
            "raw_response": response_text,
            "success": True
        }
    
    def _get_image_format(self, image_path: str) -> str:
        """Determine image format from file extension"""
        ext = image_path.lower().split('.')[-1]
        format_map = {
            'jpg': 'jpeg',
            'jpeg': 'jpeg', 
            'png': 'png',
            'gif': 'gif',
            'webp': 'webp'
        }
        return format_map.get(ext, 'jpeg')
    
    def _mock_analysis(self, image_path: str, service: str, error: bool = False) -> Dict[str, Any]:
        """Mock analysis for testing or when service is unavailable"""
        
        if error:
            return {
                "service": service,
                "risk_score": 0.0,
                "risk_level": "UNKNOWN",
                "fraud_indicators": ["Service unavailable"],
                "confidence": 0.0,
                "explanation": "AI service error - manual review required",
                "authenticity_score": 0.0,
                "success": False,
                "error": "Service unavailable"
            }
        
        # Simple mock analysis based on image characteristics
        import os
        file_size = os.path.getsize(image_path) if os.path.exists(image_path) else 0
        
        risk_factors = 0
        indicators = []
        
        # Mock risk factors based on file characteristics
        if file_size < 10000:  # Very small file
            risk_factors += 1
            indicators.append("Unusually small file size")
        
        if file_size > 5000000:  # Very large file
            risk_factors += 1
            indicators.append("Unusually large file size")
        
        filename = os.path.basename(image_path).lower()
        if 'test' in filename or 'sample' in filename:
            risk_factors += 1
            indicators.append("Test or sample filename detected")
        
        risk_score = min(risk_factors * 0.3, 1.0)
        
        return {
            "service": service,
            "risk_score": risk_score,
            "risk_level": "HIGH" if risk_score > 0.7 else "MEDIUM" if risk_score > 0.4 else "LOW",
            "fraud_indicators": indicators or ["No obvious fraud indicators"],
            "confidence": 0.7,
            "explanation": "Mock analysis for testing",
            "authenticity_score": 1.0 - risk_score,
            "success": True,
            "mock": True
        }

# Global service instance
bedrock_analyzer = AWSBedrockAnalyzer()
