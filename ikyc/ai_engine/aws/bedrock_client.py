"""
AWS Bedrock Nova Integration for IntelliKYC Document Analysis
Enhanced with multimodal capabilities and improved error handling
"""

import json
import boto3
import base64
from typing import Dict, Optional
import sys
import os
from botocore.exceptions import ClientError, NoCredentialsError

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.ai_config import AIConfig

class BedrockTitanProcessor:  # Keep class name for backwards compatibility
    """AWS Bedrock Nova for advanced multimodal document analysis"""

    def __init__(self):
        """Initialize Bedrock Nova client with comprehensive error handling"""
        self.bedrock_client = None
        
        # Nova model configurations
        self.nova_model_id = AIConfig.AWS_BEDROCK_NOVA_MODEL  # Nova Pro
        self.nova_lite_model_id = AIConfig.AWS_BEDROCK_NOVA_LITE_MODEL  # Nova Lite
        self.embeddings_model_id = AIConfig.AWS_BEDROCK_EMBEDDINGS_MODEL  # Titan V2
        
        # Legacy compatibility
        self.model_id = self.nova_model_id
        
        self.is_available = False
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Bedrock client with comprehensive error handling"""
        try:
            # Check credentials
            if not AIConfig.AWS_ACCESS_KEY or not AIConfig.AWS_SECRET_KEY:
                print("❌ AWS credentials not found in environment variables")
                print("🔧 Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
                return

            # Build client parameters
            client_params = {
                'service_name': 'bedrock-runtime',
                'region_name': AIConfig.AWS_BEDROCK_REGION,
                'aws_access_key_id': AIConfig.AWS_ACCESS_KEY,
                'aws_secret_access_key': AIConfig.AWS_SECRET_KEY
            }

            # Add session token if available (for temporary credentials)
            if AIConfig.AWS_SESSION_TOKEN:
                client_params['aws_session_token'] = AIConfig.AWS_SESSION_TOKEN

            # Initialize client
            self.bedrock_client = boto3.client(**client_params)
            
            # Test connection with Nova
            self._test_connection()
            
            self.is_available = True
            print("✅ AWS Bedrock Nova client initialized successfully")
            print(f"🎯 Primary Model: Nova Pro ({self.nova_model_id})")
            print(f"💰 Fallback Model: Nova Lite ({self.nova_lite_model_id})")
            print(f"🔍 Embeddings Model: Titan V2 ({self.embeddings_model_id})")
            print(f"🌍 Region: {AIConfig.AWS_BEDROCK_REGION}")

        except NoCredentialsError:
            print("❌ AWS credentials not found or invalid")
            self.is_available = False
        except Exception as e:
            print(f"❌ Error initializing Bedrock Nova: {e}")
            self.is_available = False

    def _test_connection(self):
        """Test Bedrock connection with Nova Lite (cheaper for testing)"""
        try:
            test_response = self._call_nova_text("Connection test", use_lite=True)
            if not test_response['success']:
                raise Exception(f"Test failed: {test_response['error']}")
            print("✅ Bedrock Nova connection test successful")
        except Exception as e:
            print(f"⚠️ Connection test failed: {e}")
            # Don't raise here - allow fallback to mock mode

    def analyze_document_risk(self, document_text: str, ocr_confidence: float, 
                            document_type: str = 'document') -> Dict:
        """
        🆕 Enhanced document risk analysis using Nova Pro
        """
        if not self.is_available:
            return self._mock_risk_analysis(document_text, ocr_confidence)

        try:
            prompt = AIConfig.NOVA_FRAUD_DETECTION_PROMPT.format(
                document_text=document_text,
                ocr_confidence=ocr_confidence,
                document_type=document_type
            )

            # Use Nova Pro for complex analysis
            response = self._call_nova_text(prompt, use_lite=False)

            if response['success']:
                risk_analysis = self._parse_risk_response(response['response_text'])
                return {
                    'success': True,
                    'risk_analysis': risk_analysis,
                    'ai_model': 'AWS_Bedrock_Nova_Pro',
                    'model_generation': 'Nova_2024',
                    'multimodal_capable': True
                }
            else:
                # Fallback to Nova Lite if Pro fails
                return self._fallback_analysis(document_text, ocr_confidence, response['error'])

        except Exception as e:
            return {
                'success': False,
                'error': f"Nova risk analysis failed: {str(e)}"
            }
        
    

    def validate_document_authenticity(self, document_data: Dict) -> Dict:
        """🆕 Enhanced document authenticity validation using Nova"""
        if not self.is_available:
            return self._mock_authenticity_validation(document_data)

        try:
            prompt = f"""
Validate the authenticity of this financial identity document using advanced analysis:

DOCUMENT DETAILS:
- Extracted Text: {document_data.get('extracted_text', '')}
- OCR Confidence: {document_data.get('ocr_confidence', 0.0)}
- Image Quality Metrics: {document_data.get('image_quality', {})}
- Extracted Fields: {document_data.get('field_extractions', {})}

VALIDATION REQUIREMENTS:
1. Document format compliance check
2. Cross-field data consistency analysis
3. Expected vs actual information pattern matching
4. Digital/physical tampering indicators
5. Authenticity confidence scoring

Return JSON with authenticity assessment.
"""

            response = self._call_nova_text(prompt)

            if response['success']:
                authenticity_analysis = self._parse_authenticity_response(response['response_text'])
                return {
                    'success': True,
                    'authenticity_analysis': authenticity_analysis,
                    'ai_model': 'AWS_Bedrock_Nova_Pro',
                    'validation_enhanced': True
                }
            else:
                return {'success': False, 'error': response['error']}

        except Exception as e:
            return {
                'success': False,
                'error': f"Nova authenticity validation failed: {str(e)}"
            }

    def analyze_document_multimodal(self, document_text: str, image_data: bytes = None) -> Dict:
        """
        🆕 NEW CAPABILITY: Multimodal document analysis using Nova Pro
        This is a unique capability that Titan doesn't have!
        """
        if not self.is_available:
            return {'success': False, 'error': 'Nova not available - multimodal analysis requires Nova Pro'}

        try:
            # Convert image to base64 if provided
            image_base64 = None
            if image_data:
                image_base64 = base64.b64encode(image_data).decode('utf-8')

            prompt = AIConfig.NOVA_MULTIMODAL_ANALYSIS_PROMPT.format(
                document_text=document_text,
                document_type='identity_document'
            )

            # Use Nova Pro's multimodal capability
            response = self._call_nova_multimodal(prompt, image_base64)

            if response['success']:
                return {
                    'success': True,
                    'multimodal_analysis': self._parse_risk_response(response['response_data']),
                    'ai_model': 'AWS_Bedrock_Nova_Pro_Multimodal',
                    'capabilities_used': ['text_analysis', 'image_analysis', 'cross_modal_validation'],
                    'unique_to_nova': True
                }
            else:
                return {'success': False, 'error': response['error']}

        except Exception as e:
            return {
                'success': False,
                'error': f"Nova multimodal analysis failed: {str(e)}"
            }

    def get_document_embeddings(self, text: str, dimensions: int = None) -> Dict:
        """🆕 Generate embeddings using Titan V2 (you have this!)"""
        if not self.is_available:
            return {'success': False, 'error': 'Bedrock not available'}

        try:
            embed_dimensions = dimensions or AIConfig.TITAN_EMBEDDINGS_DIMENSIONS
            
            body = json.dumps({
                'inputText': text,
                'dimensions': embed_dimensions,
                'normalize': AIConfig.TITAN_NORMALIZE_EMBEDDINGS
            })

            response = self.bedrock_client.invoke_model(
                modelId=self.embeddings_model_id,
                contentType='application/json',
                accept='application/json',
                body=body
            )

            response_body = json.loads(response['body'].read())
            
            return {
                'success': True,
                'embeddings': response_body.get('embedding', []),
                'dimensions': embed_dimensions,
                'model': 'Titan_Embeddings_V2',
                'text_length': len(text)
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Embeddings generation failed: {str(e)}"
            }
        

    


    def _call_nova_text(self, prompt: str, use_lite: bool = False) -> Dict:
        """Call Nova model for text generation"""
        try:
            model_id = self.nova_lite_model_id if use_lite else self.nova_model_id
            
            # Nova API format
            body = json.dumps({
                'messages': [
                    {
                        'role': 'user',
                        'content': [{'text': prompt}]
                    }
                ],
                'inferenceConfig': {
                    'maxTokens': AIConfig.NOVA_MAX_TOKENS,
                    'temperature': AIConfig.NOVA_TEMPERATURE,
                    'topP': AIConfig.NOVA_TOP_P
                }
            })

            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                contentType='application/json',
                accept='application/json',
                body=body
            )

            response_body = json.loads(response['body'].read())
            
            # Extract text from Nova response
            if 'output' in response_body and 'message' in response_body['output']:
                content = response_body['output']['message']['content']
                if content and len(content) > 0:
                    output_text = content[0].get('text', '')
                else:
                    raise Exception("No content in response")
            else:
                raise Exception("Unexpected response format")

            return {
                'success': True,
                'response_text': output_text,
                'model_used': 'nova_lite' if use_lite else 'nova_pro'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _call_nova_multimodal(self, prompt: str, image_base64: str = None) -> Dict:
        """🆕 Call Nova Pro with both text and image (multimodal capability)"""
        try:
            # Prepare content array
            content = [{'text': prompt}]
            
            # Add image if provided
            if image_base64:
                content.append({
                    'image': {
                        'format': 'jpeg',  # or determine from image
                        'source': {'bytes': image_base64}
                    }
                })

            body = json.dumps({
                'messages': [
                    {
                        'role': 'user',
                        'content': content
                    }
                ],
                'inferenceConfig': {
                    'maxTokens': AIConfig.NOVA_MAX_TOKENS,
                    'temperature': AIConfig.NOVA_TEMPERATURE,
                    'topP': AIConfig.NOVA_TOP_P
                }
            })

            response = self.bedrock_client.invoke_model(
                modelId=self.nova_model_id,  # Use Nova Pro for multimodal
                contentType='application/json',
                accept='application/json',
                body=body
            )

            response_body = json.loads(response['body'].read())
            
            # Extract response
            if 'output' in response_body and 'message' in response_body['output']:
                content = response_body['output']['message']['content']
                if content and len(content) > 0:
                    output_text = content[0].get('text', '')
                else:
                    raise Exception("No content in multimodal response")
            else:
                raise Exception("Unexpected multimodal response format")

            return {
                'success': True,
                'response_data': output_text,
                'modalities_used': ['text', 'image'] if image_base64 else ['text']
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _fallback_analysis(self, document_text: str, ocr_confidence: float, error: str) -> Dict:
        """Fallback to Nova Lite if Nova Pro fails"""
        try:
            print(f"⚠️ Nova Pro failed ({error}), trying Nova Lite...")
            
            simplified_prompt = f"""
Analyze this document for fraud risk:
Text: {document_text}
OCR Confidence: {ocr_confidence}

Return JSON with overall_risk_score (0-1) and risk_factors array.
"""
            
            response = self._call_nova_text(simplified_prompt, use_lite=True)
            
            if response['success']:
                risk_analysis = self._parse_risk_response(response['response_text'])
                return {
                    'success': True,
                    'risk_analysis': risk_analysis,
                    'ai_model': 'AWS_Bedrock_Nova_Lite',
                    'fallback_used': True,
                    'original_error': error
                }
            else:
                return self._mock_risk_analysis(document_text, ocr_confidence)
                
        except Exception as e:
            return self._mock_risk_analysis(document_text, ocr_confidence)

    def _parse_risk_response(self, response_text: str) -> Dict:
        """Parse Nova risk analysis response with improved error handling"""
        try:
            # Try to parse JSON response
            parsed = json.loads(response_text)
            
            # Validate required fields and add defaults if missing
            required_fields = {
                'document_authenticity_risk': 0.2,
                'information_consistency_risk': 0.15,
                'fraud_probability': 0.1,
                'overall_risk_score': 0.15,
                'risk_factors': ['none_identified'],
                'recommendations': ['proceed_with_standard_verification'],
                'confidence_level': 'MEDIUM'
            }
            
            for field, default_value in required_fields.items():
                if field not in parsed:
                    parsed[field] = default_value
                    
            return parsed
            
        except json.JSONDecodeError:
            # If JSON parsing fails, return safe defaults
            return {
                'document_authenticity_risk': 0.3,
                'information_consistency_risk': 0.25,
                'fraud_probability': 0.2,
                'overall_risk_score': 0.25,
                'risk_factors': ['parsing_error', 'response_format_issue'],
                'recommendations': ['manual_review_required'],
                'confidence_level': 'LOW',
                'parsing_error': True,
                'raw_response': response_text[:200] + "..." if len(response_text) > 200 else response_text
            }

    def _parse_authenticity_response(self, response_text: str) -> Dict:
        """Parse authenticity validation response with error handling"""
        try:
            return json.loads(response_text)
        except:
            return {
                'authenticity_score': 0.75,
                'format_compliance': True,
                'data_consistency': True,
                'forgery_indicators': ['parsing_error'],
                'confidence_level': 'MEDIUM',
                'parsing_error': True
            }

    def _mock_risk_analysis(self, document_text: str, ocr_confidence: float) -> Dict:
        """Enhanced mock analysis for testing"""
        base_risk = max(0.1, 1.0 - ocr_confidence)
        
        return {
            'success': True,
            'risk_analysis': {
                'document_authenticity_risk': base_risk,
                'information_consistency_risk': base_risk * 0.8,
                'fraud_probability': base_risk * 0.6,
                'overall_risk_score': base_risk,
                'risk_factors': ['low_ocr_confidence'] if ocr_confidence < 0.7 else ['none_identified'],
                'recommendations': ['manual_review'] if base_risk > 0.5 else ['proceed_with_verification'],
                'confidence_level': 'HIGH' if base_risk < 0.3 else 'MEDIUM'
            },
            'ai_model': 'Mock_Nova_Pro',
            'mock_mode': True
        }

    def _mock_authenticity_validation(self, document_data: Dict) -> Dict:
        """Enhanced mock authenticity validation"""
        has_fields = bool(document_data.get('field_extractions'))
        good_quality = document_data.get('image_quality', {}).get('quality_score', 0.5) > 0.7
        authenticity_score = 0.9 if has_fields and good_quality else 0.6

        return {
            'success': True,
            'authenticity_analysis': {
                'authenticity_score': authenticity_score,
                'format_compliance': has_fields,
                'data_consistency': good_quality,
                'forgery_indicators': [] if authenticity_score > 0.7 else ['quality_issues'],
                'confidence_level': 'HIGH' if authenticity_score > 0.8 else 'MEDIUM'
            },
            'ai_model': 'Mock_Nova_Pro',
            'mock_mode': True
        }

    # 🔄 Keep existing methods for backwards compatibility
    def cross_validate_with_ibm(self, ibm_results: Dict, bedrock_analysis: Dict) -> Dict:
        """Cross-validate IBM and AWS Bedrock results (unchanged for compatibility)"""
        try:
            # Extract scores from both analyses
            ibm_fraud_score = ibm_results.get('fraud_score', 0.5)
            ibm_confidence = ibm_results.get('ai_analysis', {}).get('confidence', 0.5)
            bedrock_risk_score = bedrock_analysis.get('risk_analysis', {}).get('overall_risk_score', 0.5)
            bedrock_authenticity = bedrock_analysis.get('authenticity_analysis', {}).get('authenticity_score', 0.5)

            # Calculate consensus scores
            consensus_fraud_score = (ibm_fraud_score + bedrock_risk_score) / 2
            consensus_authenticity = (ibm_confidence + bedrock_authenticity) / 2

            # Determine agreement level
            fraud_score_diff = abs(ibm_fraud_score - bedrock_risk_score)
            agreement_level = 'HIGH' if fraud_score_diff < 0.2 else 'MEDIUM' if fraud_score_diff < 0.4 else 'LOW'

            # Final decision logic
            if agreement_level == 'HIGH':
                final_decision = 'APPROVED' if consensus_fraud_score < 0.3 else 'REJECTED' if consensus_fraud_score > 0.7 else 'MANUAL_REVIEW'
            else:
                final_decision = 'MANUAL_REVIEW' # Low agreement requires human review

            return {
                'success': True,
                'consensus_analysis': {
                    'fraud_score': consensus_fraud_score,
                    'authenticity_score': consensus_authenticity,
                    'agreement_level': agreement_level,
                    'final_decision': final_decision
                },
                'individual_results': {
                    'ibm_analysis': ibm_results,
                    'bedrock_analysis': bedrock_analysis,
                    'nova_enhanced': True
                },
                'cross_validation': 'completed'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Cross-validation failed: {str(e)}"
            }
        
    

    # 🔄 Legacy method names for backwards compatibility
    def _call_bedrock_titan(self, prompt: str) -> Dict:
        """Legacy method - now calls Nova"""
        return self._call_nova_text(prompt)
