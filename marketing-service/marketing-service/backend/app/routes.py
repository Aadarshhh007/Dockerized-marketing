from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import List, Optional
from .models import Campaign, CampaignCreate, UserData, UserDataCreate, HealthStatus, CampaignStats
from . import database

router = APIRouter()


@router.get("/health", response_model=HealthStatus, tags=["Health"])
def health_check():
    return HealthStatus(
        status="healthy",
        service="Marketing Service API",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/campaigns", response_model=List[Campaign], tags=["Campaigns"])
def list_campaigns(status: Optional[str] = Query(None, description="Filter by campaign status")):
    campaigns = database.get_all_campaigns()
    if status:
        campaigns = [c for c in campaigns if c["status"] == status]
    return campaigns


@router.post("/campaigns", response_model=Campaign, status_code=201, tags=["Campaigns"])
def create_campaign(campaign: CampaignCreate):
    data = campaign.model_dump()
    created = database.create_campaign(data)
    return created


@router.get("/campaigns/{campaign_id}", response_model=Campaign, tags=["Campaigns"])
def get_campaign(campaign_id: int):
    campaign = database.get_campaign_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    return campaign


@router.put("/campaigns/{campaign_id}", response_model=Campaign, tags=["Campaigns"])
def update_campaign(campaign_id: int, updates: CampaignCreate):
    updated = database.update_campaign(campaign_id, updates.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    return updated


@router.delete("/campaigns/{campaign_id}", status_code=204, tags=["Campaigns"])
def delete_campaign(campaign_id: int):
    deleted = database.delete_campaign(campaign_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")


@router.get("/users", response_model=List[UserData], tags=["Users"])
def list_users(campaign_id: Optional[int] = Query(None, description="Filter by campaign ID")):
    if campaign_id:
        return database.get_users_by_campaign(campaign_id)
    return database.get_all_users()


@router.post("/users", response_model=UserData, status_code=201, tags=["Users"])
def create_user(user: UserDataCreate):
    data = user.model_dump()
    created = database.create_user(data)
    return created


@router.get("/stats", response_model=List[CampaignStats], tags=["Analytics"])
def get_stats():
    return database.get_campaign_stats()
