"""Company API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ai_sdr.api.v1.deps import get_db, verify_api_key
from ai_sdr.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from ai_sdr.services import company_service

router = APIRouter()


@router.get("", response_model=list[CompanyResponse], dependencies=[Depends(verify_api_key)])
async def list_companies_endpoint(
    franchise_brand: str | None = Query(None),
    is_franchisor: bool | None = Query(None),
    industry: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    return await company_service.list_companies(
        db,
        franchise_brand=franchise_brand,
        is_franchisor=is_franchisor,
        industry=industry,
        limit=limit,
        offset=offset,
    )


@router.get("/{company_id}", response_model=CompanyResponse, dependencies=[Depends(verify_api_key)])
async def get_company_endpoint(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    company = await company_service.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("", response_model=CompanyResponse, status_code=201, dependencies=[Depends(verify_api_key)])
async def create_or_update_company(data: CompanyCreate, db: AsyncSession = Depends(get_db)):
    return await company_service.upsert_company_by_domain(db, data)


@router.patch("/{company_id}", response_model=CompanyResponse, dependencies=[Depends(verify_api_key)])
async def update_company_endpoint(
    company_id: uuid.UUID, data: CompanyUpdate, db: AsyncSession = Depends(get_db)
):
    company = await company_service.update_company(db, company_id, data)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
