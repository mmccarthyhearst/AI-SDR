"""Leads management page."""
import streamlit as st

from ai_sdr.ui.components.api_client import get

st.set_page_config(page_title="Leads", page_icon="👥", layout="wide")
st.title("👥 Leads")

# Filters
with st.expander("Filters", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status_filter = st.selectbox("Status", ["All", "sourced", "qualified", "routed", "contacted", "meeting_booked", "disqualified"])
    with col2:
        tier_filter = st.selectbox("Tier", ["All", "hot", "warm", "cold"])
    with col3:
        min_score = st.slider("Min Score", 0, 100, 0)
    with col4:
        franchise_brand = st.text_input("Franchise Brand (filter)")

params: dict = {"limit": 100}
if status_filter != "All":
    params["status"] = status_filter
if tier_filter != "All":
    params["tier"] = tier_filter
if min_score > 0:
    params["min_score"] = min_score

leads = get("/api/v1/leads", params)

if "error" in (leads or {}):
    st.error(f"Could not fetch leads: {leads['error']}")
elif not leads:
    st.info("No leads match the current filters.")
else:
    # Optional franchise brand filter (client-side since API may not support it)
    if franchise_brand:
        leads = [l for l in leads if franchise_brand.lower() in (l.get("franchise_brand") or "").lower()]

    import pandas as pd
    df = pd.DataFrame(leads)
    display_cols = [c for c in ["id", "status", "tier", "score", "franchise_brand", "assigned_team", "assigned_rep", "created_at"] if c in df.columns]

    st.write(f"Showing {len(df)} leads")
    st.dataframe(df[display_cols] if display_cols else df, use_container_width=True)

    # Franchise network view
    if "franchise_brand" in df.columns:
        st.markdown("---")
        st.subheader("Leads by Franchise Brand")
        brand_counts = df["franchise_brand"].value_counts().dropna()
        if not brand_counts.empty:
            st.bar_chart(brand_counts)
