"""Web scraping tool for lead discovery."""

import re
import time

import httpx
from bs4 import BeautifulSoup
from crewai.tools import tool

from ai_sdr.config import settings

_last_request_time = 0.0


def _rate_limit():
    """Simple rate limiter for scraping."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < settings.SCRAPER_RATE_LIMIT_SECONDS:
        time.sleep(settings.SCRAPER_RATE_LIMIT_SECONDS - elapsed)
    _last_request_time = time.time()


@tool
def scrape_website(url: str) -> str:
    """Scrape a website URL and return its text content. Useful for researching
    companies and finding contact information on their websites.

    Args:
        url: The URL to scrape.

    Returns:
        The text content of the page, or an error message.
    """
    _rate_limit()
    try:
        with httpx.Client(
            headers={"User-Agent": settings.SCRAPER_USER_AGENT},
            follow_redirects=True,
            timeout=15.0,
        ) as client:
            response = client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        # Truncate to avoid context overflow
        return text[:8000]
    except Exception as e:
        return f"Error scraping {url}: {e}"


@tool
def search_companies(query: str, max_results: int = 5) -> str:
    """Search the web for companies matching a query using DuckDuckGo.

    Args:
        query: Search query (e.g., 'franchise brands 100+ locations food beverage').
        max_results: Maximum number of results.

    Returns:
        List of company names and URLs found.
    """
    try:
        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"- {r['title']}: {r['href']}\n  {r['body'][:150]}")
        return "\n".join(results) if results else f"No results for: {query}"
    except Exception as e:
        return f"Search error: {e}"


@tool
def scrape_team_page(url: str) -> str:
    """Scrape a company's team or about page to find names, titles, and LinkedIn links.

    Args:
        url: URL of the team/about page to scrape.

    Returns:
        List of team members with LinkedIn links, or an error message.
    """
    _rate_limit()
    try:
        with httpx.Client(
            headers={"User-Agent": settings.SCRAPER_USER_AGENT},
            follow_redirects=True,
            timeout=15.0,
        ) as client:
            response = client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "linkedin.com/in/" in href:
                text = a_tag.get_text(strip=True) or a_tag.get("aria-label", "")
                # Try to get nearby text (parent element) for name/title context
                parent = a_tag.parent
                parent_text = parent.get_text(separator=" ", strip=True) if parent else ""
                label = text or parent_text[:80] or "LinkedIn profile"
                results.append(f"- {label} | LinkedIn: {href}")
                if len(results) >= 20:
                    break

        if not results:
            return f"No LinkedIn profiles found on {url}"
        return "\n".join(results)
    except Exception as e:
        return f"Error scraping team page {url}: {e}"


@tool
def detect_tech_stack(url: str) -> str:
    """Detect technology stack used by a website from its HTML and headers.

    Checks for common platforms and marketing/analytics tools including WordPress,
    Shopify, Google Analytics, Segment, HubSpot, Marketo, Salesforce/Pardot,
    Intercom, and Drift.

    Args:
        url: The website URL to inspect.

    Returns:
        Formatted list of detected technologies, or an error message.
    """
    _rate_limit()
    try:
        with httpx.Client(
            headers={"User-Agent": settings.SCRAPER_USER_AGENT},
            follow_redirects=True,
            timeout=15.0,
        ) as client:
            response = client.get(url)
            response.raise_for_status()

        html = response.text
        detected = []

        # Check x-powered-by header
        powered_by = response.headers.get("x-powered-by", "")
        if powered_by:
            detected.append(f"Server: {powered_by}")

        # CMS / e-commerce platforms
        if "wp-content" in html or "wp-includes" in html:
            detected.append("WordPress")
        if "cdn.shopify.com" in html or "shopify" in html.lower():
            detected.append("Shopify")

        # Analytics
        if "gtag" in html or "google-analytics.com" in html or "googletagmanager.com" in html:
            detected.append("Google Analytics / GTM")
        if "segment.com/analytics" in html or "analytics.js" in html:
            detected.append("Segment")

        # Marketing / CRM
        if "js.hs-scripts.com" in html or "hubspot.com" in html:
            detected.append("HubSpot")
        if "munchkin.marketo" in html or "marketo.com" in html:
            detected.append("Marketo")
        if "pardot.com" in html or "pi.pardot.com" in html:
            detected.append("Salesforce Pardot")

        # Chat / engagement
        if "intercomcdn.com" in html or "widget.intercom.io" in html:
            detected.append("Intercom")
        if "drift.com/drift-frame" in html or "js.driftt.com" in html:
            detected.append("Drift")

        if not detected:
            return f"No recognizable technologies detected on {url}"
        return f"Technologies detected on {url}:\n" + "\n".join(f"- {t}" for t in detected)
    except Exception as e:
        return f"Error detecting tech stack for {url}: {e}"


@tool
def scrape_franchise_info(url: str) -> str:
    """Scrape franchise-specific information from a website.

    Looks for location/unit counts, franchise fee ranges, and franchise-related
    keywords such as territory, royalty, and franchisee.

    Args:
        url: The website URL to scrape for franchise information.

    Returns:
        Summary of franchise information found, or an error message.
    """
    _rate_limit()
    try:
        with httpx.Client(
            headers={"User-Agent": settings.SCRAPER_USER_AGENT},
            follow_redirects=True,
            timeout=15.0,
        ) as client:
            response = client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)

        findings = []

        # Find location/unit count patterns
        location_pattern = re.compile(
            r"(\d[\d,]+)\s*(?:locations|units|restaurants|stores|franchises)",
            re.IGNORECASE,
        )
        for match in location_pattern.finditer(text):
            findings.append(f"Unit count: {match.group(0)}")

        # Find franchise fee patterns ($X,XXX - $X,XXX franchise fee)
        fee_pattern = re.compile(
            r"\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?\s*(?:franchise\s+fee|initial\s+fee|franchis\w*\s+invest)",
            re.IGNORECASE,
        )
        for match in fee_pattern.finditer(text):
            findings.append(f"Fee info: {match.group(0)}")

        # Find paragraphs with franchise keywords
        franchise_keywords = ["franchise", "franchisee", "territory", "royalty"]
        for para in soup.find_all(["p", "li", "div"]):
            para_text = para.get_text(separator=" ", strip=True)
            if len(para_text) < 30 or len(para_text) > 500:
                continue
            if any(kw in para_text.lower() for kw in franchise_keywords):
                findings.append(f"Info: {para_text[:200]}")

        # Deduplicate and limit
        seen = set()
        unique_findings = []
        for f in findings:
            if f not in seen:
                seen.add(f)
                unique_findings.append(f)
            if len(unique_findings) >= 6:
                break

        if not unique_findings:
            return f"No franchise information found on {url}"
        return f"Franchise info from {url}:\n" + "\n".join(f"- {f}" for f in unique_findings)
    except Exception as e:
        return f"Error scraping franchise info from {url}: {e}"


@tool
def extract_contact_emails(url: str) -> str:
    """Extract contact email addresses from a website page.

    Filters out example/test addresses and image file extensions. Attempts to
    infer the company email pattern from found addresses.

    Args:
        url: The website URL to extract emails from.

    Returns:
        List of email addresses found and inferred pattern, or an error message.
    """
    _rate_limit()
    try:
        with httpx.Client(
            headers={"User-Agent": settings.SCRAPER_USER_AGENT},
            follow_redirects=True,
            timeout=15.0,
        ) as client:
            response = client.get(url)
            response.raise_for_status()

        html = response.text
        email_pattern = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
        raw_emails = email_pattern.findall(html)

        # Filter noise
        noise_terms = {"example", "test", ".png", ".jpg", ".gif", ".svg", ".css", ".js"}
        filtered = []
        for email in raw_emails:
            email_lower = email.lower()
            if any(noise in email_lower for noise in noise_terms):
                continue
            # Skip emails with invalid TLD-like endings from HTML attributes
            if re.search(r"\.(png|jpg|gif|svg|css|js|json|xml|html)$", email_lower):
                continue
            filtered.append(email)

        # Deduplicate preserving order
        seen: set = set()
        unique_emails = []
        for e in filtered:
            if e.lower() not in seen:
                seen.add(e.lower())
                unique_emails.append(e)

        if not unique_emails:
            return f"No email addresses found on {url}"

        # Infer email pattern from found addresses
        pattern_hint = ""
        for email in unique_emails:
            local, domain = email.split("@", 1)
            if "." in local:
                pattern_hint = f"Pattern hint: firstname.lastname@{domain}"
                break
            elif len(local) <= 3:
                pattern_hint = f"Pattern hint: initials@{domain}"
                break

        result_lines = [f"Emails found on {url}:"]
        result_lines.extend(f"- {e}" for e in unique_emails[:20])
        if pattern_hint:
            result_lines.append(pattern_hint)
        return "\n".join(result_lines)
    except Exception as e:
        return f"Error extracting emails from {url}: {e}"
