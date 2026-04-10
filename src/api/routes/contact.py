"""
Contact form endpoint for website inquiries.
"""

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/contact", tags=["contact"])


class ContactMessage(BaseModel):
    full_name: str
    email: EmailStr
    subject: str
    message: str


CONTACT_MESSAGES: list[dict[str, str]] = []


@router.post("/messages", status_code=201)
async def submit_contact_message(payload: ContactMessage):
    """Store a contact request in memory for local development."""
    request_id = f"contact_{uuid4().hex[:10]}"
    entry = {
        "id": request_id,
        "full_name": payload.full_name,
        "email": payload.email,
        "subject": payload.subject,
        "message": payload.message,
        "received_at": datetime.utcnow().isoformat() + "Z",
        "status": "queued",
    }
    CONTACT_MESSAGES.append(entry)
    return {
        "message": "Thanks. Your message has been received and queued for follow-up.",
        "request_id": request_id,
        "received_at": entry["received_at"],
    }