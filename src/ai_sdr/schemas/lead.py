"""Lead schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

from ai_sdr.models.lead import LeadStatus, LeadTier

if TYPE_CHECKING:
    pass


class LeadCreate(BaseModel):
    company_id: uuid.UUID
    contact_id: uuid.UUID
    icp_id: uuid.UUID | None = None


class LeadUpdate(BaseModel):
    status: LeadStatus | None = None
    score: int | None = None
    tier: LeadTier | None = None
    assigned_team: str | None = None
    assigned_rep_id: str | None = None
    assigned_rep_name: str | None = None
    disqualification_reason: str | None = None


class LeadResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    contact_id: uuid.UUID
    icp_id: uuid.UUID | None
    agent_run_id: uuid.UUID | None
    status: LeadStatus
    score: int | None
    tier: LeadTier | None
    qualification_reasoning: str | None
    buying_signals: dict | None
    assigned_team: str | None
    assigned_rep_id: str | None
    assigned_rep_name: str | None
    routing_reasoning: str | None
    disqualification_reason: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadDetailResponse(LeadResponse):
    """Lead with nested company and contact info."""

    company: CompanyResponse | None = None
    contact: ContactResponse | None = None


# Deferred imports for forward references
from ai_sdr.schemas.company import CompanyResponse  # noqa: E402
from ai_sdr.schemas.contact import ContactResponse  # noqa: E402

LeadDetailResponse.model_rebuild()
