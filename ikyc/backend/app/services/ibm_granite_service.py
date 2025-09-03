import requests
import json
import logging
from typing import Dict, Any, Optional
from core.ai_config import ai_config

logger = logging.getLogger(__name__)

class IBMGraniteAnalyzer:
    """IBM Granite AI service for document text analysis and fraud detection"""
    
    def __init__(self):
        self.api_key = ai_config.ibm_granite_api_key
        self.base_url = ai_config.ibm_granite_url
        self.project_id = ai_config.ibm_project_id
        self.timeout = ai_config.ai_timeout_seconds
        
        if not self.api_key:
            logger.warning("IBM Granite API key not configured - service disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("IBM Granite service initialized")
    
    def analyze_document_text(self, text: str, document_type: str = "aadhaar") -> Dict[str, Any]:
        """Analyze document text for fraud indicators using IBM Granite"""
        
        if not self.enabled:
            return self._mock_analysis(text, "IBMGranite")
        
        try:
            # Prepare prompt for fraud detection
            fraud_detection_prompt = self._create_fraud_detection_prompt(text, document_type)
            
            # Call IBM Granite API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "input": fraud_detection_prompt,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.1,
                    "top_p": 0.9
                },
                "model_id": "granite-13b-instruct-v2",
                "project_id": self.project_id
            }
            
            response = requests.post(
                f"{self.base_url}/ml/v1/text/generation",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = self._parse_granite_response(result, text)
                logger.info(f"IBM Granite analysis completed - Risk: {analysis['risk_level']}")
                return analysis
            else:
                logger.error(f"IBM Granite API error: {response.status_code}")
                return self._mock_analysis(text, "IBMGranite", error=True)
                
        except Exception as e:
            logger.error(f"IBM Granite analysis failed: {e}")
            return self._mock_analysis(text, "IBMGranite", error=True)
    
    def _create_fraud_detection_prompt(self, text: str, document_type: str) -> str:
        """Create specialized prompt for fraud detection analysis"""
        
        return f"""
You are an AI fraud detection specialist analyzing {document_type} documents for suspicious patterns.

Analyze the following document text for potential fraud indicators:

Document Text:
{text}

Evaluate for these fraud indicators:
1. Inconsistent formatting or unusual characters
2. Suspicious patterns in ID numbers
3. Unrealistic personal information
4. Text that appears artificially generated
5. Missing or incomplete standard document elements
6. Inconsistent name formatting
7. Unusual date patterns or impossible dates

Provide your analysis in this JSON format:
{{
    "risk_score": 0.0-1.0,
    "risk_level": "LOW|MEDIUM|HIGH",
    "fraud_indicators": ["list of detected issues"],
    "confidence": 0.0-1.0,
    "explanation": "brief explanation of findings"
}}

Analysis:
"""
    
    def _parse_granite_response(self, response: Dict, original_text: str) -> Dict[str, Any]:
        """Parse IBM Granite response and extract fraud analysis"""
        
        try:
            # Extract generated text
            generated_text = response.get("results", [{}])[0].get("generated_text", "")
            
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
            
            if json_match:
                analysis_json = json.loads(json_match.group())
                
                return {
                    "service": "IBMGranite",
                    "risk_score": float(analysis_json.get("risk_score", 0.0)),
                    "risk_level": analysis_json.get("risk_level", "LOW"),
                    "fraud_indicators": analysis_json.get("fraud_indicators", []),
                    "confidence": float(analysis_json.get("confidence", 0.0)),
                    "explanation": analysis_json.get("explanation", ""),
                    "raw_response": generated_text,
                    "success": True
                }
            else:
                # Fallback analysis if JSON parsing fails
                return self._fallback_analysis(generated_text, original_text)
                
        except Exception as e:
            logger.error(f"Failed to parse Granite response: {e}")
            return self._mock_analysis(original_text, "IBMGranite", error=True)
    
    def _fallback_analysis(self, response_text: str, original_text: str) -> Dict[str, Any]:
        """Fallback analysis when JSON parsing fails"""
        
        # Simple keyword-based risk assessment
        risk_keywords = ["suspicious", "fraud", "fake", "invalid", "inconsistent", "unusual"]
        risk_score = sum(1 for keyword in risk_keywords if keyword.lower() in response_text.lower()) / len(risk_keywords)
        
        return {
            "service": "IBMGranite",
            "risk_score": min(risk_score, 1.0),
            "risk_level": "HIGH" if risk_score > 0.6 else "MEDIUM" if risk_score > 0.3 else "LOW",
            "fraud_indicators": ["Fallback analysis - manual review recommended"],
            "confidence": 0.5,
            "explanation": "Analysis completed with fallback method",
            "raw_response": response_text,
            "success": True
        }
    
    def _mock_analysis(self, text: str, service: str, error: bool = False) -> Dict[str, Any]:
        """Mock analysis for testing or when service is unavailable"""
        
        if error:
            return {
                "service": service,
                "risk_score": 0.0,
                "risk_level": "UNKNOWN",
                "fraud_indicators": ["Service unavailable"],
                "confidence": 0.0,
                "explanation": "AI service error - manual review required",
                "success": False,
                "error": "Service unavailable"
            }
        
        # Simple mock analysis based on text characteristics
        risk_factors = 0
        indicators = []
        
        # Check for suspicious patterns
        if len(text) < 50:
            risk_factors += 1
            indicators.append("Document text too short")
        
        if "1234567890" in text or "0000000000" in text:
            risk_factors += 2
            indicators.append("Sequential or repeated numbers detected")
        
        if not any(char.isalpha() for char in text):
            risk_factors += 1
            indicators.append("No alphabetic characters found")
        
        risk_score = min(risk_factors * 0.25, 1.0)
        
        return {
            "service": service,
            "risk_score": risk_score,
            "risk_level": "HIGH" if risk_score > 0.7 else "MEDIUM" if risk_score > 0.4 else "LOW",
            "fraud_indicators": indicators or ["No obvious fraud indicators"],
            "confidence": 0.7,
            "explanation": "Mock analysis for testing",
            "success": True,
            "mock": True
        }

# Global service instance
granite_analyzer = IBMGraniteAnalyzer()
