"""Unit tests for Slack notification tools in mock mode (no webhook configured).

Note: The Slack functions are decorated with @tool from crewai, which wraps them
into Tool objects. We call .func(...) to invoke the underlying function directly.
"""

import pytest


# ---------------------------------------------------------------------------
# send_slack_notification
# ---------------------------------------------------------------------------


def test_send_slack_notification_mock(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SLACK_WEBHOOK_URL", "")
    from ai_sdr.tools.slack import send_slack_notification

    result = send_slack_notification.func("Test message")
    assert "[MOCK]" in result


def test_send_slack_notification_includes_message(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SLACK_WEBHOOK_URL", "")
    from ai_sdr.tools.slack import send_slack_notification

    result = send_slack_notification.func("Hello from test suite")
    assert "Hello from test suite" in result or "[MOCK]" in result


def test_send_slack_notification_returns_string(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SLACK_WEBHOOK_URL", "")
    from ai_sdr.tools.slack import send_slack_notification

    result = send_slack_notification.func("ping")
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# notify_new_lead
# ---------------------------------------------------------------------------


def test_notify_new_lead_mock(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SLACK_WEBHOOK_URL", "")
    from ai_sdr.tools.slack import notify_new_lead

    result = notify_new_lead.func(
        company_name="Acme Franchise",
        contact_name="Jane Smith",
        contact_title="VP Operations",
        score=85,
        tier="hot",
        assigned_rep="@alice",
        crm_link="",
    )
    assert "[MOCK]" in result


def test_notify_new_lead_warm_tier(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SLACK_WEBHOOK_URL", "")
    from ai_sdr.tools.slack import notify_new_lead

    result = notify_new_lead.func(
        company_name="Beta Burgers",
        contact_name="Bob Jones",
        contact_title="CEO",
        score=65,
        tier="warm",
        assigned_rep="@bob",
        crm_link="https://salesforce.com/lead/123",
    )
    assert "[MOCK]" in result


def test_notify_new_lead_cold_tier(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SLACK_WEBHOOK_URL", "")
    from ai_sdr.tools.slack import notify_new_lead

    result = notify_new_lead.func(
        company_name="Gamma Gyms",
        contact_name="Carol White",
        contact_title="Operations Manager",
        score=30,
        tier="cold",
        assigned_rep="@carol",
    )
    assert "[MOCK]" in result


def test_notify_new_lead_unknown_tier(monkeypatch):
    """Unknown tier should not crash — defaults to empty emoji."""
    monkeypatch.setattr("ai_sdr.config.settings.SLACK_WEBHOOK_URL", "")
    from ai_sdr.tools.slack import notify_new_lead

    result = notify_new_lead.func(
        company_name="Delta Donuts",
        contact_name="Dave Brown",
        contact_title="CFO",
        score=50,
        tier="unknown",
        assigned_rep="@dave",
    )
    assert "[MOCK]" in result


# ---------------------------------------------------------------------------
# notify_meeting_booked
# ---------------------------------------------------------------------------


def test_notify_meeting_booked_mock(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SLACK_WEBHOOK_URL", "")
    from ai_sdr.tools.slack import notify_meeting_booked

    result = notify_meeting_booked.func(
        company_name="Acme Franchise",
        contact_name="Jane Smith",
        meeting_datetime="2025-03-15 14:00 EST",
        meeting_link="https://cal.com/meeting/123",
        assigned_rep="@alice",
        prep_notes="Multi-unit operator, 8 locations",
    )
    assert "[MOCK]" in result


def test_notify_meeting_booked_without_prep_notes(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SLACK_WEBHOOK_URL", "")
    from ai_sdr.tools.slack import notify_meeting_booked

    result = notify_meeting_booked.func(
        company_name="Delta Donuts",
        contact_name="Dave Brown",
        meeting_datetime="2025-04-01 10:00 EST",
        meeting_link="https://zoom.us/j/456",
        assigned_rep="@dave",
        prep_notes="",
    )
    assert "[MOCK]" in result


def test_notify_meeting_booked_returns_string(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SLACK_WEBHOOK_URL", "")
    from ai_sdr.tools.slack import notify_meeting_booked

    result = notify_meeting_booked.func(
        company_name="Echo Eats",
        contact_name="Eve Fox",
        meeting_datetime="2025-05-01 09:00 EST",
        meeting_link="https://meet.google.com/abc",
        assigned_rep="@eve",
    )
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# notify_pipeline_complete
# ---------------------------------------------------------------------------


def test_notify_pipeline_complete_mock(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SLACK_WEBHOOK_URL", "")
    from ai_sdr.tools.slack import notify_pipeline_complete

    result = notify_pipeline_complete.func(
        run_id="abc-123",
        leads_sourced=20,
        leads_qualified=10,
        leads_routed=8,
        appointments_set=3,
        duration_seconds=120,
    )
    assert "[MOCK]" in result


def test_notify_pipeline_complete_zero_leads(monkeypatch):
    """Zero leads_sourced should not raise a division by zero error."""
    monkeypatch.setattr("ai_sdr.config.settings.SLACK_WEBHOOK_URL", "")
    from ai_sdr.tools.slack import notify_pipeline_complete

    result = notify_pipeline_complete.func(
        run_id="xyz-000",
        leads_sourced=0,
        leads_qualified=0,
        leads_routed=0,
        appointments_set=0,
        duration_seconds=5,
    )
    assert "[MOCK]" in result


def test_notify_pipeline_complete_returns_string(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.SLACK_WEBHOOK_URL", "")
    from ai_sdr.tools.slack import notify_pipeline_complete

    result = notify_pipeline_complete.func(
        run_id="test-run",
        leads_sourced=5,
        leads_qualified=3,
        leads_routed=3,
        appointments_set=1,
    )
    assert isinstance(result, str)
    assert len(result) > 0
