"""Unit tests for email_tool — Resend-only with franchise templates."""

import pytest
from unittest.mock import patch


def test_send_email_mock_without_key(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.RESEND_API_KEY", "")
    from ai_sdr.tools.email_tool import send_email

    result = send_email("test@example.com", "Hello", "Body text")
    assert "[MOCK]" in result


def test_send_email_with_template_initial_outreach(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.RESEND_API_KEY", "")
    from ai_sdr.tools.email_tool import send_email_with_template

    result = send_email_with_template(
        "initial_outreach",
        "jane@acme.com",
        '{"first_name": "Jane", "company_name": "Acme", "franchise_count": "100", "sender_name": "Bob"}',
    )
    assert "[MOCK]" in result
    assert "Acme" in result


def test_send_email_with_template_invalid_template(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.RESEND_API_KEY", "")
    from ai_sdr.tools.email_tool import send_email_with_template

    result = send_email_with_template("nonexistent", "test@test.com", "{}")
    assert "Unknown template" in result


def test_send_email_with_template_franchise_expansion(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.RESEND_API_KEY", "")
    from ai_sdr.tools.email_tool import send_email_with_template

    result = send_email_with_template(
        "franchise_expansion",
        "bob@burgers.com",
        '{"first_name": "Bob", "company_name": "Burgers Inc", "franchise_count": "50", "sender_name": "Alice"}',
    )
    assert "[MOCK]" in result
    assert "Burgers Inc" in result


def test_send_email_with_template_follow_up_1(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.RESEND_API_KEY", "")
    from ai_sdr.tools.email_tool import send_email_with_template

    result = send_email_with_template(
        "follow_up_1",
        "carol@corp.com",
        '{"first_name": "Carol", "company_name": "Corp", "buying_signal": "opened a new location", "sender_name": "Dave"}',
    )
    assert "[MOCK]" in result
    assert "Corp" in result


def test_send_email_with_template_follow_up_2(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.RESEND_API_KEY", "")
    from ai_sdr.tools.email_tool import send_email_with_template

    result = send_email_with_template(
        "follow_up_2",
        "eve@enterprise.com",
        '{"first_name": "Eve", "company_name": "Enterprise", "peer_brand": "Rival Co", "next_quarter": "3", "sender_name": "Frank"}',
    )
    assert "[MOCK]" in result


def test_send_email_with_template_meeting_booked(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.RESEND_API_KEY", "")
    from ai_sdr.tools.email_tool import send_email_with_template

    result = send_email_with_template(
        "meeting_booked",
        "grace@group.com",
        '{"first_name": "Grace", "company_name": "Group LLC", "meeting_datetime": "Monday 3pm", "prep_link": "https://example.com/prep", "meeting_link": "https://zoom.us/j/123", "sender_name": "Hank"}',
    )
    assert "[MOCK]" in result
    assert "Group LLC" in result


def test_check_email_status_mock_without_key(monkeypatch):
    monkeypatch.setattr("ai_sdr.config.settings.RESEND_API_KEY", "")
    from ai_sdr.tools.email_tool import check_email_status

    result = check_email_status("msg_abc123")
    assert "[MOCK]" in result
    assert "msg_abc123" in result


def test_send_email_with_template_missing_variables_does_not_crash(monkeypatch):
    """Template with missing variables should fall back to raw template text."""
    monkeypatch.setattr("ai_sdr.config.settings.RESEND_API_KEY", "")
    from ai_sdr.tools.email_tool import send_email_with_template

    # Pass empty variables — should not raise, falls back to raw template
    result = send_email_with_template("initial_outreach", "test@test.com", "{}")
    assert "[MOCK]" in result or "Error" in result


def test_send_email_with_template_invalid_json_variables(monkeypatch):
    """Invalid JSON for variables should not crash — falls back to empty dict."""
    monkeypatch.setattr("ai_sdr.config.settings.RESEND_API_KEY", "")
    from ai_sdr.tools.email_tool import send_email_with_template

    result = send_email_with_template("initial_outreach", "test@test.com", "not-json")
    assert "[MOCK]" in result or "Error" in result


def test_all_templates_exist():
    """Verify all 5 expected templates are registered."""
    from ai_sdr.tools.email_tool import _TEMPLATES

    expected = {"initial_outreach", "franchise_expansion", "follow_up_1", "follow_up_2", "meeting_booked"}
    assert set(_TEMPLATES.keys()) == expected


def test_no_sendgrid_references():
    """Ensure SendGrid code has been fully removed."""
    import inspect
    import ai_sdr.tools.email_tool as mod

    source = inspect.getsource(mod)
    assert "sendgrid" not in source.lower()
    assert "_send_via_sendgrid" not in source
