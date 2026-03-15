"""Lead Qualifier agent — scores franchise leads against ICP criteria."""

from crewai import Agent

from ai_sdr.config import settings
from ai_sdr.tools.enrichment import search_company_info, search_buying_signals, search_franchise_info
from ai_sdr.tools.web_scraper import scrape_website, detect_tech_stack


def create_lead_qualifier() -> Agent:
    return Agent(
        role="Franchise Lead Qualification Analyst",
        goal=(
            "Score franchise leads 0-100 against ICP criteria. Key franchise-specific signals: "
            "unit count growth rate (>10% YoY is strong), territory white space in growing markets, "
            "FDD filing updates, hiring of franchise development staff, recent expansion announcements, "
            "and technology stack modernization (POS system upgrades are a hot signal). "
            "Assign tier: Hot (80+), Warm (50-79), Cold (<50)."
        ),
        backstory=(
            "You are a franchise industry analyst who understands the franchise buying cycle — "
            "it's longer and more complex than SaaS sales, involves franchisee approval processes, "
            "and requires understanding both the franchisor AND franchisee perspectives. "
            "You never inflate scores — a conservative 65 is worth more than an optimistic 85. "
            "You know that rapid unit expansion and FDD amendments are the strongest buying signals."
        ),
        tools=[
            search_company_info,
            search_buying_signals,
            search_franchise_info,
            detect_tech_stack,
            scrape_website,
        ],
        llm=f"{settings.LLM_PROVIDER}/{settings.LLM_MODEL_MID}",
        verbose=settings.DEBUG,
        max_iter=10,
    )
