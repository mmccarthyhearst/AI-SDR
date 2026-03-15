"""ICP API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ai_sdr.api.v1.deps import get_db, verify_api_key
from ai_sdr.schemas.icp import ICPCreate, ICPResponse, ICPUpdate
from ai_sdr.services import icp_service

router = APIRouter()


@router.get("", response_model=list[ICPResponse], dependencies=[Depends(verify_api_key)])
async def list_icps(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    return await icp_service.list_icps(db, active_only=active_only)


@router.get("/{icp_id}", response_model=ICPResponse, dependencies=[Depends(verify_api_key)])
async def get_icp(icp_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    icp = await icp_service.get_icp(db, icp_id)
    if not icp:
        raise HTTPException(status_code=404, detail="ICP not found")
    return icp


@router.post("", response_model=ICPResponse, status_code=201, dependencies=[Depends(verify_api_key)])
async def create_icp(data: ICPCreate, db: AsyncSession = Depends(get_db)):
    return await icp_service.create_icp(db, data)


@router.put("/{icp_id}", response_model=ICPResponse, dependencies=[Depends(verify_api_key)])
async def update_icp(
    icp_id: uuid.UUID, data: ICPUpdate, db: AsyncSession = Depends(get_db)
):
    icp = await icp_service.update_icp(db, icp_id, data)
    if not icp:
        raise HTTPException(status_code=404, detail="ICP not found")
    return icp
