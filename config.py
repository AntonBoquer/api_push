import os
from dotenv import load_dotenv

# Load environment variables (only if .env file exists)
try:
    load_dotenv()
except:
    pass  # In production (Vercel), environment variables are set directly

class Settings:
    # Supabase configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Security - Only Bearer Token
    BEARER_TOKEN: str = os.getenv("BEARER_TOKEN")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Bus Occupancy API"
    
    def __init__(self):
        # Log configuration (for debugging)
        if self.ENVIRONMENT == "development":
            print(f"SUPABASE_URL: {self.SUPABASE_URL[:20]}..." if self.SUPABASE_URL else "SUPABASE_URL: Not set")
            print(f"BEARER_TOKEN: {self.BEARER_TOKEN[:10]}..." if self.BEARER_TOKEN else "BEARER_TOKEN: Not set")
            print(f"ENVIRONMENT: {self.ENVIRONMENT}")
    
    class Config:
        case_sensitive = True

settings = Settings()
