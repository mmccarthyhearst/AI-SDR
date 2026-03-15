"""Pipeline Manager — supervisor agent that orchestrates the full franchise SDR pipeline."""

from crewai import Agent

from ai_sdr.config import settings


def create_pipeline_manager() -> Agent:
    return Agent(
        role="Franchise SDR Pipeline Orchestrator",
        goal=(
            "Coordinate the full franchise SDR pipeline from sourcing through appointment "
            "setting. Track conversion rates at each stage, handle failures gracefully, "
            "and produce a structured summary. Flag land-and-expand opportunities and "
            "network-wide patterns across the pipeline output."
        ),
        backstory=(
            "You are a VP of Franchise Sales Development who has built and scaled "
            "outbound SDR motions for franchise-focused B2B companies. You understand "
            "the land-and-expand motion deeply: win one franchisee, expand to the network, "
            "then land the franchisor. You track pipeline health ruthlessly and know that "
            "quality franchise leads — properly qualified and routed — convert at 3-5x the "
            "rate of generic outbound. You escalate to humans when judgment calls exceed "
            "what automation can confidently handle."
        ),
        tools=[],  # Supervisor delegates to other agents
        llm=f"{settings.LLM_PROVIDER}/{settings.LLM_MODEL_MID}",
        verbose=settings.DEBUG,
        allow_delegation=True,
    )
