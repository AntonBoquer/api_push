import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Supabase configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Security - Only Bearer Token
    BEARER_TOKEN: str = os.getenv("BEARER_TOKEN", "your-bearer-token")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Bus Occupancy API"
    
    class Config:
        case_sensitive = True

settings = Settings()
