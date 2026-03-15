"""Company service — CRUD operations for companies."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_sdr.models.company import Company
from ai_sdr.schemas.company import CompanyCreate, CompanyUpdate


async def create_company(session: AsyncSession, data: CompanyCreate) -> Company:
    company = Company(**data.model_dump())
    session.add(company)
    await session.commit()
    await session.refresh(company)
    return company


async def get_company(session: AsyncSession, company_id: uuid.UUID) -> Company | None:
    return await session.get(Company, company_id)


async def get_company_by_domain(session: AsyncSession, domain: str) -> Company | None:
    result = await session.execute(select(Company).where(Company.domain == domain))
    return result.scalar_one_or_none()


async def list_companies(
    session: AsyncSession,
    industry: str | None = None,
    franchise_brand: str | None = None,
    is_franchisor: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Company]:
    query = select(Company)
    if industry:
        query = query.where(Company.industry == industry)
    if franchise_brand is not None:
        query = query.where(Company.franchise_brand == franchise_brand)
    if is_franchisor is not None:
        query = query.where(Company.is_franchisor == is_franchisor)
    query = query.order_by(Company.created_at.desc()).limit(limit).offset(offset)
    result = await session.execute(query)
    return list(result.scalars().all())


async def update_company(
    session: AsyncSession, company_id: uuid.UUID, data: CompanyUpdate
) -> Company | None:
    company = await session.get(Company, company_id)
    if not company:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    await session.commit()
    await session.refresh(company)
    return company


async def upsert_company_by_domain(session: AsyncSession, data: CompanyCreate) -> Company:
    """Create or update a company identified by its domain."""
    result = await session.execute(select(Company).where(Company.domain == data.domain))
    company = result.scalar_one_or_none()
    if company:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(company, field, value)
    else:
        company = Company(**data.model_dump())
        session.add(company)
    await session.commit()
    await session.refresh(company)
    return company


async def get_franchise_network(session: AsyncSession, network_id: uuid.UUID) -> list[Company]:
    """Return all companies belonging to the given franchise network."""
    result = await session.execute(
        select(Company).where(Company.franchise_network_id == network_id)
    )
    return list(result.scalars().all())


async def search_companies_by_name(
    session: AsyncSession, name: str, limit: int = 10
) -> list[Company]:
    """Case-insensitive substring search on company name."""
    result = await session.execute(
        select(Company).where(Company.name.ilike(f"%{name}%")).limit(limit)
    )
    return list(result.scalars().all())
