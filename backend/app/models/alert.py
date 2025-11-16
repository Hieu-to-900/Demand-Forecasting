"""Alert data models."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AlertBase(BaseModel):
    """Base alert model."""
    
    alert_type: str = Field(..., description="Type of alert (logistics_delay, capacity_warning, etc.)")
    severity: str = Field(..., pattern="^(high|medium|low)$", description="Alert severity level")
    message: str = Field(..., min_length=1, description="Human-readable alert message")
    affected_products: List[str] = Field(default_factory=list, description="List of affected product codes")
    affected_categories: List[str] = Field(default_factory=list, description="List of affected categories")
    impact_description: Optional[str] = Field(None, description="Detailed impact description")
    action_required: Optional[str] = Field(None, description="Recommended action")
    source: str = Field(default="scheduled_job", description="Alert source")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional alert data")
    priority_score: int = Field(default=50, ge=0, le=100, description="Priority score (0-100)")


class AlertCreate(AlertBase):
    """Model for creating a new alert."""
    pass


class AlertUpdate(BaseModel):
    """Model for updating an alert."""
    
    read: Optional[bool] = None
    read_by: Optional[str] = None
    dismissed: Optional[bool] = None


class Alert(AlertBase):
    """Full alert model with database fields."""
    
    id: UUID = Field(..., description="Unique alert ID")
    created_at: datetime = Field(..., description="Alert creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    read: bool = Field(default=False, description="Whether alert has been read")
    read_at: Optional[datetime] = Field(None, description="When alert was read")
    read_by: Optional[str] = Field(None, description="User who read the alert")
    dismissed: bool = Field(default=False, description="Whether alert has been dismissed")
    dismissed_at: Optional[datetime] = Field(None, description="When alert was dismissed")
    
    class Config:
        from_attributes = True


class AlertStats(BaseModel):
    """Alert statistics model."""
    
    total_alerts: int
    unread_count: int
    by_severity: Dict[str, int]
    by_type: Dict[str, int]
    latest_alert: Optional[datetime] = None


class UnreadAlertsSummary(BaseModel):
    """Summary of unread alerts."""
    
    severity: str
    count: int
    latest_alert: datetime
