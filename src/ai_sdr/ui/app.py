"""AI SDR Dashboard — entry point with KPI summary."""
import streamlit as st

from ai_sdr.ui.components.api_client import get

st.set_page_config(
    page_title="AI SDR Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("AI SDR Dashboard")
st.caption("Franchise-focused autonomous lead generation & qualification")
st.markdown("---")

# KPI metrics from latest pipeline run
runs = get("/api/v1/pipeline/runs", {"limit": 1})
if isinstance(runs, list) and runs:
    latest = runs[0]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Leads Sourced", latest.get("leads_sourced", "—"))
    with col2:
        st.metric("Qualified", latest.get("leads_qualified", "—"))
    with col3:
        st.metric("Meetings Booked", latest.get("appointments_set", "—"))
    with col4:
        sourced = latest.get("leads_sourced", 0)
        meetings = latest.get("appointments_set", 0)
        rate = f"{int(meetings / sourced * 100)}%" if sourced and sourced > 0 else "—"
        st.metric("Conversion Rate", rate)
else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Leads Sourced", "—", help="Total leads found this period")
    with col2:
        st.metric("Qualified", "—", help="Leads that passed ICP scoring")
    with col3:
        st.metric("Meetings Booked", "—", help="Appointments scheduled")
    with col4:
        st.metric("Conversion Rate", "—", help="Sourced → Meeting rate")

st.markdown("---")
st.subheader("System Status")

# Health check
health = get("/health")
if isinstance(health, dict) and health.get("status") == "ok":
    st.success("✅ API is online")
elif "error" in (health or {}):
    st.error(f"❌ API error: {health['error']}")
else:
    st.warning("⚠️ API status unknown")

st.info("Use the sidebar to navigate: Pipeline → Leads → ICP → Routing Rules → Outreach → Agent Log")
