"""Slack notification tools with Block Kit support."""

import httpx
from crewai.tools import tool

from ai_sdr.config import settings


@tool
def send_slack_notification(message: str) -> str:
    """Send a notification to Slack. Used to alert sales reps about new leads
    or booked meetings.

    Args:
        message: The notification message to send.

    Returns:
        Confirmation or error message.
    """
    if not settings.SLACK_WEBHOOK_URL:
        return f"[MOCK] Would send Slack notification: {message[:200]}. Set SLACK_WEBHOOK_URL to enable."

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                settings.SLACK_WEBHOOK_URL,
                json={"text": message},
            )
            response.raise_for_status()
            return "Slack notification sent successfully."
    except Exception as e:
        return f"Error sending Slack notification: {e}"


def _send_blocks(blocks: list) -> str:
    """Send Block Kit payload to Slack webhook."""
    if not settings.SLACK_WEBHOOK_URL:
        return "[MOCK] Slack Block Kit notification (configure SLACK_WEBHOOK_URL)."
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(settings.SLACK_WEBHOOK_URL, json={"blocks": blocks})
            response.raise_for_status()
            return "Slack notification sent."
    except Exception as e:
        return f"Error sending Slack notification: {e}"


@tool
def notify_new_lead(
    company_name: str,
    contact_name: str,
    contact_title: str,
    score: int,
    tier: str,
    assigned_rep: str,
    crm_link: str = "",
) -> str:
    """Notify a sales rep about a new qualified franchise lead via Slack with Block Kit formatting.

    Args:
        company_name: Franchise company name.
        contact_name: Primary contact's full name.
        contact_title: Contact's title.
        score: ICP score (0-100).
        tier: Lead tier (hot/warm/cold).
        assigned_rep: Rep name or @handle.
        crm_link: Optional Salesforce link.

    Returns:
        Confirmation or error.
    """
    tier_emoji = {"hot": ":fire:", "warm": ":sun_with_face:", "cold": ":snowflake:"}.get(
        tier.lower(), ""
    )
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"New Franchise Lead: {company_name}"},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Contact:*\n{contact_name} — {contact_title}"},
                {"type": "mrkdwn", "text": f"*Score:*\n{score}/100 {tier_emoji} {tier.upper()}"},
            ],
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Assigned to:*\n{assigned_rep}"},
                {"type": "mrkdwn", "text": f"*CRM:*\n{crm_link or 'Not yet in CRM'}"},
            ],
        },
    ]
    return _send_blocks(blocks)


@tool
def notify_meeting_booked(
    company_name: str,
    contact_name: str,
    meeting_datetime: str,
    meeting_link: str,
    assigned_rep: str,
    prep_notes: str = "",
) -> str:
    """Notify a sales rep about a booked meeting via Slack.

    Args:
        company_name: Franchise company name.
        contact_name: Prospect's name.
        meeting_datetime: When the meeting is scheduled.
        meeting_link: Cal.com or video link.
        assigned_rep: Rep's name or @handle.
        prep_notes: Optional context/prep notes.

    Returns:
        Confirmation or error.
    """
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f":calendar: Meeting Booked: {company_name}"},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Prospect:*\n{contact_name}"},
                {"type": "mrkdwn", "text": f"*Time:*\n{meeting_datetime}"},
            ],
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Rep:*\n{assigned_rep}"},
                {"type": "mrkdwn", "text": f"*Join:*\n<{meeting_link}|Video link>"},
            ],
        },
    ]
    if prep_notes:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Prep notes:* {prep_notes}"},
        })
    return _send_blocks(blocks)


@tool
def notify_pipeline_complete(
    run_id: str,
    leads_sourced: int,
    leads_qualified: int,
    leads_routed: int,
    appointments_set: int,
    duration_seconds: int = 0,
) -> str:
    """Post a pipeline run completion summary to Slack.

    Args:
        run_id: Pipeline run UUID.
        leads_sourced: Number of leads found.
        leads_qualified: Number of leads that passed ICP scoring.
        leads_routed: Number of leads routed to reps.
        appointments_set: Number of meetings booked.
        duration_seconds: How long the run took.

    Returns:
        Confirmation or error.
    """
    rate = (
        f"{int(appointments_set / leads_sourced * 100)}%"
        if leads_sourced > 0 else "N/A"
    )
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": ":rocket: Pipeline Run Complete"},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Sourced:*\n{leads_sourced}"},
                {"type": "mrkdwn", "text": f"*Qualified:*\n{leads_qualified}"},
                {"type": "mrkdwn", "text": f"*Routed:*\n{leads_routed}"},
                {"type": "mrkdwn", "text": f"*Meetings:*\n{appointments_set}"},
            ],
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Run ID: {run_id} | Conversion: {rate} | Duration: {duration_seconds}s",
                }
            ],
        },
    ]
    return _send_blocks(blocks)
