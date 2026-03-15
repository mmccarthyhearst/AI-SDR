"""CRM tool — Salesforce adapter via simple-salesforce."""

from crewai.tools import tool

from ai_sdr.config import settings


def _get_sf_client():
    """Create a Salesforce client. Returns None if credentials not configured."""
    if not all([settings.SALESFORCE_USERNAME, settings.SALESFORCE_PASSWORD]):
        return None

    from simple_salesforce import Salesforce

    return Salesforce(
        username=settings.SALESFORCE_USERNAME,
        password=settings.SALESFORCE_PASSWORD,
        security_token=settings.SALESFORCE_SECURITY_TOKEN,
        domain=settings.SALESFORCE_DOMAIN,
    )


@tool
def check_crm_duplicate(email: str) -> str:
    """Check if a contact already exists in Salesforce by email.

    Args:
        email: The email address to check.

    Returns:
        Whether the contact exists and any existing lead/opportunity data.
    """
    sf = _get_sf_client()
    if sf is None:
        return f"[MOCK] CRM check for {email}: No existing record found. Configure Salesforce credentials to enable live CRM checks."

    try:
        result = sf.query(
            f"SELECT Id, Name, Email, Account.Name FROM Contact WHERE Email = '{email}' LIMIT 1"
        )
        if result["totalSize"] > 0:
            record = result["records"][0]
            return (
                f"DUPLICATE FOUND: {record['Name']} at {record.get('Account', {}).get('Name', 'Unknown')} "
                f"(Salesforce ID: {record['Id']})"
            )
        return f"No existing record for {email} in Salesforce."
    except Exception as e:
        return f"Error checking CRM for {email}: {e}"


@tool
def create_crm_lead(
    first_name: str,
    last_name: str,
    email: str,
    company: str,
    title: str = "",
    description: str = "",
) -> str:
    """Create a new Lead record in Salesforce.

    Args:
        first_name: Contact's first name.
        last_name: Contact's last name.
        email: Contact's email.
        company: Company name.
        title: Contact's job title.
        description: Additional context about the lead.

    Returns:
        The Salesforce Lead ID if created, or error message.
    """
    sf = _get_sf_client()
    if sf is None:
        return f"[MOCK] Would create Salesforce lead: {first_name} {last_name} ({email}) at {company}. Configure Salesforce credentials to enable."

    try:
        result = sf.Lead.create(
            {
                "FirstName": first_name,
                "LastName": last_name,
                "Email": email,
                "Company": company,
                "Title": title,
                "Description": description,
                "LeadSource": "AI SDR",
            }
        )
        return f"Created Salesforce Lead: {result['id']}"
    except Exception as e:
        return f"Error creating lead in Salesforce: {e}"


@tool
def get_sales_reps(team: str = "") -> str:
    """Get a list of sales reps, optionally filtered by team.

    Args:
        team: Team name to filter by (optional).

    Returns:
        List of sales reps with their IDs and assignment info.
    """
    sf = _get_sf_client()
    if sf is None:
        return (
            "[MOCK] Sales reps:\n"
            "- Rep 1: Alice Johnson (alice@company.com) - Team: Enterprise\n"
            "- Rep 2: Bob Smith (bob@company.com) - Team: Mid-Market\n"
            "- Rep 3: Carol White (carol@company.com) - Team: SMB\n"
            "Configure Salesforce credentials for live data."
        )

    try:
        query = "SELECT Id, Name, Email, Department FROM User WHERE IsActive = true AND UserType = 'Standard'"
        if team:
            query += f" AND Department = '{team}'"
        query += " LIMIT 20"

        result = sf.query(query)
        if result["totalSize"] == 0:
            return f"No sales reps found for team: {team}"

        reps = []
        for r in result["records"]:
            reps.append(f"- {r['Name']} ({r['Email']}) - Dept: {r.get('Department', 'N/A')}")
        return "Sales reps:\n" + "\n".join(reps)
    except Exception as e:
        return f"Error fetching sales reps: {e}"


@tool
def update_crm_lead(lead_id: str, status: str, description: str = "") -> str:
    """Update an existing Salesforce Lead record.

    Args:
        lead_id: Salesforce Lead ID.
        status: New status (e.g., 'Working', 'Qualified', 'Unqualified').
        description: Additional notes to append.

    Returns:
        Success confirmation or error.
    """
    sf = _get_sf_client()
    if sf is None:
        return f"[MOCK] Would update Lead {lead_id} status to {status}."
    try:
        sf.Lead.update(lead_id, {"Status": status, "Description": description})
        return f"Updated Lead {lead_id} status to {status}"
    except Exception as e:
        return f"Error updating lead {lead_id}: {e}"


@tool
def get_crm_lead(lead_id: str) -> str:
    """Get a full Salesforce Lead record by ID.

    Args:
        lead_id: Salesforce Lead ID.

    Returns:
        Lead details as formatted text.
    """
    sf = _get_sf_client()
    if sf is None:
        return f"[MOCK] Lead {lead_id}: Jane Smith, VP Sales at Acme Corp."
    try:
        lead = sf.Lead.get(lead_id)
        return (
            f"Lead: {lead.get('FirstName', '')} {lead.get('LastName', '')}\n"
            f"Company: {lead.get('Company', 'N/A')}\n"
            f"Status: {lead.get('Status', 'N/A')}\n"
            f"Email: {lead.get('Email', 'N/A')}"
        )
    except Exception as e:
        return f"Error fetching lead {lead_id}: {e}"


@tool
def sync_lead_to_crm(
    first_name: str,
    last_name: str,
    email: str,
    company: str,
    title: str = "",
    lead_source: str = "AI SDR",
    franchise_brand: str = "",
    franchise_count: str = "",
) -> str:
    """Check if lead exists in Salesforce; create if not, update if found.
    Includes franchise custom context in description.

    Args:
        first_name: Contact's first name.
        last_name: Contact's last name.
        email: Contact's email address.
        company: Company name.
        title: Job title.
        lead_source: Source identifier.
        franchise_brand: Franchise brand name for context.
        franchise_count: Number of locations for context.

    Returns:
        Salesforce Lead ID and action taken.
    """
    sf = _get_sf_client()
    description = (
        f"Franchise Brand: {franchise_brand} | Locations: {franchise_count}"
        if franchise_brand else ""
    )
    if sf is None:
        return f"[MOCK] Synced {first_name} {last_name} ({email}) to CRM. Source: {lead_source}."
    try:
        result = sf.query(f"SELECT Id FROM Lead WHERE Email = '{email}' LIMIT 1")
        if result["totalSize"] > 0:
            lead_id = result["records"][0]["Id"]
            sf.Lead.update(lead_id, {
                "Title": title, "LeadSource": lead_source, "Description": description
            })
            return f"Updated existing Lead: {lead_id}"
        else:
            created = sf.Lead.create({
                "FirstName": first_name, "LastName": last_name,
                "Email": email, "Company": company, "Title": title,
                "LeadSource": lead_source, "Description": description,
            })
            return f"Created new Lead: {created['id']}"
    except Exception as e:
        return f"Error syncing lead {email}: {e}"
