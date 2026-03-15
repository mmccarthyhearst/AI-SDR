"""Appointment Setter agent — crafts franchise-focused outreach and books meetings."""

from crewai import Agent

from ai_sdr.config import settings
from ai_sdr.tools.calendar import check_availability, create_booking
from ai_sdr.tools.crm import sync_lead_to_crm
from ai_sdr.tools.email_tool import send_email, send_email_with_template
from ai_sdr.tools.slack import notify_new_lead, notify_meeting_booked


def create_appointment_setter() -> Agent:
    return Agent(
        role="Franchise Outreach & Meeting Specialist",
        goal=(
            "Write personalized outreach referencing franchise-specific context: "
            "location count, territory growth, brand momentum. Lead with the "
            "land-and-expand value proposition if applicable. Book meetings via Cal.com "
            "and sync leads to Salesforce. Notify reps via Slack with rich context."
        ),
        backstory=(
            "You are a franchise-focused SDR who understands the pain points unique to "
            "franchise operators: inconsistent tech across units, manual reporting, "
            "territory conflicts, and the challenge of maintaining brand standards at scale. "
            "Your outreach is never generic — you reference specific franchise counts, "
            "recent expansion news, and peer brands. You know that a franchisor with 150 "
            "locations has very different needs than a multi-unit franchisee with 7 units."
        ),
        tools=[
            send_email,
            send_email_with_template,
            check_availability,
            create_booking,
            sync_lead_to_crm,
            notify_new_lead,
            notify_meeting_booked,
        ],
        llm=f"{settings.LLM_PROVIDER}/{settings.LLM_MODEL_MID}",
        verbose=settings.DEBUG,
        max_iter=10,
    )
