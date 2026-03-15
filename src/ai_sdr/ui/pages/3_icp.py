"""ICP management page."""
import streamlit as st

from ai_sdr.ui.components.api_client import get, post

st.set_page_config(page_title="ICP", page_icon="🎯", layout="wide")
st.title("🎯 Ideal Customer Profiles")

icps = get("/api/v1/icp")

if "error" in (icps or {}):
    st.error(f"Could not fetch ICPs: {icps['error']}")
elif not icps:
    st.info("No ICPs configured yet.")
else:
    for icp in icps:
        with st.expander(f"{'✅' if icp.get('is_active') else '⏸'} {icp['name']}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Industries:** {', '.join(icp.get('target_industries') or [])}")
                st.write(f"**Min employees:** {icp.get('min_employee_count', '—')}")
                st.write(f"**Min franchise count:** {icp.get('min_franchise_count', '—')}")
                st.write(f"**Franchisor target:** {'Yes' if icp.get('is_franchisor_target') else 'No'}")
                st.write(f"**Franchisee target:** {'Yes' if icp.get('is_franchisee_target') else 'No'}")
            with col2:
                st.write(f"**Target titles:** {', '.join(icp.get('target_titles') or [])}")
                st.write(f"**Active:** {'Yes' if icp.get('is_active') else 'No'}")
                st.write(f"**Created:** {icp.get('created_at', '—')[:10]}")

st.markdown("---")
st.subheader("Create New ICP")
with st.form("create_icp"):
    name = st.text_input("Name", placeholder="Franchise Brands (50+ Locations)")
    industries = st.text_input("Target Industries (comma-separated)", placeholder="Food & Beverage, Fitness")
    titles = st.text_input("Target Titles (comma-separated)", placeholder="VP of Operations, Director of Franchise Development")
    min_franchise_count = st.number_input("Min Franchise Count", min_value=0, value=50)
    is_franchisor_target = st.checkbox("Target Franchisors", value=True)
    is_franchisee_target = st.checkbox("Target Franchisees", value=False)

    if st.form_submit_button("Create ICP"):
        if name:
            result = post("/api/v1/icp", {
                "name": name,
                "target_industries": [i.strip() for i in industries.split(",") if i.strip()],
                "target_titles": [t.strip() for t in titles.split(",") if t.strip()],
                "min_franchise_count": min_franchise_count if min_franchise_count > 0 else None,
                "is_franchisor_target": is_franchisor_target,
                "is_franchisee_target": is_franchisee_target,
            })
            if "error" in (result or {}):
                st.error(f"Failed: {result['error']}")
            else:
                st.success(f"ICP created: {result.get('name')}")
                st.rerun()
        else:
            st.warning("Name is required")
