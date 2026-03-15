"""Outreach metrics page."""
import streamlit as st

from ai_sdr.ui.components.api_client import get

st.set_page_config(page_title="Outreach", page_icon="📧", layout="wide")
st.title("📧 Outreach")

leads = get("/api/v1/leads", {"limit": 200})

if "error" in (leads or {}):
    st.error(f"Could not fetch outreach data: {leads['error']}")
    leads = []

leads = leads or []
total = len(leads)
contacted = len([l for l in leads if l.get("status") in ["contacted", "meeting_booked"]])
meetings = len([l for l in leads if l.get("status") == "meeting_booked"])
response_rate = f"{int(contacted / total * 100)}%" if total > 0 else "—"
meeting_rate = f"{int(meetings / total * 100)}%" if total > 0 else "—"

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Leads", total)
with col2:
    st.metric("Contacted", contacted)
with col3:
    st.metric("Meetings Booked", meetings)
with col4:
    st.metric("Meeting Rate", meeting_rate)

st.markdown("---")

# Appointments
appts = get("/api/v1/appointments", {"limit": 50})
if isinstance(appts, list) and appts:
    st.subheader(f"Upcoming Appointments ({len(appts)})")
    import pandas as pd
    df = pd.DataFrame(appts)
    display_cols = [c for c in ["id", "status", "scheduled_at", "rep_email", "meeting_link", "lead_id"] if c in df.columns]
    st.dataframe(df[display_cols] if display_cols else df, use_container_width=True)
else:
    st.subheader("Appointments")
    st.info("No appointments yet.")
