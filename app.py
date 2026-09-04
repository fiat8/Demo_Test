# =============================================================================
# app.py — Streamlit entrypoint
# BRF Billing Reconcile — AR/AP Reconciliation System
# =============================================================================

import streamlit as st
import pandas as pd

from ui.sidebar          import render_sidebar
from ui.kpi_summary      import render_kpi
from ui.preview_download import render_preview, render_download

from engine.loader       import load_raw_data, load_fuel_price
from engine.pipeline     import run as run_pipeline, get_kpi

from reference_tables.location_fuel import load_location1, load_location2
from reference_tables.ap_tables import (
    load_ap_prime, load_ap_child_master, load_ap_mandate,
    load_ap_carrier, load_ap_truck,
    load_apfinal_generic, load_apfinal_child, load_ap_stop,
)
from reference_tables.ar_tables import (
    load_ar_prime, load_arfinal_normal, load_ar_stop,
)

st.set_page_config(
    page_title="BRF Billing Reconcile",
    page_icon="📊",
    layout="wide",
)

st.title("📊 BRF Billing Reconcile")
st.caption("AR/AP Reconciliation — BRF Logistics Co., Ltd. (TMS: 1200 / 3L00)")

# ── Sidebar Upload ─────────────────────────────────────────────────────────
uploads = render_sidebar()

if not uploads["all_ready"]:
    st.info("👈 กรุณาอัปโหลดไฟล์ทั้ง 4 ไฟล์ทางซ้ายก่อน แล้วกด Run Reconcile")
    st.stop()

# ── Run Button ─────────────────────────────────────────────────────────────
if st.button("▶️ Run Reconcile", type="primary", use_container_width=True):
    try:
        with st.status("กำลังประมวลผล...", expanded=True) as status_box:

            # Phase 1: Load Tier 1
            st.write("📂 Phase 1: โหลด Raw Data...")
            load_df  = load_raw_data(uploads["load_confirm"])
            fuel_df  = load_fuel_price(uploads["fuel_price"])

            # Phase 2: Load Tier 2 (GitHub)
            st.write("🗂️ Phase 2: โหลด Reference Tables (GitHub)...")
            loc1 = load_location1()
            loc2 = load_location2()

            # Phase 3: Load AP/AR Master (from Tier 1 uploads)
            st.write("📋 Phase 3: โหลด AP/AR Master Tables...")
            ref_ap_prime        = load_ap_prime(uploads["ap_rate"])
            ref_ap_child_master = load_ap_child_master(uploads["ap_rate"])
            ref_ap_mandate      = load_ap_mandate(uploads["ap_rate"])
            ref_ap_carrier      = load_ap_carrier(uploads["ap_rate"])
            ref_ap_truck        = load_ap_truck(uploads["ap_rate"])
            ref_apfinal_generic = load_apfinal_generic(uploads["ap_rate"])
            ref_apfinal_child   = load_apfinal_child(uploads["ap_rate"])
            ref_ap_stop         = load_ap_stop(uploads["ap_rate"])
            ref_ar_prime        = load_ar_prime(uploads["ar_rate"])
            ref_arfinal_normal  = load_arfinal_normal(uploads["ar_rate"])
            ref_ar_stop         = load_ar_stop(uploads["ar_rate"])

            # Phase 4: Run Pipeline
            st.write("⚙️ Phase 4: รัน Reconcile Engine (Step 1→5)...")
            result_df = run_pipeline(
                load_confirm_df     = load_df,
                fuel_price_df       = fuel_df,
                ref_ap_prime        = ref_ap_prime,
                ref_ap_child_master = ref_ap_child_master,
                ref_ap_mandate      = ref_ap_mandate,
                ref_ap_carrier      = ref_ap_carrier,
                ref_ap_truck        = ref_ap_truck,
                ref_apfinal_generic = ref_apfinal_generic,
                ref_apfinal_child   = ref_apfinal_child,
                ref_ap_stop         = ref_ap_stop,
                ref_ar_prime        = ref_ar_prime,
                ref_arfinal_normal  = ref_arfinal_normal,
                ref_ar_stop         = ref_ar_stop,
                loc1_df             = loc1,
                loc2_df             = loc2,
            )

            # Phase 5: KPI + Output
            st.write("📊 Phase 5: สรุปผล...")
            kpi = get_kpi(result_df)
            st.session_state["result"] = result_df
            st.session_state["kpi"]    = kpi
            status_box.update(label="✅ เสร็จสิ้น!", state="complete")

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
        st.stop()

# ── Results ────────────────────────────────────────────────────────────────
if "result" in st.session_state:
    st.divider()
    render_kpi(st.session_state["kpi"])
    st.divider()
    render_preview(st.session_state["result"])
    st.divider()
    render_download(st.session_state["result"])
