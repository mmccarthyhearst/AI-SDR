"""Unit tests for icp_service — score_lead_against_icp and CRUD with mocked session."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_sdr.schemas.agent import LeadCandidate
from ai_sdr.services.icp_service import (
    create_icp,
    get_icp,
    list_icps,
    score_lead_against_icp,
    update_icp,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_icp(**overrides):
    """Build a minimal ICP-like mock for score_lead_against_icp tests."""
    icp = MagicMock()
    icp.target_industries = overrides.get("target_industries", ["Technology", "SaaS"])
    icp.min_employee_count = overrides.get("min_employee_count", 50)
    icp.max_employee_count = overrides.get("max_employee_count", 5000)
    icp.target_seniority = overrides.get("target_seniority", ["VP", "C-Suite"])
    icp.target_titles = overrides.get("target_titles", ["VP of Sales", "CRO"])
    icp.target_geography = overrides.get("target_geography", ["US", "Canada"])
    icp.required_tech_stack = overrides.get("required_tech_stack", ["Salesforce"])
    icp.scoring_weights = overrides.get("scoring_weights", None)
    return icp


def _make_candidate(**overrides):
    defaults = dict(
        company_name="Acme Corp",
        company_domain="acme.com",
        contact_first_name="Jane",
        contact_last_name="Smith",
        contact_email="jane@acme.com",
    )
    defaults.update(overrides)
    return LeadCandidate(**defaults)


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
# score_lead_against_icp — perfect match
# ---------------------------------------------------------------------------


def test_score_lead_full_match():
    """Lead matching all ICP criteria returns 100."""
    icp = _make_icp()
    candidate = _make_candidate(
        industry="Technology",
        employee_count_range="100-500",
        contact_seniority="VP",
        contact_title="VP of Sales",
        hq_location="US",
        tech_stack=["Salesforce"],
    )
    score = score_lead_against_icp(candidate, icp)
    assert score == 100


def test_score_lead_industry_match_only():
    """Lead matching only industry criterion scores partial."""
    icp = _make_icp()
    candidate = _make_candidate(
        industry="Technology",
        contact_seniority="Manager",    # no match
        contact_title="SDR",             # no match
        hq_location="Germany",           # no match
        tech_stack=["HubSpot"],          # no match
    )
    score = score_lead_against_icp(candidate, icp)
    assert 0 < score < 100


def test_score_lead_no_match():
    """Lead with no matching criteria scores 0."""
    icp = _make_icp()
    candidate = _make_candidate(
        industry="Agriculture",
        employee_count_range="1000000-9999999",  # way outside range
        contact_seniority="Intern",
        contact_title="Farm Manager",
        hq_location="Mars",
        tech_stack=["Excel"],
    )
    score = score_lead_against_icp(candidate, icp)
    assert score == 0


def test_score_lead_no_criteria_returns_50():
    """ICP with no criteria defined returns 50 (neutral default)."""
    icp = _make_icp(
        target_industries=None,
        min_employee_count=None,
        max_employee_count=None,
        target_seniority=None,
        target_titles=None,
        target_geography=None,
        required_tech_stack=None,
    )
    candidate = _make_candidate()
    score = score_lead_against_icp(candidate, icp)
    assert score == 50


def test_score_lead_partial_tech_stack():
    """Lead with partial tech stack overlap scores proportionally."""
    icp = _make_icp(required_tech_stack=["Salesforce", "Python", "AWS"])
    candidate = _make_candidate(
        industry=None,
        tech_stack=["Salesforce"],  # 1/3 overlap
    )
    # Only tech_stack contributes (default weight 15), so partial score
    score = score_lead_against_icp(candidate, icp)
    assert 0 < score <= 100


def test_score_lead_seniority_case_insensitive():
    """Seniority matching is case-insensitive."""
    icp = _make_icp(target_seniority=["VP", "C-Suite"])
    candidate = _make_candidate(
        contact_seniority="vp",
        industry=None,
        tech_stack=None,
        hq_location=None,
    )
    score = score_lead_against_icp(candidate, icp)
    # Seniority should match
    assert score > 0


def test_score_lead_geography_partial_match():
    """Geography match on substring (e.g. 'US' in 'Austin, US')."""
    icp = _make_icp(target_geography=["US"])
    candidate = _make_candidate(
        hq_location="Austin, US",
        industry=None,
        tech_stack=None,
        contact_seniority=None,
    )
    score = score_lead_against_icp(candidate, icp)
    assert score > 0


def test_score_lead_employee_range_midpoint_in_range():
    """Employee range midpoint within ICP bounds gives full size score."""
    icp = _make_icp(
        min_employee_count=50,
        max_employee_count=5000,
        target_industries=None,
        target_seniority=None,
        target_titles=None,
        target_geography=None,
        required_tech_stack=None,
    )
    candidate = _make_candidate(employee_count_range="100-500")
    score = score_lead_against_icp(candidate, icp)
    # Only company_size matches — should be 100% of that criterion
    assert score == 100


def test_score_lead_employee_range_outside_returns_less():
    """Employee count completely outside range gets no size credit."""
    icp = _make_icp(
        min_employee_count=50,
        max_employee_count=500,
        target_industries=None,
        target_seniority=None,
        target_titles=None,
        target_geography=None,
        required_tech_stack=None,
    )
    candidate = _make_candidate(employee_count_range="10000-50000")
    score = score_lead_against_icp(candidate, icp)
    assert score == 0


def test_score_lead_title_substring_match():
    """Title match works on substring containment."""
    icp = _make_icp(target_titles=["VP of Sales"])
    candidate = _make_candidate(
        contact_title="Global VP of Sales & Marketing",
        industry=None,
        tech_stack=None,
        hq_location=None,
        contact_seniority=None,
    )
    score = score_lead_against_icp(candidate, icp)
    assert score > 0


def test_score_lead_custom_scoring_weights():
    """Custom scoring weights are respected."""
    icp = _make_icp(
        scoring_weights={"industry": 50, "company_size": 50},
        target_industries=["Technology"],
        min_employee_count=50,
        max_employee_count=5000,
        target_seniority=None,
        target_titles=None,
        target_geography=None,
        required_tech_stack=None,
    )
    candidate = _make_candidate(
        industry="Technology",
        employee_count_range="100-500",
    )
    score = score_lead_against_icp(candidate, icp)
    assert score == 100


# ---------------------------------------------------------------------------
# CRUD — create_icp
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_icp_calls_add_and_commit(monkeypatch):
    from ai_sdr.schemas.icp import ICPCreate
    import ai_sdr.services.icp_service as icp_svc

    icp_mock = MagicMock()
    monkeypatch.setattr(icp_svc, "ICP", lambda **kwargs: icp_mock)

    session = _make_session()
    data = ICPCreate(name="Franchise ICP", target_industries=["Fitness"])
    await create_icp(session, data)

    session.add.assert_called_once_with(icp_mock)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once()


# ---------------------------------------------------------------------------
# CRUD — get_icp
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_icp_returns_object():
    icp_mock = MagicMock()
    icp_mock.name = "Test ICP"

    session = AsyncMock()
    session.get = AsyncMock(return_value=icp_mock)

    icp_id = uuid.uuid4()
    result = await get_icp(session, icp_id)

    assert result is icp_mock
    session.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_icp_not_found_returns_none():
    session = AsyncMock()
    session.get = AsyncMock(return_value=None)

    result = await get_icp(session, uuid.uuid4())
    assert result is None


# ---------------------------------------------------------------------------
# CRUD — list_icps
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_icps_active_only():
    icp_a = MagicMock()
    icp_b = MagicMock()
    session = _make_session(scalars_all=[icp_a, icp_b])

    results = await list_icps(session, active_only=True)

    assert len(results) == 2
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_icps_empty():
    session = _make_session(scalars_all=[])
    results = await list_icps(session)
    assert results == []


# ---------------------------------------------------------------------------
# CRUD — update_icp
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_icp_returns_updated():
    from ai_sdr.schemas.icp import ICPUpdate

    icp_mock = MagicMock()
    icp_mock.name = "Old Name"

    session = AsyncMock()
    session.get = AsyncMock(return_value=icp_mock)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    update_data = ICPUpdate(name="New Name")
    result = await update_icp(session, uuid.uuid4(), update_data)

    assert icp_mock.name == "New Name"
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_icp_not_found_returns_none():
    from ai_sdr.schemas.icp import ICPUpdate

    session = AsyncMock()
    session.get = AsyncMock(return_value=None)

    result = await update_icp(session, uuid.uuid4(), ICPUpdate(name="X"))
    assert result is None
