from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CampaignStatus(str, Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    completed = "completed"


class Campaign(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    status: CampaignStatus = CampaignStatus.draft
    budget: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    target_audience: Optional[str] = None
    created_at: Optional[datetime] = None


class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    budget: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    target_audience: Optional[str] = None


class UserData(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    phone: Optional[str] = None
    campaign_id: Optional[int] = None
    subscribed: bool = True
    created_at: Optional[datetime] = None


class UserDataCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    campaign_id: Optional[int] = None


class HealthStatus(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str


class CampaignStats(BaseModel):
    campaign_id: int
    campaign_name: str
    total_users: int
    active_users: int
    budget: float
    status: str
