# =============================================================================
# ui/kpi_summary.py — KPI Cards
# =============================================================================

import streamlit as st


def render_kpi(kpi: dict):
    """
    แสดง KPI 4 cards: Total / Matched / Unmatched / PSC
    + Fallback Tier breakdown (ถ้ามี)
    """
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Total",     kpi.get("total", 0))
    c2.metric("✅ Matched",   kpi.get("matched", 0),
              delta=f"{kpi.get('match_pct', 0)}%")
    c3.metric("❌ Unmatched", kpi.get("unmatched", 0))
    c4.metric("🔔 PSC Flag",  kpi.get("psc", 0))

    # Fallback summary
    fallback = kpi.get("fallback", {})
    breakdown = fallback.get("tier_breakdown", {})
    if breakdown:
        st.subheader("Fallback Tier Summary")
        cols = st.columns(len(breakdown))
        for col, (tier, count) in zip(cols, breakdown.items()):
            col.metric(tier, count)
