"""Lead API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ai_sdr.api.v1.deps import get_db, verify_api_key
from ai_sdr.models.lead import LeadStatus, LeadTier
from ai_sdr.schemas.lead import LeadCreate, LeadResponse, LeadUpdate
from ai_sdr.services import lead_service

router = APIRouter()


@router.get("", response_model=list[LeadResponse], dependencies=[Depends(verify_api_key)])
async def list_leads(
    status: LeadStatus | None = None,
    tier: LeadTier | None = None,
    assigned_team: str | None = None,
    min_score: int | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    return await lead_service.list_leads(
        db, status=status, tier=tier, assigned_team=assigned_team,
        min_score=min_score, limit=limit, offset=offset,
    )


@router.get("/{lead_id}", response_model=LeadResponse, dependencies=[Depends(verify_api_key)])
async def get_lead(lead_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    lead = await lead_service.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("", response_model=LeadResponse, status_code=201, dependencies=[Depends(verify_api_key)])
async def create_lead(data: LeadCreate, db: AsyncSession = Depends(get_db)):
    return await lead_service.create_lead(db, data)


@router.patch("/{lead_id}", response_model=LeadResponse, dependencies=[Depends(verify_api_key)])
async def update_lead(
    lead_id: uuid.UUID, data: LeadUpdate, db: AsyncSession = Depends(get_db)
):
    lead = await lead_service.update_lead(db, lead_id, data)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
