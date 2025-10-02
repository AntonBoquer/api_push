from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime
import importlib.util
from uuid import UUID

class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DetectionResult(BaseModel):
    image: str
    x_max: float
    x_min: float
    y_max: float
    y_min: float
    class_id: int
    class_name: str
    confidence: float


class PushPayload(BaseModel):
    """Model for incoming push request payload"""
    uuid: Optional[UUID] = Field(
        None, description="Unique identifier for the payload (nullable if not provided)"
    )    
    detection_results: List[DetectionResult] = Field(default_factory=list)    # metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")

class BusOccupancyData(BaseModel):
    """Example model for bus occupancy data"""
    bus_id: str = Field(..., description="Unique identifier for the bus")
    route_id: str = Field(..., description="Route identifier")
    occupancy_count: int = Field(..., ge=0, description="Number of passengers")
    max_capacity: int = Field(..., gt=0, description="Maximum capacity of the bus")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    location: Optional[Dict[str, float]] = Field(None, description="GPS coordinates")
    
    @property
    def occupancy_percentage(self) -> float:
        """Calculate occupancy percentage"""
        return (self.occupancy_count / self.max_capacity) * 100

class HealthCheck(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    database_connected: bool
