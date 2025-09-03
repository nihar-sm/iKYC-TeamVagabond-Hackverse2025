import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from services.ibm_granite_service import granite_analyzer
from services.aws_bedrock_service import bedrock_analyzer
from core.ai_config import ai_config

logger = logging.getLogger(__name__)

class FraudDetectionOrchestrator:
    """Orchestrates multiple AI services for comprehensive fraud detection"""
    
    def __init__(self):
        self.granite = granite_analyzer
        self.bedrock = bedrock_analyzer
        self.thresholds = {
            "high": ai_config.fraud_threshold_high,
            "medium": ai_config.fraud_threshold_medium,
            "low": ai_config.fraud_threshold_low
        }
    
    def analyze_document_fraud(
        self, 
        document_text: str, 
        image_path: str, 
        document_type: str = "aadhaar"
    ) -> Dict[str, Any]:
        """Comprehensive fraud analysis using multiple AI services"""
        
        logger.info(f"Starting comprehensive fraud analysis for {document_type}")
        
        analyses = []
        
        # IBM Granite text analysis
        if ai_config.enable_ibm_granite:
            try:
                granite_result = self.granite.analyze_document_text(document_text, document_type)
                analyses.append(granite_result)
                logger.info(f"IBM Granite analysis: {granite_result['risk_level']}")
            except Exception as e:
                logger.error(f"IBM Granite analysis failed: {e}")
        
        # AWS Bedrock image analysis
        if ai_config.enable_aws_bedrock:
            try:
                bedrock_result = self.bedrock.analyze_document_image(image_path, document_type)
                analyses.append(bedrock_result)
                logger.info(f"AWS Bedrock analysis: {bedrock_result['risk_level']}")
            except Exception as e:
                logger.error(f"AWS Bedrock analysis failed: {e}")
        
        # Combine results
        combined_analysis = self._combine_analyses(analyses, document_type)
        
        logger.info(f"Combined fraud analysis: {combined_analysis['overall_risk_level']} "
                   f"(Score: {combined_analysis['combined_risk_score']:.2f})")
        
        return combined_analysis
    
    def _combine_analyses(self, analyses: List[Dict[str, Any]], document_type: str) -> Dict[str, Any]:
        """Combine multiple AI analysis results into unified fraud assessment"""
        
        if not analyses:
            return self._create_default_analysis(document_type, "No AI services available")
        
        # Extract successful analyses
        successful_analyses = [a for a in analyses if a.get('success', False)]
        
        if not successful_analyses:
            return self._create_default_analysis(document_type, "All AI services failed")
        
        # Calculate combined metrics
        risk_scores = [a['risk_score'] for a in successful_analyses]
        confidences = [a['confidence'] for a in successful_analyses]
        
        # Weighted combination (higher weight for higher confidence)
        total_weight = sum(confidences)
        if total_weight > 0:
            combined_risk_score = sum(score * conf for score, conf in zip(risk_scores, confidences)) / total_weight
        else:
            combined_risk_score = sum(risk_scores) / len(risk_scores)
        
        # Determine overall risk level
        overall_risk_level = self._determine_risk_level(combined_risk_score)
        
        # Collect all fraud indicators
        all_indicators = []
        for analysis in successful_analyses:
            all_indicators.extend(analysis.get('fraud_indicators', []))
        
        # Create recommendation
        recommendation = self._create_recommendation(combined_risk_score, overall_risk_level)
        
        return {
            "overall_risk_level": overall_risk_level,
            "combined_risk_score": round(combined_risk_score, 3),
            "average_confidence": round(sum(confidences) / len(confidences), 3),
            "services_used": len(successful_analyses),
            "fraud_indicators": list(set(all_indicators)),  # Remove duplicates
            "individual_analyses": successful_analyses,
            "recommendation": recommendation,
            "analysis_timestamp": datetime.now().isoformat(),
            "document_type": document_type,
            "thresholds_used": self.thresholds
        }
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on combined score and thresholds"""
        if risk_score >= self.thresholds["high"]:
            return "HIGH"
        elif risk_score >= self.thresholds["medium"]:
            return "MEDIUM"
        elif risk_score >= self.thresholds["low"]:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _create_recommendation(self, risk_score: float, risk_level: str) -> Dict[str, Any]:
        """Create actionable recommendation based on fraud analysis"""
        
        recommendations = {
            "HIGH": {
                "action": "REJECT",
                "message": "Document shows high fraud indicators - reject immediately",
                "manual_review": True,
                "additional_verification": ["Request original documents", "Conduct video call verification"]
            },
            "MEDIUM": {
                "action": "MANUAL_REVIEW",
                "message": "Document requires manual review due to suspicious indicators",
                "manual_review": True,
                "additional_verification": ["Enhanced due diligence", "Additional document requests"]
            },
            "LOW": {
                "action": "ADDITIONAL_CHECKS",
                "message": "Document acceptable but recommend additional verification",
                "manual_review": False,
                "additional_verification": ["Cross-reference with database", "Basic verification calls"]
            },
            "MINIMAL": {
                "action": "APPROVE",
                "message": "Document appears authentic - approve with standard processing",
                "manual_review": False,
                "additional_verification": []
            }
        }
        
        base_recommendation = recommendations.get(risk_level, recommendations["MEDIUM"])
        base_recommendation["risk_score"] = risk_score
        
        return base_recommendation
    
    def _create_default_analysis(self, document_type: str, reason: str) -> Dict[str, Any]:
        """Create default analysis when AI services are unavailable"""
        
        return {
            "overall_risk_level": "UNKNOWN",
            "combined_risk_score": 0.0,
            "average_confidence": 0.0,
            "services_used": 0,
            "fraud_indicators": [reason],
            "individual_analyses": [],
            "recommendation": {
                "action": "MANUAL_REVIEW",
                "message": "AI fraud detection unavailable - manual review required",
                "manual_review": True,
                "additional_verification": ["Full manual document review"],
                "risk_score": 0.0
            },
            "analysis_timestamp": datetime.now().isoformat(),
            "document_type": document_type,
            "error": reason
        }

# Global fraud detection service
fraud_detector = FraudDetectionOrchestrator()
