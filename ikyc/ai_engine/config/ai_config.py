"""
AI Engine Configuration for IntelliKYC (Updated for Nova Models + OCR Engines)
"""

import os
from typing import Dict, List

class AIConfig:
    """Configuration for AI services"""

    # IBM Watson Configuration (Keep existing)
    IBM_WATSON_API_KEY = os.getenv('IBM_WATSON_API_KEY', 'RNe_5QO_GI79hw1677ol-MtYEsJX6i16yNKfCFRzA2QI')
    IBM_WATSON_URL = os.getenv('IBM_WATSON_URL', 'https://api.us-south.watson.cloud.ibm.com')
    IBM_WATSON_VERSION = '2021-05-13'
    
    # IBM NLU Configuration (Add this)
    IBM_NLU_VERSION = '2021-05-13'
    IBM_NLU_URL = 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com'

    # IBM Granite Configuration (Keep existing)
    IBM_GRANITE_API_KEY = os.getenv('IBM_GRANITE_API_KEY', 'RNe_5QO_GI79hw1677ol-MtYEsJX6i16yNKfCFRzA2QI')
    IBM_PROJECT_ID = os.getenv('IBM_PROJECT_ID', '942e8fb2-25d6-4f82-bec9-d16e62de5433')
    IBM_GRANITE_13B_MODEL = 'ibm/granite-13b-instruct-v2'
    IBM_GRANITE_20B_MODEL = 'ibm/granite-20b-multilingual'
    IBM_WATSONX_URL = 'https://us-south.ml.cloud.ibm.com/ml/v1'

    # AWS Bedrock Configuration (UPDATED FOR NOVA MODELS)
    AWS_BEDROCK_REGION = os.getenv('AWS_BEDROCK_REGION', 'us-east-1')
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID','AKIA3QHPZMDPRPQHXZ5Q') # Required - remove default
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY','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') # Required - remove default
    AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN') # Optional for temporary credentials

    # 🆕 Available Nova Models (Your Available Models)
    AWS_BEDROCK_NOVA_MODELS = {
        # Text + Vision Models (PERFECT for document analysis)
        'nova_pro': 'amazon.nova-pro-v1:0', # 🏆 BEST for complex document analysis
        'nova_lite': 'amazon.nova-lite-v1:0', # 💰 Cost-effective alternative
        'nova_micro': 'amazon.nova-micro-v1:0', # 🚀 Text-only, fastest & cheapest
        # Embeddings Model V2 (You have this!)
        'embeddings_v2': 'amazon.titan-embed-text-v2:0', # 🔍 For semantic search/RAG
    }

    # PRIMARY MODEL FOR DOCUMENT ANALYSIS - Nova Pro (Multimodal!)
    AWS_BEDROCK_NOVA_MODEL = AWS_BEDROCK_NOVA_MODELS['nova_pro']
    # FALLBACK MODEL FOR SIMPLE TASKS - Nova Lite
    AWS_BEDROCK_NOVA_LITE_MODEL = AWS_BEDROCK_NOVA_MODELS['nova_lite']
    # EMBEDDINGS MODEL - Titan V2
    AWS_BEDROCK_EMBEDDINGS_MODEL = AWS_BEDROCK_NOVA_MODELS['embeddings_v2']

    # 🔄 Legacy Titan Model (for backwards compatibility)
    AWS_BEDROCK_TITAN_MODEL = AWS_BEDROCK_NOVA_MODEL # Point to Nova Pro

    # 🎛️ Nova Model Parameters (Optimized for document analysis)
    NOVA_MAX_TOKENS = 8192 # Nova Pro supports long context
    NOVA_TEMPERATURE = 0.1 # Low for consistent analysis
    NOVA_TOP_P = 0.9

    # 🖼️ Nova Pro supports both text and images!
    NOVA_MULTIMODAL = True # Enable image + text processing
    NOVA_MAX_IMAGE_SIZE = 25 # MB - for document images

    # 📊 Embeddings V2 Parameters
    TITAN_EMBEDDINGS_DIMENSIONS = 512 # Good balance: accuracy vs cost
    TITAN_NORMALIZE_EMBEDDINGS = True

    # 🆕 OCR ENGINE CONFIGURATION (MISSING - ADD THIS)
    # OCR Engines in order of preference
    OCR_ENGINES = ['easyocr', 'ocr_space', 'mock']
    
    # OCR.space API Configuration
    OCR_SPACE_API_KEY = os.getenv('OCR_SPACE_API_KEY', 'K87844805588957')  # Get free key at https://ocr.space/ocrapi
    OCR_SPACE_URL = 'https://api.ocr.space/parse/image'
    
    # OCR Processing Parameters
    OCR_MAX_IMAGE_SIZE_MB = 5  # Maximum image size for OCR processing
    OCR_SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png', 'pdf', 'bmp', 'gif']
    OCR_DEFAULT_LANGUAGE = 'eng'  # English language code
    OCR_CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence for accepting OCR results

    # Document Processing Settings (Keep existing)
    SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png', 'pdf']
    MAX_FILE_SIZE_MB = 10
    FRAUD_DETECTION_THRESHOLD = 0.6

    # Fraud Detection Parameters (Keep existing)
    FRAUD_INDICATORS = {
        'low_ocr_confidence': 0.5,
        'inconsistent_fonts': 0.7,
        'image_quality_issues': 0.6,
        'suspicious_patterns': 0.8
    }

    # Document Field Mappings (Keep existing)
    AADHAAR_FIELDS = [
        'aadhaar_number', 'name', 'date_of_birth', 'gender',
        'address', 'father_name', 'issue_date'
    ]

    PAN_FIELDS = [
        'pan_number', 'name', 'father_name', 'date_of_birth',
        'signature', 'issue_date'
    ]

    # 🆕 Enhanced Prompts for Nova Models
    NOVA_FRAUD_DETECTION_PROMPT = """
You are an expert document fraud detection AI. Analyze this document for potential fraud indicators.

DOCUMENT ANALYSIS:
- Document Text: {document_text}
- OCR Confidence: {ocr_confidence}
- Document Type: {document_type}

ANALYSIS REQUIREMENTS:
1. Document authenticity assessment (0-1 score)
2. Information consistency check (0-1 score)
3. Fraud probability calculation (0-1 score)
4. Overall risk score (0-1 score)
5. Specific risk factors identified
6. Actionable recommendations

RESPONSE FORMAT: Return ONLY valid JSON with this structure:
{{
    "document_authenticity_risk": <float>,
    "information_consistency_risk": <float>,
    "fraud_probability": <float>,
    "overall_risk_score": <float>,
    "risk_factors": ["list", "of", "specific", "risks"],
    "recommendations": ["list", "of", "recommendations"],
    "confidence_level": "HIGH|MEDIUM|LOW",
    "analysis_reasoning": "Brief explanation of the assessment"
}}
"""

    # 🔄 Legacy prompts (for backwards compatibility)
    FRAUD_DETECTION_PROMPT = NOVA_FRAUD_DETECTION_PROMPT

    FIELD_EXTRACTION_PROMPT = """
Extract structured information from this {document_type} document.

DOCUMENT TEXT: {document_text}
REQUIRED FIELDS: {required_fields}

Return ONLY valid JSON with extracted fields. Use null for missing fields.
"""

    # 🆕 Nova Multimodal Prompt (NEW CAPABILITY!)
    NOVA_MULTIMODAL_ANALYSIS_PROMPT = """
Analyze this document using BOTH the extracted text and the document image.

EXTRACTED TEXT: {document_text}
DOCUMENT TYPE: {document_type}

Provide comprehensive analysis including:
1. Visual authenticity assessment
2. Text-image consistency check
3. Document quality evaluation
4. Fraud indicators from both modalities
5. Overall risk assessment

Return detailed JSON analysis with the same structure as fraud detection prompt.
"""
