"""Email tool — Resend adapter with franchise-specific templates."""

from crewai.tools import tool

from ai_sdr.config import settings


# Franchise email templates
_TEMPLATES = {
    "initial_outreach": {
        "subject": "Helping {company_name} grow its franchise network",
        "body": """<p>Hi {first_name},</p>
<p>I noticed {company_name} has been expanding its franchise network — {franchise_count} locations is impressive growth.</p>
<p>We help franchise brands like yours streamline operations across all units, reducing the manual overhead that comes with scaling from {franchise_count} to the next milestone.</p>
<p>Would you have 20 minutes this week to see how we've helped similar franchise brands cut operational costs by 30%?</p>
<p>Best,<br>{sender_name}</p>""",
    },
    "franchise_expansion": {
        "subject": "Land-and-expand opportunity: {company_name}",
        "body": """<p>Hi {first_name},</p>
<p>Following our work with one of {company_name}'s franchisees, I wanted to reach out about expanding that success across your full network of {franchise_count} locations.</p>
<p>When one franchise unit succeeds with a solution, the ROI multiplies across every unit in the network.</p>
<p>Open to a quick call to discuss?</p>
<p>Best,<br>{sender_name}</p>""",
    },
    "follow_up_1": {
        "subject": "Re: {company_name} — quick follow-up",
        "body": """<p>Hi {first_name},</p>
<p>I wanted to follow up on my previous note. I saw {company_name} recently {buying_signal} — that's exactly the kind of growth moment where our platform delivers the most value.</p>
<p>Happy to keep it brief — just 15 minutes to show you the ROI calculator for networks your size.</p>
<p>Best,<br>{sender_name}</p>""",
    },
    "follow_up_2": {
        "subject": "One more thought on {company_name}",
        "body": """<p>Hi {first_name},</p>
<p>Last note, I promise. Brands like {peer_brand} with similar franchise counts saw a 3x improvement in franchisee satisfaction scores after working with us.</p>
<p>If the timing isn't right now, no problem — I'll check back in Q{next_quarter}.</p>
<p>Best,<br>{sender_name}</p>""",
    },
    "meeting_booked": {
        "subject": "Confirmed: Meeting with {company_name} — prep materials",
        "body": """<p>Hi {first_name},</p>
<p>Looking forward to our call on {meeting_datetime}!</p>
<p>To make the most of our time, I've put together a brief overview of how we typically work with franchise brands at your stage. You can review it here: {prep_link}</p>
<p>Join link: {meeting_link}</p>
<p>See you then,<br>{sender_name}</p>""",
    },
}


def _send_via_resend(to_email: str, subject: str, body: str) -> str:
    """Internal Resend sender."""
    if not settings.RESEND_API_KEY:
        return (
            f"[MOCK] Would send email via Resend:\n"
            f"To: {to_email}\nSubject: {subject}\nBody: {body[:200]}...\n"
            "Set RESEND_API_KEY to enable."
        )
    try:
        import resend

        resend.api_key = settings.RESEND_API_KEY
        result = resend.Emails.send(
            {
                "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM_ADDRESS}>",
                "to": [to_email],
                "subject": subject,
                "html": body,
            }
        )
        return f"Email sent to {to_email}. Message ID: {result.get('id', 'unknown')}"
    except Exception as e:
        return f"Error sending email via Resend: {e}"


@tool
def send_email(to_email: str, subject: str, body: str) -> str:
    """Send an email to a prospect via Resend.

    Args:
        to_email: Recipient email address.
        subject: Email subject line.
        body: Email body (plain text or HTML).

    Returns:
        Confirmation with message ID, or error message.
    """
    return _send_via_resend(to_email, subject, body)


@tool
def send_email_with_template(template_name: str, to_email: str, variables: str) -> str:
    """Send a franchise-focused email using a named template.

    Available templates: initial_outreach, franchise_expansion, follow_up_1, follow_up_2, meeting_booked.

    Args:
        template_name: Name of the template to use.
        to_email: Recipient email address.
        variables: JSON string of template variables (e.g., '{"first_name": "Jane", "company_name": "Acme"}').

    Returns:
        Confirmation with message ID, or error message.
    """
    import json

    if template_name not in _TEMPLATES:
        available = ", ".join(_TEMPLATES.keys())
        return f"Unknown template '{template_name}'. Available: {available}"
    try:
        vars_dict = json.loads(variables) if isinstance(variables, str) else variables
    except (json.JSONDecodeError, TypeError):
        vars_dict = {}
    template = _TEMPLATES[template_name]
    try:
        subject = template["subject"].format_map({**vars_dict})
        body = template["body"].format_map({**vars_dict})
    except KeyError:
        subject = template["subject"]
        body = template["body"]
    return _send_via_resend(to_email, subject, body)


@tool
def check_email_status(message_id: str) -> str:
    """Check the delivery status of a sent email via Resend.

    Args:
        message_id: The Resend message ID returned by send_email.

    Returns:
        Delivery status (delivered, bounced, etc.) or error.
    """
    if not settings.RESEND_API_KEY:
        return f"[MOCK] Email {message_id} status: delivered. Set RESEND_API_KEY to enable."
    try:
        import resend

        resend.api_key = settings.RESEND_API_KEY
        email = resend.Emails.get(message_id)
        return f"Email {message_id}: {email}"
    except Exception as e:
        return f"Error checking email status {message_id}: {e}"
