import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # API
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    
    # Model
    LLM_MODEL = "models/gemini-2.5-flash"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///resume_matcher.db")
    
    # Scoring
    MAX_SCORE = 100
    MIN_SCORE = 0
    
    # UI
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    # Limits
    MAX_RESUME_LENGTH = 10000
    MAX_JD_LENGTH = 5000
    MAX_RETRIES = 3
