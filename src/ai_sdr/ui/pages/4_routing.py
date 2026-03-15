"""Routing rules management page."""
import streamlit as st

from ai_sdr.ui.components.api_client import get, post

st.set_page_config(page_title="Routing Rules", page_icon="🔀", layout="wide")
st.title("🔀 Routing Rules")

rules = get("/api/v1/routing-rules", {"active_only": False})

if "error" in (rules or {}):
    st.error(f"Could not fetch routing rules: {rules['error']}")
elif not rules:
    st.info("No routing rules configured.")
else:
    import pandas as pd
    df = pd.DataFrame(rules)
    display_cols = [c for c in ["name", "priority", "is_active", "action"] if c in df.columns]
    st.dataframe(df[display_cols] if display_cols else df, use_container_width=True)

    st.markdown("---")
    st.subheader("Rule Details")
    for rule in sorted(rules, key=lambda r: r.get("priority", 999)):
        status = "✅" if rule.get("is_active") else "⏸"
        with st.expander(f"{status} #{rule.get('priority', '?')} — {rule['name']}"):
            conditions = rule.get("conditions") or []
            if conditions:
                st.write("**Conditions (ALL must match):**")
                for c in conditions:
                    st.code(f"{c.get('field')} {c.get('op')} {c.get('value')}")
            else:
                st.write("**Catch-all rule** (matches all leads)")
            action = rule.get("action") or {}
            st.write(f"**Action:** Route to `{action.get('team', '?')}` team"
                     + (f", assign to `{action.get('rep', '')}`" if action.get("rep") else ""))

st.markdown("---")
st.subheader("Add Routing Rule")
with st.form("create_rule"):
    name = st.text_input("Rule Name", placeholder="Franchise Brands 50+ Locations")
    priority = st.number_input("Priority (lower = checked first)", min_value=1, value=10)
    team = st.text_input("Route to Team", placeholder="enterprise")
    st.caption("Leave conditions empty for a catch-all rule")
    if st.form_submit_button("Create Rule"):
        if name and team:
            result = post("/api/v1/routing-rules", {
                "name": name,
                "priority": priority,
                "conditions": [],
                "action": {"team": team},
            })
            if "error" in (result or {}):
                st.error(f"Failed: {result['error']}")
            else:
                st.success(f"Rule created: {name}")
                st.rerun()
        else:
            st.warning("Name and team are required")
