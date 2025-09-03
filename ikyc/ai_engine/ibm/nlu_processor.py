"""
IBM NLU Integration for Enhanced Document Analysis
"""

import json
from typing import Dict, List, Optional
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions, EntitiesOptions, KeywordsOptions, ConceptsOptions, CategoriesOptions, EmotionOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.ai_config import AIConfig

class IBMNLUProcessor:
    """IBM NLU for enhanced document understanding and fraud detection"""

    def __init__(self):
        """Initialize IBM NLU client"""
        try:
            authenticator = IAMAuthenticator(AIConfig.IBM_GRANITE_API_KEY)
            self.nlu = NaturalLanguageUnderstandingV1(
                version=AIConfig.IBM_NLU_VERSION,
                authenticator=authenticator
            )
            self.nlu.set_service_url(AIConfig.IBM_NLU_URL)
            self.is_available = True
        except Exception as e:
            print(f"Warning: IBM NLU not available: {e}")
            self.is_available = False

    def analyze_document_content(self, document_text: str, document_type: str) -> Dict:
        """
        Enhanced NLU analysis for KYC documents
        """
        if not self.is_available:
            return self._mock_nlu_analysis(document_text, document_type)

        try:
            # Configure NLU features for KYC analysis
            features = Features(
                sentiment=SentimentOptions(document=True),
                entities=EntitiesOptions(model='latest', limit=50),
                keywords=KeywordsOptions(limit=50, sentiment=True),
                concepts=ConceptsOptions(limit=50),
                categories=CategoriesOptions(),
                emotion=EmotionOptions(document=True)
            )

            response = self.nlu.analyze(
                text=document_text,
                features=features
            ).get_result()

            # Process and score results
            analysis_results = self._process_nlu_response(response, document_type)
            
            return {
                'success': True,
                'nlu_analysis': analysis_results,
                'ai_service': 'IBM_NLU',
                'document_type': document_type
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"NLU analysis failed: {str(e)}"
            }

    def _process_nlu_response(self, response: Dict, document_type: str) -> Dict:
        """Process NLU response for KYC-specific insights"""
        analysis = {
            'sentiment_analysis': {},
            'entity_consistency': {},
            'fraud_indicators': [],
            'document_quality_score': 0.0,
            'suspicious_patterns': []
        }

        # Sentiment Analysis
        if 'sentiment' in response:
            sentiment = response['sentiment']['document']
            analysis['sentiment_analysis'] = {
                'label': sentiment['label'],
                'score': sentiment['score'],
                'is_suspicious': sentiment['label'] == 'negative' and abs(sentiment['score']) > 0.7
            }
            
            if analysis['sentiment_analysis']['is_suspicious']:
                analysis['fraud_indicators'].append('suspicious_negative_sentiment')

        # Entity Consistency Analysis
        if 'entities' in response:
            entities = response['entities']
            analysis['entity_consistency'] = self._analyze_entity_consistency(entities, document_type)

        # Keyword Analysis for Fraud Detection
        if 'keywords' in response:
            keywords = response['keywords']
            suspicious_keywords = self._detect_suspicious_keywords(keywords)
            if suspicious_keywords:
                analysis['suspicious_patterns'].extend(suspicious_keywords)

        # Emotion Analysis (unusual emotional patterns can indicate fraud)
        if 'emotion' in response:
            emotions = response['emotion']['document']['emotion']
            high_emotions = [emotion for emotion, score in emotions.items() if score > 0.7]
            if high_emotions:
                analysis['fraud_indicators'].append(f'high_emotion_detected_{high_emotions}')

        # Calculate overall document quality score
        analysis['document_quality_score'] = self._calculate_quality_score(analysis)

        return analysis

    def _analyze_entity_consistency(self, entities: List[Dict], document_type: str) -> Dict:
        """Analyze entity consistency for fraud detection"""
        consistency_analysis = {
            'person_entities': [],
            'location_entities': [],
            'organization_entities': [],
            'inconsistency_score': 0.0,
            'potential_issues': []
        }

        for entity in entities:
            entity_type = entity.get('type', '').lower()
            entity_text = entity.get('text', '')
            confidence = entity.get('confidence', 0.0)

            if entity_type == 'person':
                consistency_analysis['person_entities'].append({
                    'text': entity_text,
                    'confidence': confidence
                })
            elif entity_type == 'location':
                consistency_analysis['location_entities'].append({
                    'text': entity_text,
                    'confidence': confidence
                })
            elif entity_type == 'organization':
                consistency_analysis['organization_entities'].append({
                    'text': entity_text,
                    'confidence': confidence
                })

        # Check for inconsistencies (multiple names, locations, etc.)
        if len(consistency_analysis['person_entities']) > 2:
            consistency_analysis['potential_issues'].append('multiple_person_entities')
            consistency_analysis['inconsistency_score'] += 0.3

        if len(consistency_analysis['location_entities']) > 3:
            consistency_analysis['potential_issues'].append('multiple_location_entities')  
            consistency_analysis['inconsistency_score'] += 0.2

        return consistency_analysis

    def _detect_suspicious_keywords(self, keywords: List[Dict]) -> List[str]:
        """Detect suspicious keywords that might indicate fraud"""
        suspicious_patterns = []
        suspicious_terms = [
            'fake', 'forged', 'duplicate', 'copy', 'scan', 'photocopy',
            'temporary', 'expired', 'invalid', 'cancelled'
        ]

        for keyword in keywords:
            keyword_text = keyword.get('text', '').lower()
            relevance = keyword.get('relevance', 0.0)
            
            if any(term in keyword_text for term in suspicious_terms) and relevance > 0.5:
                suspicious_patterns.append(f'suspicious_keyword_{keyword_text}')

        return suspicious_patterns

    def _calculate_quality_score(self, analysis: Dict) -> float:
        """Calculate overall document quality score based on NLU analysis"""
        base_score = 1.0
        
        # Deduct for fraud indicators
        base_score -= len(analysis['fraud_indicators']) * 0.15
        
        # Deduct for suspicious patterns
        base_score -= len(analysis['suspicious_patterns']) * 0.1
        
        # Deduct for entity inconsistencies
        base_score -= analysis['entity_consistency'].get('inconsistency_score', 0.0)
        
        # Deduct for negative sentiment
        if analysis['sentiment_analysis'].get('is_suspicious', False):
            base_score -= 0.2

        return max(0.0, base_score)

    def _mock_nlu_analysis(self, document_text: str, document_type: str) -> Dict:
        """Mock NLU analysis for testing"""
        return {
            'success': True,
            'nlu_analysis': {
                'sentiment_analysis': {
                    'label': 'neutral',
                    'score': 0.1,
                    'is_suspicious': False
                },
                'entity_consistency': {
                    'person_entities': [{'text': 'Rajesh Kumar', 'confidence': 0.95}],
                    'location_entities': [{'text': 'Mumbai', 'confidence': 0.88}],
                    'organization_entities': [],
                    'inconsistency_score': 0.0,
                    'potential_issues': []
                },
                'fraud_indicators': [],
                'document_quality_score': 0.9,
                'suspicious_patterns': []
            },
            'ai_service': 'Mock_IBM_NLU'
        }

    def cross_validate_with_granite(self, granite_results: Dict, nlu_results: Dict) -> Dict:
        """Cross-validate Granite AI and NLU results"""
        try:
            # Extract scores
            granite_fraud_score = granite_results.get('fraud_score', 0.5)
            nlu_quality_score = nlu_results.get('nlu_analysis', {}).get('document_quality_score', 0.5)
            
            # NLU fraud indicators
            nlu_fraud_indicators = nlu_results.get('nlu_analysis', {}).get('fraud_indicators', [])
            nlu_fraud_score = len(nlu_fraud_indicators) * 0.2  # Convert indicators to score
            
            # Calculate consensus
            consensus_fraud_score = (granite_fraud_score + nlu_fraud_score + (1.0 - nlu_quality_score)) / 3
            
            # Determine agreement
            score_diff = abs(granite_fraud_score - nlu_fraud_score)
            agreement_level = 'HIGH' if score_diff < 0.2 else 'MEDIUM' if score_diff < 0.4 else 'LOW'
            
            return {
                'success': True,
                'consensus_analysis': {
                    'granite_fraud_score': granite_fraud_score,
                    'nlu_fraud_score': nlu_fraud_score,
                    'nlu_quality_score': nlu_quality_score,
                    'consensus_fraud_score': consensus_fraud_score,
                    'agreement_level': agreement_level,
                    'combined_indicators': granite_results.get('fraud_indicators', []) + nlu_fraud_indicators
                },
                'validation_enhanced': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Cross-validation failed: {str(e)}"
            }
