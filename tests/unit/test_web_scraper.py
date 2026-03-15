"""Unit tests for web_scraper tools."""

import httpx
import respx


@respx.mock
def test_scrape_website_returns_text():
    """scrape_website extracts visible text from HTML."""
    respx.get("https://example.com").mock(
        return_value=httpx.Response(
            200,
            html="<html><body><p>Hello world</p></body></html>",
        )
    )
    from ai_sdr.tools.web_scraper import scrape_website

    result = scrape_website.func("https://example.com")
    assert "Hello world" in result


@respx.mock
def test_scrape_website_strips_scripts():
    """scrape_website removes script/style tags from output."""
    respx.get("https://example.com/page").mock(
        return_value=httpx.Response(
            200,
            html=(
                "<html><body>"
                "<script>var x = 1;</script>"
                "<p>Visible content</p>"
                "</body></html>"
            ),
        )
    )
    from ai_sdr.tools.web_scraper import scrape_website

    result = scrape_website.func("https://example.com/page")
    assert "Visible content" in result
    assert "var x = 1" not in result


@respx.mock
def test_scrape_website_handles_http_error():
    """scrape_website returns error string on HTTP failure."""
    respx.get("https://broken.example.com").mock(
        return_value=httpx.Response(404)
    )
    from ai_sdr.tools.web_scraper import scrape_website

    result = scrape_website.func("https://broken.example.com")
    assert result.startswith("Error scraping")


@respx.mock
def test_detect_tech_stack_finds_wordpress():
    """detect_tech_stack identifies WordPress from wp-content in HTML."""
    respx.get("https://wpsite.example.com").mock(
        return_value=httpx.Response(
            200,
            html=(
                '<html><head>'
                '<link rel="stylesheet" href="/wp-content/themes/main/style.css">'
                '</head><body><p>A WordPress site</p></body></html>'
            ),
        )
    )
    from ai_sdr.tools.web_scraper import detect_tech_stack

    result = detect_tech_stack.func("https://wpsite.example.com")
    assert "WordPress" in result


@respx.mock
def test_detect_tech_stack_finds_hubspot():
    """detect_tech_stack identifies HubSpot from script URL."""
    respx.get("https://hssite.example.com").mock(
        return_value=httpx.Response(
            200,
            html=(
                '<html><head>'
                '<script src="//js.hs-scripts.com/12345.js"></script>'
                '</head><body></body></html>'
            ),
        )
    )
    from ai_sdr.tools.web_scraper import detect_tech_stack

    result = detect_tech_stack.func("https://hssite.example.com")
    assert "HubSpot" in result


@respx.mock
def test_detect_tech_stack_no_tech_found():
    """detect_tech_stack returns informative message when nothing is detected."""
    respx.get("https://plain.example.com").mock(
        return_value=httpx.Response(
            200,
            html="<html><body><p>Plain HTML site</p></body></html>",
        )
    )
    from ai_sdr.tools.web_scraper import detect_tech_stack

    result = detect_tech_stack.func("https://plain.example.com")
    assert "No recognizable technologies" in result


@respx.mock
def test_extract_contact_emails_finds_emails():
    """extract_contact_emails returns email addresses present in page HTML."""
    respx.get("https://contact.example.com").mock(
        return_value=httpx.Response(
            200,
            html=(
                "<html><body>"
                "<p>Contact us at info@acmecorp.com or sales@acmecorp.com</p>"
                "</body></html>"
            ),
        )
    )
    from ai_sdr.tools.web_scraper import extract_contact_emails

    result = extract_contact_emails.func("https://contact.example.com")
    assert "info@acmecorp.com" in result
    assert "sales@acmecorp.com" in result


@respx.mock
def test_extract_contact_emails_filters_noise():
    """extract_contact_emails excludes example/test addresses and image extensions."""
    respx.get("https://noisy.example.com").mock(
        return_value=httpx.Response(
            200,
            html=(
                "<html><body>"
                "<img src='icon@2x.png'>"
                "<p>Email: example@example.com or real@company.io</p>"
                "</body></html>"
            ),
        )
    )
    from ai_sdr.tools.web_scraper import extract_contact_emails

    result = extract_contact_emails.func("https://noisy.example.com")
    # The real address should be present
    assert "real@company.io" in result
    # Noise addresses should be filtered
    assert "icon@2x.png" not in result


@respx.mock
def test_extract_contact_emails_none_found():
    """extract_contact_emails returns informative message when no emails on page."""
    respx.get("https://noemail.example.com").mock(
        return_value=httpx.Response(
            200,
            html="<html><body><p>No contact info here.</p></body></html>",
        )
    )
    from ai_sdr.tools.web_scraper import extract_contact_emails

    result = extract_contact_emails.func("https://noemail.example.com")
    assert "No email addresses found" in result


@respx.mock
def test_scrape_team_page_finds_linkedin():
    """scrape_team_page returns LinkedIn profile links found on the page."""
    respx.get("https://company.example.com/team").mock(
        return_value=httpx.Response(
            200,
            html=(
                "<html><body>"
                '<a href="https://linkedin.com/in/jane-doe">Jane Doe</a>'
                '<a href="https://linkedin.com/in/john-smith">John Smith</a>'
                "</body></html>"
            ),
        )
    )
    from ai_sdr.tools.web_scraper import scrape_team_page

    result = scrape_team_page.func("https://company.example.com/team")
    assert "linkedin.com/in/jane-doe" in result
    assert "linkedin.com/in/john-smith" in result


@respx.mock
def test_scrape_franchise_info_finds_unit_count():
    """scrape_franchise_info extracts location count patterns from page text."""
    respx.get("https://franchise.example.com").mock(
        return_value=httpx.Response(
            200,
            html=(
                "<html><body>"
                "<p>We operate 1,200 locations across North America.</p>"
                "<p>Our franchise fee starts at $35,000.</p>"
                "</body></html>"
            ),
        )
    )
    from ai_sdr.tools.web_scraper import scrape_franchise_info

    result = scrape_franchise_info.func("https://franchise.example.com")
    assert "1,200 locations" in result
