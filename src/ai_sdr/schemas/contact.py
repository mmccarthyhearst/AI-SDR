"""Contact schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    title: str | None = None
    seniority_level: str | None = None
    linkedin_url: str | None = None
    phone: str | None = None


class ContactCreate(ContactBase):
    company_id: uuid.UUID
    source: str = "manual"


class ContactUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    title: str | None = None
    seniority_level: str | None = None
    verified: bool | None = None


class ContactResponse(ContactBase):
    id: uuid.UUID
    company_id: uuid.UUID
    verified: bool
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
