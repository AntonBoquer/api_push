from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
import uuid
import time
from datetime import datetime
from typing import Any
import httpx

# Local imports
from config import settings
from auth import verify_bearer_token
from models import APIResponse, PushPayload, BusOccupancyData, HealthCheck
from database import supabase_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global persistent HTTP client for connection pooling
# This will be initialized on app startup and reused across all requests
http_client: httpx.AsyncClient = None

# Webhook notification function
async def notify_frontend_of_new_data(record_id, data):
    """
    Send webhook notification to frontend deployment about new detection data
    Uses the global persistent http_client for connection reuse
    """
    start_time = time.time()
    
    # Configure your frontend webhook URL
    FRONTEND_WEBHOOK_URL = os.getenv("FRONTEND_WEBHOOK_URL", "https://your-frontend-deployment.vercel.app/api/webhook/new-data")
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-webhook-secret")
    
    try:
        webhook_payload = {
            "event": "new_detection_data",
            "record_id": record_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "secret": WEBHOOK_SECRET
        }
        
        # Use global persistent client instead of creating a new one
        response = await http_client.post(
            FRONTEND_WEBHOOK_URL,
            json=webhook_payload,
            headers={"Content-Type": "application/json"}
        )
            
        if response.status_code == 200:
            duration = time.time() - start_time
            logger.info(f"✅ Webhook COMPLETED successfully for record {record_id} in {duration:.2f}s")
        else:
            duration = time.time() - start_time
            logger.warning(f"❌ Webhook FAILED for record {record_id} in {duration:.2f}s: {response.status_code}")
            
    except httpx.TimeoutException as e:
        duration = time.time() - start_time
        logger.error(f"⏰ Webhook TIMEOUT for record {record_id} in {duration:.2f}s: {e}")
        # Don't raise exception in background task to avoid affecting main request
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"💥 Webhook ERROR for record {record_id} in {duration:.2f}s: {e}")
        # Don't raise exception in background task to avoid affecting main request

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for handling push requests with bearer token authentication",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event: Initialize persistent HTTP client
@app.on_event("startup")
async def startup_event():
    """
    Initialize the global HTTP client with connection pooling on app startup
    This allows connections to be reused, reducing latency by 300-500ms per request
    """
    global http_client
    
    # Configure HTTP client with optimized settings
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(3.0),  # 3 second timeout
        limits=httpx.Limits(
            max_connections=100,      # Maximum number of connections in the pool
            max_keepalive_connections=20,  # Keep 20 connections alive for reuse
            keepalive_expiry=30.0     # Keep connections alive for 30 seconds
        ),
        http2=True,  # Enable HTTP/2 for better performance (optional)
        follow_redirects=True
    )
    logger.info("✅ Persistent HTTP client initialized with connection pooling")

# Shutdown event: Close persistent HTTP client
@app.on_event("shutdown")
async def shutdown_event():
    """
    Gracefully close the HTTP client on app shutdown
    """
    global http_client
    if http_client:
        await http_client.aclose()
        logger.info("✅ Persistent HTTP client closed")

@app.get("/")
async def root():
    """Root endpoint"""
    return APIResponse(
        success=True,
        message="Bus Occupancy API is running",
        data={"version": "1.0.0", "environment": settings.ENVIRONMENT}
    )

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_connected = True
        try:
            supabase_client.get_client()
        except Exception:
            db_connected = False
        
        return HealthCheck(
            status="healthy" if db_connected else "degraded",
            database_connected=db_connected
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )

@app.post(f"{settings.API_V1_PREFIX}/push", response_model=APIResponse)
async def push_data(
    payload: PushPayload,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_bearer_token)
):
    try:
        # Use existing UUID or generate a new one (minimal logging)
        record_uuid = payload.uuid or str(uuid.uuid4())

        # Use `payload.data` if it exists; otherwise use the full model dict
        if payload.data:
            data_content = payload.data
        else:
            data_content = payload.model_dump(exclude_none=True, exclude={"metadata"})

        # Optimize JSON creation (avoid datetime conversion overhead)
        now = datetime.utcnow()
        json_data = {
            "uuid": record_uuid,
            "received_at": now.isoformat(),
            "data": data_content,
            "metadata": payload.metadata or {},
            "processed": True
        }

        db_insert_start = time.time()
        try:
            logger.info(f"🔵 Starting database insert for UUID {record_uuid}")
            result = await supabase_client.insert_data("push_requests", json_data)
            db_duration = time.time() - db_insert_start
            
            if result:
                logger.info(f"✅ Database insert completed in {db_duration:.3f}s")
            else:
                logger.warning(f"⚠️ Database insert returned None (Supabase not configured)")

            # Schedule webhook notification in background (non-blocking)
            if result and "detection_results" in data_content:
                record_id = result.data[0]["id"]
                # Add to background tasks - API responds immediately without waiting
                background_tasks.add_task(
                    notify_frontend_of_new_data,
                    record_id=record_id,
                    data={**data_content, "uuid": record_uuid}
                )
                logger.info(f"📤 Webhook scheduled for record {record_id} (will process in background)")
            elif not result:
                logger.warning("Supabase not configured - skipping webhook notification")

        except Exception as db_error:
            db_duration = time.time() - db_insert_start
            logger.error(f"❌ Database error after {db_duration:.3f}s: {db_error}")
            logger.exception(db_error)  # Print full traceback
            json_data["database_error"] = str(db_error)

        return APIResponse(
            success=True,
            message="Data processed successfully",
            data={
                "processed_data": json_data,
                "payload_size": len(str(data_content))
            }
        )

    except Exception as e:
        logger.error(f"Error processing push request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process request: {str(e)}"
        )




@app.post(f"{settings.API_V1_PREFIX}/bus-occupancy", response_model=APIResponse)
async def update_bus_occupancy(
    occupancy_data: BusOccupancyData,
    token: str = Depends(verify_bearer_token)
):
    """
    Update bus occupancy data
    Specific endpoint for bus occupancy system
    """
    try:
        logger.info(f"Received bus occupancy update for bus {occupancy_data.bus_id}")
        
        # Prepare JSON data for simplified schema
        json_data = {
            "bus_id": occupancy_data.bus_id,
            "route_id": occupancy_data.route_id,
            "occupancy_count": occupancy_data.occupancy_count,
            "max_capacity": occupancy_data.max_capacity,
            "occupancy_percentage": occupancy_data.occupancy_percentage,
            "timestamp": occupancy_data.timestamp.isoformat(),
            "location": occupancy_data.location
        }
        
        # Store in database (simplified schema: id, created_at, json_data)
        try:
            logger.info(f"🔵 Inserting bus occupancy data for bus {occupancy_data.bus_id}")
            result = await supabase_client.insert_data("bus_occupancy", json_data)
            if result:
                logger.info(f"✅ Bus occupancy data stored successfully")
            else:
                logger.warning(f"⚠️ Bus occupancy insert returned None (Supabase not configured)")
        except Exception as db_error:
            logger.error(f"❌ Database error: {db_error}")
            logger.exception(db_error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store occupancy data"
            )
        
        return APIResponse(
            success=True,
            message="Bus occupancy updated successfully",
            data={
                "bus_id": occupancy_data.bus_id,
                "occupancy_percentage": occupancy_data.occupancy_percentage,
                "timestamp": occupancy_data.timestamp
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating bus occupancy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update occupancy: {str(e)}"
        )

@app.get(f"{settings.API_V1_PREFIX}/bus-occupancy/{{bus_id}}", response_model=APIResponse)
async def get_bus_occupancy(
    bus_id: str,
    token: str = Depends(verify_bearer_token)
):
    """
    Get current bus occupancy data for a specific bus
    """
    try:
        logger.info(f"Retrieving occupancy data for bus {bus_id}")
        
        # Get latest data for the bus from simplified schema
        result = await supabase_client.get_data("bus_occupancy")
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No occupancy data found for bus {bus_id}"
            )
        
        # Filter and get the most recent entry for the specific bus
        bus_data = [
            entry for entry in result.data 
            if entry.get('json_data', {}).get('bus_id') == bus_id
        ]
        
        if not bus_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No occupancy data found for bus {bus_id}"
            )
        
        # Get the most recent entry based on created_at
        latest_data = max(bus_data, key=lambda x: x.get('created_at', ''))
        
        return APIResponse(
            success=True,
            message="Bus occupancy data retrieved successfully",
            data=latest_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving bus occupancy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve occupancy data: {str(e)}"
        )

# Exception handler for validation errors
@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content=APIResponse(
            success=False,
            message="Validation error",
            data={"detail": exc.detail if hasattr(exc, 'detail') else str(exc)}
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
