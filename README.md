# iKYC-TeamVagabond-Hackverse2025
Team Vagabond's submission for Hackverse 2025 - a 36 hour hackathon hosted by MIT Bengaluru in collaboration with IBM, AWS and 1M1B. This project, a KYC automation, secured 2nd place in the Fintech category of the competition.

# NOTE: Keys of IBM and AWS services have expired; real-world implementation must include connection to govt. database for validation

Project: IntelliKYC - AI Powered KYC Verification
- Multi-component system: Backend (FastAPI), Frontend (Streamlit), Redis backend.
- Uses multi-engine OCR: EasyOCR, OCR.space, Mock OCR as fallback.
- Integrates IBM Granite AI for semantic and fraud evaluations.
- Uses IBM NLU for advanced document content analysis.
- Uses AWS Bedrock Nova models for document authenticity and risk.
- Features include document digitization, fraud detection, and face liveness verification.
- Validation pipeline (personal info, document, contact, face) with multi-step sequential processing.
- Data managed via Redis including user, Aadhaar, PAN, sessions, OTPs, blacklists.
- Includes test harnesses for OCR engines, document pipeline, and live face tests.
- Dockerized with separate containers for backend, frontend, and Redis.
- Configuration via environment variables and structured python config files.
- Auditor and validation logic includes: fuzzy matching, field-level validations, semantic analysis.
- Capable to integrate multi-modal AI including image + text processing.
- Focus on Indian document formats, stringent validation, and compliance.
- Immutably records KYC verifications—each institution’s verification is stored as a tamper-proof transaction on the blockchain.
- Preserves privacy with zero-knowledge proofs—all customer attestations are validated and shared across banks without revealing any personal data.


System Dependencies:
- Python packages: fastapi, uvicorn, streamlit, redis, requests, pillow, numpy, opencv, mediapipe, easyocr, boto3, ibm-watson.
- Requires Redis server running (can be dockerized).

Usage Notes:
- OCR attempts multiple engines sequentially for best accuracy.
- Fraud and risk scoring integrates several AI sources.
- Face verification uses MediaPipe and custom logic.
- OTP management via Redis with retry limits.
- Supports mock modes for offline and testing scenarios.
- Immutable records of KYC transactions via blockchain with zero-knowledge proofs

The above encapsulates the core project setup, dependencies, and architectural highlights.
