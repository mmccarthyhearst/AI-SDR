"""Lead Sourcer agent — discovers franchise companies and contacts matching ICP."""

from crewai import Agent

from ai_sdr.config import settings
from ai_sdr.tools.crm import check_crm_duplicate
from ai_sdr.tools.enrichment import search_company_info, search_franchise_info, search_contacts
from ai_sdr.tools.web_scraper import (
    scrape_website,
    scrape_franchise_info,
    search_companies,
    extract_contact_emails,
)


def create_lead_sourcer() -> Agent:
    return Agent(
        role="Franchise Lead Discovery Specialist",
        goal=(
            "Find franchise organizations matching the ICP: franchisors with 50+ locations "
            "and multi-unit franchisees with 5+ units. For each company, identify the right "
            "decision-maker: VP of Operations, Director of Franchise Development, or multi-unit "
            "owner. Use franchise directories, web scraping, and DuckDuckGo search. "
            "Flag land-and-expand opportunities where we already have a franchisee in the same brand."
        ),
        backstory=(
            "You are a franchise industry sales researcher with deep knowledge of the "
            "franchise ecosystem. You understand FDD (Franchise Disclosure Document) filings, "
            "franchise directories like Franchise Gator and Entrepreneur 500, and the "
            "land-and-expand sales motion — where winning one franchisee in a brand creates "
            "a path to the entire network. You always verify data before reporting and flag "
            "when information is uncertain."
        ),
        tools=[
            scrape_website,
            scrape_franchise_info,
            search_companies,
            search_company_info,
            search_franchise_info,
            search_contacts,
            extract_contact_emails,
            check_crm_duplicate,
        ],
        llm=f"{settings.LLM_PROVIDER}/{settings.LLM_MODEL_FAST}",
        verbose=settings.DEBUG,
        max_iter=10,
    )
