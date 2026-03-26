import os
from datetime import datetime
from typing import List, Optional
from .models import Campaign, CampaignStatus, UserData

CAMPAIGNS_DB: List[dict] = [
    {
        "id": 1,
        "name": "Summer Sale 2025",
        "description": "Seasonal promotional campaign targeting existing customers",
        "status": "active",
        "budget": 15000.0,
        "start_date": "2025-06-01",
        "end_date": "2025-08-31",
        "target_audience": "Existing customers aged 25-45",
        "created_at": datetime(2025, 5, 1).isoformat(),
    },
    {
        "id": 2,
        "name": "Product Launch Q3",
        "description": "New product launch campaign for premium segment",
        "status": "draft",
        "budget": 50000.0,
        "start_date": "2025-07-15",
        "end_date": "2025-09-15",
        "target_audience": "Premium customers and prospects",
        "created_at": datetime(2025, 5, 10).isoformat(),
    },
    {
        "id": 3,
        "name": "Re-engagement Drive",
        "description": "Win back lapsed customers with special offers",
        "status": "paused",
        "budget": 8000.0,
        "start_date": "2025-04-01",
        "end_date": "2025-06-30",
        "target_audience": "Customers inactive for 6+ months",
        "created_at": datetime(2025, 3, 20).isoformat(),
    },
]

USERS_DB: List[dict] = [
    {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "phone": "+1-555-0101", "campaign_id": 1, "subscribed": True, "created_at": datetime(2025, 5, 5).isoformat()},
    {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "phone": "+1-555-0102", "campaign_id": 1, "subscribed": True, "created_at": datetime(2025, 5, 6).isoformat()},
    {"id": 3, "name": "Carol White", "email": "carol@example.com", "phone": None, "campaign_id": 2, "subscribed": True, "created_at": datetime(2025, 5, 7).isoformat()},
    {"id": 4, "name": "David Lee", "email": "david@example.com", "phone": "+1-555-0104", "campaign_id": 3, "subscribed": False, "created_at": datetime(2025, 5, 8).isoformat()},
    {"id": 5, "name": "Eva Martinez", "email": "eva@example.com", "phone": "+1-555-0105", "campaign_id": 1, "subscribed": True, "created_at": datetime(2025, 5, 9).isoformat()},
]

_campaign_counter = len(CAMPAIGNS_DB)
_user_counter = len(USERS_DB)


def get_all_campaigns() -> List[dict]:
    return list(CAMPAIGNS_DB)


def get_campaign_by_id(campaign_id: int) -> Optional[dict]:
    for c in CAMPAIGNS_DB:
        if c["id"] == campaign_id:
            return c
    return None


def create_campaign(data: dict) -> dict:
    global _campaign_counter
    _campaign_counter += 1
    new_campaign = {
        "id": _campaign_counter,
        "status": "draft",
        "created_at": datetime.utcnow().isoformat(),
        **data,
    }
    CAMPAIGNS_DB.append(new_campaign)
    return new_campaign


def update_campaign(campaign_id: int, updates: dict) -> Optional[dict]:
    for idx, c in enumerate(CAMPAIGNS_DB):
        if c["id"] == campaign_id:
            CAMPAIGNS_DB[idx] = {**c, **updates}
            return CAMPAIGNS_DB[idx]
    return None


def delete_campaign(campaign_id: int) -> bool:
    for idx, c in enumerate(CAMPAIGNS_DB):
        if c["id"] == campaign_id:
            CAMPAIGNS_DB.pop(idx)
            return True
    return False


def get_all_users() -> List[dict]:
    return list(USERS_DB)


def get_users_by_campaign(campaign_id: int) -> List[dict]:
    return [u for u in USERS_DB if u["campaign_id"] == campaign_id]


def create_user(data: dict) -> dict:
    global _user_counter
    _user_counter += 1
    new_user = {
        "id": _user_counter,
        "subscribed": True,
        "created_at": datetime.utcnow().isoformat(),
        **data,
    }
    USERS_DB.append(new_user)
    return new_user


def get_campaign_stats() -> List[dict]:
    stats = []
    for c in CAMPAIGNS_DB:
        users = get_users_by_campaign(c["id"])
        active_users = [u for u in users if u["subscribed"]]
        stats.append({
            "campaign_id": c["id"],
            "campaign_name": c["name"],
            "total_users": len(users),
            "active_users": len(active_users),
            "budget": c["budget"],
            "status": c["status"],
        })
    return stats
