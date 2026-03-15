"""Lead enrichment tool — free search-based using DuckDuckGo (no paid APIs)."""
import re
import socket
import time

from crewai.tools import tool

from ai_sdr.config import settings

_cache: dict = {}
_cache_ttl = 3600  # 1 hour


def _ddg_search(query: str, max_results: int = 5) -> list[dict]:
    """DuckDuckGo search with simple in-memory cache."""
    cache_key = f"{query}:{max_results}"
    now = time.time()
    if cache_key in _cache and now - _cache[cache_key]["ts"] < _cache_ttl:
        return _cache[cache_key]["data"]
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        _cache[cache_key] = {"ts": now, "data": results}
        return results
    except Exception:
        return []


@tool
def search_company_info(domain: str) -> str:
    """Search for company information using free web search. Returns company overview,
    industry, and general facts scraped from public sources.

    Args:
        domain: Company website domain (e.g., 'acme.com').

    Returns:
        Company information snippets with confidence rating.
    """
    query = f'site:{domain} OR "{domain}" company about employees industry'
    results = _ddg_search(query, max_results=settings.DUCKDUCKGO_MAX_RESULTS)
    if not results:
        return f"No information found for {domain}"
    snippets = [f"- {r['title']}: {r['body'][:200]}" for r in results[:5]]
    return f"Company info for {domain} (confidence: medium):\n" + "\n".join(snippets)


@tool
def search_franchise_info(company_name: str) -> str:
    """Search franchise directories to find location counts and franchise details
    for a given company.

    Args:
        company_name: Name of the franchise company.

    Returns:
        Location count mentions and franchise info snippets.
    """
    query = (
        f'"{company_name}" franchise locations units count '
        f"site:franchisegator.com OR site:entrepreneur.com OR site:franchisegrade.com"
    )
    results = _ddg_search(query, max_results=settings.DUCKDUCKGO_MAX_RESULTS)
    if not results:
        query = f'"{company_name}" franchise "number of locations"'
        results = _ddg_search(query, max_results=settings.DUCKDUCKGO_MAX_RESULTS)

    if not results:
        return f"No franchise information found for {company_name}"

    output_lines = []
    for r in results:
        body = r.get("body", "")
        counts = re.findall(r"(\d[\d,]+)\s*(?:locations|units|franchises)", body, re.IGNORECASE)
        if counts:
            output_lines.append(f"- {r['title']}: {counts} locations/units — {body[:200]}")
        else:
            output_lines.append(f"- {r['title']}: {body[:200]}")

    return f"Franchise info for {company_name}:\n" + "\n".join(output_lines)


@tool
def search_buying_signals(company_name: str, domain: str) -> str:
    """Search for recent buying signals including funding events, hiring activity,
    and expansion plans for a given company.

    Args:
        company_name: Name of the company to research.
        domain: Company website domain.

    Returns:
        Up to 6 buying signal snippets, or a message if none found.
    """
    signals = []

    # Funding signals
    funding_results = _ddg_search(
        f'"{company_name}" funding raised investment 2024 2025',
        max_results=settings.DUCKDUCKGO_MAX_RESULTS,
    )
    for r in funding_results:
        body = r.get("body", "").lower()
        if any(kw in body for kw in ["million", "funding", "raised", "series"]):
            signals.append(f"[FUNDING] {r['title']}: {r['body'][:200]}")

    # Hiring signals
    hiring_results = _ddg_search(
        f'"{company_name}" hiring "head of" OR "VP of" OR "director" 2024 2025',
        max_results=settings.DUCKDUCKGO_MAX_RESULTS,
    )
    for r in hiring_results:
        signals.append(f"[HIRING] {r['title']}: {r['body'][:200]}")

    # Expansion signals
    expansion_results = _ddg_search(
        f'"{company_name}" expansion "new locations" OR "new markets" OR "opening" 2024 2025',
        max_results=settings.DUCKDUCKGO_MAX_RESULTS,
    )
    for r in expansion_results:
        signals.append(f"[EXPANSION] {r['title']}: {r['body'][:200]}")

    if not signals:
        return f"No recent buying signals found for {company_name}"

    return "\n".join(signals[:6])


@tool
def search_contacts(company_name: str, domain: str, title_keywords: str = "") -> str:
    """Search for contacts at a company using public web sources including LinkedIn.

    Args:
        company_name: Name of the company.
        domain: Company website domain.
        title_keywords: Optional comma-separated title keywords to search for.

    Returns:
        Found contact names/titles, or suggestion to use scrape_team_page.
    """
    titles = title_keywords.strip() if title_keywords.strip() else "VP Director Head Chief CEO COO CMO President"
    query = f'"{company_name}" {titles} site:linkedin.com/in OR site:{domain}'
    results = _ddg_search(query, max_results=settings.DUCKDUCKGO_MAX_RESULTS)

    found = []
    title_pattern = re.compile(
        r"(VP|Vice President|Director|Head of|Chief|President|CEO|COO|CMO)[^,\n]{0,60}",
        re.IGNORECASE,
    )
    for r in results:
        body = r.get("body", "")
        matches = title_pattern.findall(body)
        for match in matches:
            found.append(f"- {r['title']}: {match.strip()}")

    if not found:
        return (
            f"No contacts found for {company_name} via search. "
            f"Consider using scrape_team_page with {domain}/about or {domain}/team"
        )

    return f"Contacts found at {company_name}:\n" + "\n".join(found)


@tool
def search_competitors(company_name: str, industry: str = "") -> str:
    """Search for competitors and alternatives to a given company.

    Args:
        company_name: Name of the company.
        industry: Optional industry context to refine the search.

    Returns:
        Competitor mentions and snippets.
    """
    query = f'"{company_name}" competitors alternatives {industry}'.strip()
    results = _ddg_search(query, max_results=settings.DUCKDUCKGO_MAX_RESULTS)

    if not results:
        return f"No competitor information found for {company_name}"

    snippets = [f"- {r['title']}: {r['body'][:200]}" for r in results[:4]]
    return f"Competitors of {company_name}:\n" + "\n".join(snippets)


@tool
def verify_email_pattern(email: str, domain: str) -> str:
    """Verify whether an email address has a plausible format and that its domain
    resolves via DNS.

    Args:
        email: Email address to verify.
        domain: Domain to check DNS resolution for.

    Returns:
        INVALID, UNKNOWN, or PLAUSIBLE with reasoning.
    """
    email_pattern = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$")
    if not email_pattern.match(email):
        return f"INVALID: '{email}' does not match a valid email format."

    try:
        socket.getaddrinfo(domain, None)
        domain_resolves = True
    except socket.gaierror:
        domain_resolves = False

    if domain_resolves:
        return (
            f"PLAUSIBLE: '{email}' has valid format and domain '{domain}' resolves via DNS."
        )
    else:
        return (
            f"UNKNOWN: '{email}' has valid format but domain '{domain}' did not resolve via DNS."
        )
