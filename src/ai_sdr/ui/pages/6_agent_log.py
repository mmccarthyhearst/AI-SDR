"""Agent run log page."""
import streamlit as st

from ai_sdr.ui.components.api_client import get

st.set_page_config(page_title="Agent Log", page_icon="🤖", layout="wide")
st.title("🤖 Agent Run Log")

runs = get("/api/v1/pipeline/runs", {"limit": 50})

if "error" in (runs or {}):
    st.error(f"Could not fetch agent runs: {runs['error']}")
elif not runs:
    st.info("No pipeline runs yet.")
else:
    # Summary stats
    total_runs = len(runs)
    completed = len([r for r in runs if r.get("status") == "completed"])
    failed = len([r for r in runs if r.get("status") == "failed"])
    running = len([r for r in runs if r.get("status") == "running"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Runs", total_runs)
    with col2:
        st.metric("Completed", completed)
    with col3:
        st.metric("Failed", failed)
    with col4:
        st.metric("Running", running)

    st.markdown("---")

    # Run timeline
    for run in runs:
        status_icon = {"completed": "✅", "failed": "❌", "running": "⏳", "pending": "⏸"}.get(run.get("status", ""), "?")
        run_id_short = str(run.get("id", "?"))[:8]

        with st.expander(f"{status_icon} Run {run_id_short} — {run.get('status', 'unknown')} — {(run.get('started_at') or '')[:16]}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Run ID:** `{run.get('id')}`")
                st.write(f"**Status:** {run.get('status')}")
                st.write(f"**Started:** {run.get('started_at', '—')}")
                st.write(f"**Completed:** {run.get('completed_at', '—')}")
            with col2:
                st.write(f"**Leads sourced:** {run.get('leads_sourced', '—')}")
                st.write(f"**Leads qualified:** {run.get('leads_qualified', '—')}")
                st.write(f"**Leads routed:** {run.get('leads_routed', '—')}")
                st.write(f"**Meetings booked:** {run.get('appointments_set', '—')}")

            if run.get("error_message"):
                st.error(f"Error: {run['error_message']}")

    if running > 0:
        if st.button("Refresh"):
            st.rerun()
