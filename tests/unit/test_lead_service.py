"""Unit tests for lead_service — CRUD operations with mocked async sessions."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_sdr.models.lead import LeadStatus, LeadTier
from ai_sdr.schemas.lead import LeadCreate, LeadUpdate
from ai_sdr.services.lead_service import (
    create_lead,
    disqualify_lead,
    get_lead,
    list_leads,
    update_lead,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_session(scalar_one_or_none=None, scalars_all=None):
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


# ---------------------------------------------------------------------------
# create_lead
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_lead_calls_add_and_commit(monkeypatch):
    import ai_sdr.services.lead_service as lead_svc

    lead_mock = MagicMock()
    monkeypatch.setattr(lead_svc, "Lead", lambda **kwargs: lead_mock)

    session = _make_session()
    data = LeadCreate(
        company_id=uuid.uuid4(),
        contact_id=uuid.uuid4(),
    )
    await create_lead(session, data)

    session.add.assert_called_once_with(lead_mock)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_lead_with_icp_id(monkeypatch):
    import ai_sdr.services.lead_service as lead_svc

    lead_mock = MagicMock()
    monkeypatch.setattr(lead_svc, "Lead", lambda **kwargs: lead_mock)

    session = _make_session()
    data = LeadCreate(
        company_id=uuid.uuid4(),
        contact_id=uuid.uuid4(),
        icp_id=uuid.uuid4(),
    )
    await create_lead(session, data)
    session.add.assert_called_once_with(lead_mock)


# ---------------------------------------------------------------------------
# get_lead
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_lead_returns_lead(monkeypatch):
    """get_lead returns a lead when found. Patch select to bypass SQLAlchemy mapper config."""
    from unittest.mock import patch, MagicMock

    lead_mock = MagicMock()
    lead_mock.id = uuid.uuid4()
    lead_mock.status = LeadStatus.NEW

    session = _make_session(scalar_one_or_none=lead_mock)

    lead_id = uuid.uuid4()
    # Patch select so query construction doesn't trigger mapper config
    fake_query = MagicMock()
    fake_query.options.return_value = fake_query
    fake_query.where.return_value = fake_query

    with patch("ai_sdr.services.lead_service.select", return_value=fake_query):
        with patch("ai_sdr.services.lead_service.selectinload", return_value=MagicMock()):
            result = await get_lead(session, lead_id)

    assert result is lead_mock
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_lead_not_found_returns_none():
    from unittest.mock import patch, MagicMock

    session = _make_session(scalar_one_or_none=None)

    fake_query = MagicMock()
    fake_query.options.return_value = fake_query
    fake_query.where.return_value = fake_query

    with patch("ai_sdr.services.lead_service.select", return_value=fake_query):
        with patch("ai_sdr.services.lead_service.selectinload", return_value=MagicMock()):
            result = await get_lead(session, uuid.uuid4())
    assert result is None


# ---------------------------------------------------------------------------
# list_leads
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_leads_no_filters():
    lead_a = MagicMock()
    lead_b = MagicMock()
    session = _make_session(scalars_all=[lead_a, lead_b])

    results = await list_leads(session)

    assert len(results) == 2
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_leads_with_status_filter():
    session = _make_session(scalars_all=[])
    results = await list_leads(session, status=LeadStatus.QUALIFIED)
    assert results == []
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_leads_with_tier_filter():
    session = _make_session(scalars_all=[])
    results = await list_leads(session, tier=LeadTier.HOT)
    assert results == []


@pytest.mark.asyncio
async def test_list_leads_with_min_score_filter():
    session = _make_session(scalars_all=[])
    results = await list_leads(session, min_score=80)
    assert results == []


@pytest.mark.asyncio
async def test_list_leads_with_assigned_team_filter():
    session = _make_session(scalars_all=[])
    results = await list_leads(session, assigned_team="Enterprise")
    assert results == []


@pytest.mark.asyncio
async def test_list_leads_with_limit_offset():
    session = _make_session(scalars_all=[])
    results = await list_leads(session, limit=10, offset=5)
    assert results == []


# ---------------------------------------------------------------------------
# update_lead
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_lead_updates_status():
    lead_mock = MagicMock()
    lead_mock.status = LeadStatus.NEW

    session = AsyncMock()
    session.get = AsyncMock(return_value=lead_mock)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    data = LeadUpdate(status=LeadStatus.QUALIFIED)
    result = await update_lead(session, uuid.uuid4(), data)

    assert lead_mock.status == LeadStatus.QUALIFIED
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_lead_not_found_returns_none():
    session = AsyncMock()
    session.get = AsyncMock(return_value=None)

    result = await update_lead(session, uuid.uuid4(), LeadUpdate(score=90))
    assert result is None


@pytest.mark.asyncio
async def test_update_lead_multiple_fields():
    lead_mock = MagicMock()
    lead_mock.score = 50
    lead_mock.tier = LeadTier.COLD

    session = AsyncMock()
    session.get = AsyncMock(return_value=lead_mock)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    data = LeadUpdate(score=85, tier=LeadTier.HOT, assigned_team="Priority")
    await update_lead(session, uuid.uuid4(), data)

    assert lead_mock.score == 85
    assert lead_mock.tier == LeadTier.HOT
    assert lead_mock.assigned_team == "Priority"


# ---------------------------------------------------------------------------
# disqualify_lead
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_disqualify_lead_sets_status_and_reason():
    lead_mock = MagicMock()
    lead_mock.status = LeadStatus.NEW

    session = AsyncMock()
    session.get = AsyncMock(return_value=lead_mock)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    result = await disqualify_lead(session, uuid.uuid4(), "Does not meet ICP criteria")

    assert lead_mock.status == LeadStatus.DISQUALIFIED
    assert lead_mock.disqualification_reason == "Does not meet ICP criteria"
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_disqualify_lead_not_found_returns_none():
    session = AsyncMock()
    session.get = AsyncMock(return_value=None)

    result = await disqualify_lead(session, uuid.uuid4(), "reason")
    assert result is None


# ---------------------------------------------------------------------------
# LeadStatus and LeadTier enums
# ---------------------------------------------------------------------------


def test_lead_status_values():
    assert LeadStatus.NEW == "new"
    assert LeadStatus.QUALIFIED == "qualified"
    assert LeadStatus.DISQUALIFIED == "disqualified"
    assert LeadStatus.ROUTED == "routed"
    assert LeadStatus.CONTACTED == "contacted"
    assert LeadStatus.MEETING_BOOKED == "meeting_booked"
    assert LeadStatus.CONVERTED == "converted"


def test_lead_tier_values():
    assert LeadTier.HOT == "hot"
    assert LeadTier.WARM == "warm"
    assert LeadTier.COLD == "cold"
