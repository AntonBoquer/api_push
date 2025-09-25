from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Security scheme for bearer token
security = HTTPBearer()

async def verify_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the bearer token in the Authorization header
    """
    try:
        # Get the token from the Authorization header
        token = credentials.credentials
        
        # Compare with the expected bearer token
        if token != settings.BEARER_TOKEN:
            logger.warning(f"Invalid bearer token attempted: {token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid bearer token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info("Bearer token verified successfully")
        return token
        
    except Exception as e:
        logger.error(f"Error verifying bearer token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
