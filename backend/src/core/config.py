"""Configuration settings for the application"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/contract_db")

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_USERNAME = os.getenv("REDIS_USERNAME", None)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Celery Configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Application Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 52428800))  # 50MB in bytes

# API Configuration
API_V1_STR = "/api/v1"
PROJECT_NAME = "Contract Intelligence Parser"
PROJECT_DESCRIPTION = "Automated contract analysis and data extraction system"
PROJECT_VERSION = "1.0.0"

# File Upload Configuration
ALLOWED_FILE_TYPES = {".pdf"}
UPLOAD_DIR = "uploads"

# Scoring Configuration
SCORING_WEIGHTS = {
    "financial_completeness": 30,
    "party_identification": 25,
    "payment_terms_clarity": 20,
    "sla_definition": 15,
    "contact_information": 10,
}
