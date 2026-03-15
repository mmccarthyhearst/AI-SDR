"""Unit tests for company_service — DB session is fully mocked."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_sdr.schemas.company import CompanyCreate
from ai_sdr.services.company_service import (
    get_franchise_network,
    list_companies,
    search_companies_by_name,
    upsert_company_by_domain,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_session(scalar_one_or_none=None, scalars_all=None):
    """Return a minimal AsyncSession mock.

    Parameters
    ----------
    scalar_one_or_none:
        Value returned by ``result.scalar_one_or_none()``.
    scalars_all:
        List returned by ``result.scalars().all()``.
    """
    session = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = scalar_one_or_none

    scalars_mock = MagicMock()
    scalars_mock.all.return_value = scalars_all or []
    mock_result.scalars.return_value = scalars_mock

    session.execute = AsyncMock(return_value=mock_result)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


def _make_company_data(**overrides):
    defaults = dict(name="Acme Franchise", domain="acme.com", industry="Retail")
    defaults.update(overrides)
    return CompanyCreate(**defaults)


# ---------------------------------------------------------------------------
# upsert_company_by_domain — creates new company
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_creates_new_company_when_domain_not_found():
    session = _make_session(scalar_one_or_none=None)
    data = _make_company_data()

    await upsert_company_by_domain(session, data)

    session.add.assert_called_once()
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once()


# ---------------------------------------------------------------------------
# upsert_company_by_domain — updates existing company
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_updates_existing_company_when_domain_found():
    existing = MagicMock()
    existing.name = "Old Name"
    existing.domain = "acme.com"

    session = _make_session(scalar_one_or_none=existing)
    data = _make_company_data(name="New Name")

    await upsert_company_by_domain(session, data)

    # Should NOT add a new object — only update the existing one
    session.add.assert_not_called()
    # The name attribute should have been updated via setattr
    assert existing.name == "New Name"
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once()


# ---------------------------------------------------------------------------
# search_companies_by_name
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_companies_by_name_returns_list():
    company_a = MagicMock()
    company_a.name = "Acme Corp"
    company_b = MagicMock()
    company_b.name = "Acme Franchise"

    session = _make_session(scalars_all=[company_a, company_b])

    results = await search_companies_by_name(session, "acme")

    assert len(results) == 2
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_companies_by_name_empty_result():
    session = _make_session(scalars_all=[])
    results = await search_companies_by_name(session, "nonexistent")
    assert results == []


# ---------------------------------------------------------------------------
# get_franchise_network
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_franchise_network_returns_matching_companies():
    network_id = uuid.uuid4()
    member_a = MagicMock()
    member_b = MagicMock()

    session = _make_session(scalars_all=[member_a, member_b])

    results = await get_franchise_network(session, network_id)

    assert len(results) == 2
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_franchise_network_empty_when_no_members():
    session = _make_session(scalars_all=[])
    results = await get_franchise_network(session, uuid.uuid4())
    assert results == []


# ---------------------------------------------------------------------------
# list_companies — franchise filters
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_companies_with_franchise_brand_filter():
    session = _make_session(scalars_all=[])
    results = await list_companies(session, franchise_brand="SubwayBrand")
    assert results == []
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_companies_with_is_franchisor_filter():
    session = _make_session(scalars_all=[])
    results = await list_companies(session, is_franchisor=True)
    assert results == []
    session.execute.assert_awaited_once()
