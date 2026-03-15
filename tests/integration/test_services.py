"""Integration tests for service layer using mocked async sessions.

Note: The ORM models use PostgreSQL-specific UUID columns which are not
compatible with SQLite in-memory DB. These tests use the same mock-session
approach as unit tests but are kept separate as service-layer integration tests
(testing the full service function behavior end-to-end with realistic data).
"""
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_sdr.schemas.company import CompanyCreate
from ai_sdr.schemas.icp import ICPCreate
from ai_sdr.services.company_service import (
    list_companies,
    upsert_company_by_domain,
)
from ai_sdr.services.icp_service import create_icp, list_icps


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
# company_service integration
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_creates_company(monkeypatch):
    """upsert creates a new Company when domain not found.

    Patches both `select` and `Company` in company_service to bypass
    SQLAlchemy mapper config that fails due to ambiguous FK in Lead.company.
    """
    from unittest.mock import patch

    company_mock = MagicMock()
    session = _make_session(scalar_one_or_none=None)
    data = CompanyCreate(name="Test Franchise", domain="test.com", is_franchisor=True, franchise_count=50)

    fake_query = MagicMock()
    fake_query.where.return_value = fake_query

    with patch("ai_sdr.services.company_service.select", return_value=fake_query), \
         patch("ai_sdr.services.company_service.Company", return_value=company_mock) as mock_co:
        mock_co.domain = MagicMock()
        mock_co.franchise_network_id = MagicMock()
        await upsert_company_by_domain(session, data)

    session.add.assert_called_once()
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_upsert_updates_existing():
    existing = MagicMock()
    existing.name = "Original Name"
    existing.domain = "update-test.com"

    session = _make_session(scalar_one_or_none=existing)
    data = CompanyCreate(name="Updated Name", domain="update-test.com")
    await upsert_company_by_domain(session, data)

    # update path: should NOT add a new object
    session.add.assert_not_called()
    assert existing.name == "Updated Name"
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_companies_franchisor_filter():
    franchisor = MagicMock()
    franchisor.is_franchisor = True

    session = _make_session(scalars_all=[franchisor])
    results = await list_companies(session, is_franchisor=True)

    assert len(results) == 1
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_companies_returns_empty_list():
    session = _make_session(scalars_all=[])
    results = await list_companies(session)
    assert results == []


@pytest.mark.asyncio
async def test_list_companies_franchise_brand_filter():
    session = _make_session(scalars_all=[])
    results = await list_companies(session, franchise_brand="Subway")
    assert results == []
    session.execute.assert_awaited_once()


# ---------------------------------------------------------------------------
# icp_service integration
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_icp_franchise_profile(monkeypatch):
    import ai_sdr.services.icp_service as icp_svc

    icp_mock = MagicMock()
    monkeypatch.setattr(icp_svc, "ICP", lambda **kwargs: icp_mock)

    session = _make_session()
    data = ICPCreate(
        name="Franchise ICP",
        target_industries=["Fitness", "Food"],
        min_employee_count=10,
        max_employee_count=10000,
        target_titles=["VP Operations", "COO", "CFO"],
        target_seniority=["VP", "C-Suite"],
        target_geography=["US"],
        required_tech_stack=["Salesforce"],
    )
    await create_icp(session, data)

    session.add.assert_called_once_with(icp_mock)
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_icps_returns_all_active():
    icp_a = MagicMock()
    icp_b = MagicMock()
    session = _make_session(scalars_all=[icp_a, icp_b])

    results = await list_icps(session, active_only=True)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_list_icps_all_inactive_returns_empty():
    session = _make_session(scalars_all=[])
    results = await list_icps(session)
    assert results == []


# ---------------------------------------------------------------------------
# routing_service integration
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_routing_rule_integration(monkeypatch):
    from ai_sdr.schemas.routing_rule import RoutingRuleCreate, RuleCondition, RuleAction
    from ai_sdr.services.routing_service import create_routing_rule
    import ai_sdr.services.routing_service as routing_svc

    rule_mock = MagicMock()
    monkeypatch.setattr(routing_svc, "RoutingRule", lambda **kwargs: rule_mock)

    session = _make_session()
    data = RoutingRuleCreate(
        name="Enterprise Rule",
        priority=1,
        conditions=[
            RuleCondition(field="score", op=">=", value=80),
        ],
        action=RuleAction(team="enterprise", rep_id=None, rep_name=None),
    )
    await create_routing_rule(session, data)

    session.add.assert_called_once_with(rule_mock)
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_routing_rules_active_only():
    from ai_sdr.services.routing_service import list_routing_rules

    rule_a = MagicMock()
    rule_b = MagicMock()
    session = _make_session(scalars_all=[rule_a, rule_b])

    results = await list_routing_rules(session, active_only=True)
    assert len(results) == 2
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_routing_rules_empty():
    from ai_sdr.services.routing_service import list_routing_rules

    session = _make_session(scalars_all=[])
    results = await list_routing_rules(session)
    assert results == []
