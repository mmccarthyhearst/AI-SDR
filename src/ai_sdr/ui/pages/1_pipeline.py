"""Pipeline management page."""
import streamlit as st

from ai_sdr.ui.components.api_client import get, post

st.set_page_config(page_title="Pipeline", page_icon="🚀", layout="wide")
st.title("🚀 Pipeline Runs")

# Trigger new run
st.subheader("Trigger a Run")
with st.form("trigger_form"):
    icps = get("/api/v1/icp")
    icp_options = {}
    if isinstance(icps, list):
        icp_options = {icp["name"]: icp["id"] for icp in icps}
    selected_icp_name = st.selectbox("ICP", options=list(icp_options.keys()) or ["No ICPs found"])
    max_leads = st.slider("Max Leads", min_value=5, max_value=100, value=20, step=5)
    submitted = st.form_submit_button("▶ Run Pipeline", type="primary")

    if submitted and icp_options:
        icp_id = icp_options[selected_icp_name]
        result = post("/api/v1/pipeline/run", {"icp_id": icp_id, "max_leads": max_leads})
        if "error" in (result or {}):
            st.error(f"Failed to trigger run: {result['error']}")
        else:
            st.success(f"Pipeline run triggered! Run ID: {result.get('run_id', '?')}")

st.markdown("---")

# Run history
st.subheader("Run History")
runs = get("/api/v1/pipeline/runs", {"limit": 20})

if "error" in (runs or {}):
    st.error(f"Could not fetch runs: {runs['error']}")
elif not runs:
    st.info("No pipeline runs yet. Trigger one above!")
else:
    import pandas as pd
    df = pd.DataFrame(runs)
    display_cols = [c for c in ["id", "status", "leads_sourced", "leads_qualified", "leads_routed", "appointments_set", "started_at", "completed_at"] if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True)

    # Check if any are still running
    running = [r for r in runs if r.get("status") == "running"]
    if running:
        st.info(f"{len(running)} run(s) in progress...")
        if st.button("Refresh"):
            st.rerun()
