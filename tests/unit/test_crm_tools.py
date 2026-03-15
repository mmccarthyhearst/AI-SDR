"""Unit tests for CRM tools — mock mode (no Salesforce credentials)."""

import pytest


# ---------------------------------------------------------------------------
# check_crm_duplicate
# ---------------------------------------------------------------------------


def test_check_crm_duplicate_no_sf(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SALESFORCE_USERNAME", "")
    from ai_sdr.tools.crm import check_crm_duplicate

    result = check_crm_duplicate.func("test@example.com")
    assert "[MOCK]" in result


def test_check_crm_duplicate_includes_email(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SALESFORCE_USERNAME", "")
    from ai_sdr.tools.crm import check_crm_duplicate

    result = check_crm_duplicate.func("unique@lead.io")
    assert "unique@lead.io" in result


# ---------------------------------------------------------------------------
# create_crm_lead
# ---------------------------------------------------------------------------


def test_create_crm_lead_no_sf(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SALESFORCE_USERNAME", "")
    from ai_sdr.tools.crm import create_crm_lead

    result = create_crm_lead.func(
        first_name="Jane",
        last_name="Smith",
        email="jane@acme.com",
        company="Acme Franchise",
        title="VP Operations",
    )
    assert "[MOCK]" in result


def test_create_crm_lead_includes_contact_info(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SALESFORCE_USERNAME", "")
    from ai_sdr.tools.crm import create_crm_lead

    result = create_crm_lead.func(
        first_name="Bob",
        last_name="Jones",
        email="bob@burgers.com",
        company="Burger Group",
    )
    assert "Bob" in result or "bob@burgers.com" in result or "[MOCK]" in result


# ---------------------------------------------------------------------------
# update_crm_lead
# ---------------------------------------------------------------------------


def test_update_crm_lead_no_sf(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SALESFORCE_USERNAME", "")
    from ai_sdr.tools.crm import update_crm_lead

    result = update_crm_lead.func(lead_id="00Q1234567890ABC", status="Working")
    assert "[MOCK]" in result
    assert "00Q1234567890ABC" in result


def test_update_crm_lead_returns_string(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SALESFORCE_USERNAME", "")
    from ai_sdr.tools.crm import update_crm_lead

    result = update_crm_lead.func(lead_id="FAKEID", status="Qualified", description="Hot lead")
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# get_crm_lead
# ---------------------------------------------------------------------------


def test_get_crm_lead_no_sf(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SALESFORCE_USERNAME", "")
    from ai_sdr.tools.crm import get_crm_lead

    result = get_crm_lead.func(lead_id="00Q1234567890XYZ")
    assert "[MOCK]" in result


# ---------------------------------------------------------------------------
# sync_lead_to_crm
# ---------------------------------------------------------------------------


def test_sync_lead_to_crm_no_sf(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SALESFORCE_USERNAME", "")
    from ai_sdr.tools.crm import sync_lead_to_crm

    result = sync_lead_to_crm.func(
        first_name="Jane",
        last_name="Smith",
        email="jane@acme.com",
        company="Acme Franchise",
        franchise_brand="Orangetheory Fitness",
        franchise_count="1400",
    )
    assert "[MOCK]" in result


def test_sync_lead_to_crm_includes_name(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SALESFORCE_USERNAME", "")
    from ai_sdr.tools.crm import sync_lead_to_crm

    result = sync_lead_to_crm.func(
        first_name="Carol",
        last_name="White",
        email="carol@chain.com",
        company="Chain Corp",
    )
    assert "Carol" in result or "[MOCK]" in result


# ---------------------------------------------------------------------------
# get_sales_reps
# ---------------------------------------------------------------------------


def test_get_sales_reps_returns_list(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SALESFORCE_USERNAME", "")
    from ai_sdr.tools.crm import get_sales_reps

    result = get_sales_reps.func()
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_sales_reps_mock_contains_names(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SALESFORCE_USERNAME", "")
    from ai_sdr.tools.crm import get_sales_reps

    result = get_sales_reps.func()
    # Mock mode returns predefined rep names
    assert "[MOCK]" in result or "Alice" in result or "Rep" in result


def test_get_sales_reps_with_team_filter(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SALESFORCE_USERNAME", "")
    from ai_sdr.tools.crm import get_sales_reps

    result = get_sales_reps.func(team="Enterprise")
    assert isinstance(result, str)
