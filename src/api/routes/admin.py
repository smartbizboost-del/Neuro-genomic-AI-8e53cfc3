"""
Admin routes for user management and system monitoring
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime

from src.api.middleware.auth import get_current_user
from src.api.services.monitoring import set_active_users

router = APIRouter(prefix="/admin", tags=["admin"])

# Models
class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: str
    created_at: datetime
    last_login: Optional[datetime]
    analyses_count: int

class UserRoleUpdate(BaseModel):
    role: str

class UserStatusUpdate(BaseModel):
    status: str  # active, suspended, pending

# Mock database (replace with real DB)
MOCK_USERS = {
    "user_1": {
        "id": "user_1",
        "email": "researcher@test.com",
        "full_name": "Test Researcher",
        "role": "researcher",
        "status": "active",
        "created_at": datetime.now(),
        "last_login": datetime.now(),
        "analyses_count": 15
    },
    "user_2": {
        "id": "user_2",
        "email": "clinician@test.com",
        "full_name": "Dr. Jane",
        "role": "clinician",
        "status": "active",
        "created_at": datetime.now(),
        "last_login": datetime.now(),
        "analyses_count": 24
    }
}

LOG_ENTRIES = [
    {
        "timestamp": datetime.now().isoformat(),
        "level": "INFO",
        "endpoint": "/api/v1/analysis",
        "method": "POST",
        "status_code": 200,
        "response_time_ms": 234,
        "user_id": "user_1"
    },
    {
        "timestamp": datetime.now().isoformat(),
        "level": "WARNING",
        "endpoint": "/api/v1/analysis",
        "method": "GET",
        "status_code": 500,
        "response_time_ms": 514,
        "user_id": "user_2"
    }
]

# Helper function to check admin access
def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    admin: dict = Depends(require_admin),
    role: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Get all users with optional filters.
    Requires admin role.
    """
    users = list(MOCK_USERS.values())
    
    if role:
        users = [u for u in users if u["role"] == role]
    if status:
        users = [u for u in users if u.get("status") == status]

    active_users = sum(1 for u in users if u.get("status") == "active")
    set_active_users(active_users)
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    admin: dict = Depends(require_admin)
):
    """Get a specific user by ID"""
    if user_id not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    return MOCK_USERS[user_id]


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_update: UserRoleUpdate,
    admin: dict = Depends(require_admin)
):
    """Update a user's role"""
    if user_id not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    valid_roles = ["admin", "clinician", "researcher", "viewer"]
    if role_update.role not in valid_roles:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid role. Must be one of: {valid_roles}"
        )
    
    MOCK_USERS[user_id]["role"] = role_update.role
    return {"message": "User role updated", "user_id": user_id, "new_role": role_update.role}


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    status_update: UserStatusUpdate,
    admin: dict = Depends(require_admin)
):
    """Activate, suspend, or approve a user"""
    if user_id not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    valid_statuses = ["active", "suspended", "pending"]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    MOCK_USERS[user_id]["status"] = status_update.status
    return {"message": "User status updated", "user_id": user_id, "new_status": status_update.status}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: dict = Depends(require_admin)
):
    """Delete a user (soft delete)"""
    if user_id not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Soft delete - mark as deleted instead of removing
    MOCK_USERS[user_id]["status"] = "deleted"
    return {"message": f"User {user_id} has been deleted"}


@router.get("/metrics")
async def get_system_metrics(admin: dict = Depends(require_admin)):
    """Get system health and usage metrics"""
    active = sum(1 for u in MOCK_USERS.values() if u.get("status") == "active")
    set_active_users(active)

    return {
        "users": {
            "total": len(MOCK_USERS),
            "active": active,
            "by_role": {
                "admin": sum(1 for u in MOCK_USERS.values() if u.get("role") == "admin"),
                "clinician": sum(1 for u in MOCK_USERS.values() if u.get("role") == "clinician"),
                "researcher": sum(1 for u in MOCK_USERS.values() if u.get("role") == "researcher"),
                "viewer": sum(1 for u in MOCK_USERS.values() if u.get("role") == "viewer")
            }
        },
        "analyses": {
            "total": 1234,
            "today": 42,
            "this_week": 287,
            "this_month": 890
        },
        "api": {
            "uptime": "99.8%",
            "avg_response_ms": 342,
            "error_rate": "0.3%",
            "total_calls": 45678
        },
        "system": {
            "status": "healthy",
            "workers": 2,
            "queue_length": 0,
            "last_backup": datetime.now().isoformat()
        }
    }


@router.get("/health/services")
async def get_service_health(admin: dict = Depends(require_admin)):
    """Get health status of all services"""
    return {
        "api": {"status": "healthy", "uptime": "99.9%"},
        "database": {"status": "healthy", "connections": 5},
        "redis": {"status": "healthy", "memory_used_mb": 42},
        "celery": {"status": "healthy", "workers": 2, "queue": 0},
        "storage": {"status": "healthy", "used_gb": 2.3, "total_gb": 100}
    }


@router.get("/logs")
async def get_api_logs(
    admin: dict = Depends(require_admin),
    limit: int = 100,
    level: Optional[str] = None
):
    """Get recent API logs"""
    logs = LOG_ENTRIES
    if level:
        logs = [entry for entry in logs if entry["level"].lower() == level.lower()]
    return {
        "logs": logs[:limit],
        "total": len(logs),
        "limit": limit
    }
