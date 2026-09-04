# =============================================================================
# ui/sidebar.py — Upload section (Tier 1 + Tier 3)
# =============================================================================

import streamlit as st


def render_sidebar() -> dict:
    """
    Sidebar: Upload Tier 1 (3 ไฟล์) + Tier 3 (Fuel Price)
    Returns dict ของ uploaded file objects (None ถ้ายังไม่ได้ upload)
    """
    st.sidebar.header("📂 อัปโหลดข้อมูล")

    st.sidebar.subheader("Tier 1 — ข้อมูลหลัก")
    load_confirm = st.sidebar.file_uploader(
        "Load Confirm Data *",
        type=["xlsx", "xls", "xlsb", "csv"],
        key="load_confirm",
    )
    ap_rate = st.sidebar.file_uploader(
        "AP Rate Master *",
        type=["xlsx", "xls", "xlsb"],
        key="ap_rate",
    )
    ar_rate = st.sidebar.file_uploader(
        "AR Rate Master *",
        type=["xlsx", "xls", "xlsb"],
        key="ar_rate",
    )

    st.sidebar.subheader("Tier 3 — Fuel Price")
    st.sidebar.caption("รูปแบบ: Date (DD/MM/YYYY) | Fuel Price (บาท/ลิตร)")
    fuel_price = st.sidebar.file_uploader(
        "Fuel Price (.xlsx)",
        type=["xlsx", "xls", "csv"],
        key="fuel_price",
    )

    st.sidebar.divider()
    st.sidebar.caption(
        "📌 Tier 2 (Location + DRAFT Parameters) โหลดจาก GitHub อัตโนมัติ"
    )

    all_ready = all([load_confirm, ap_rate, ar_rate, fuel_price])

    return {
        "load_confirm": load_confirm,
        "ap_rate":      ap_rate,
        "ar_rate":      ar_rate,
        "fuel_price":   fuel_price,
        "all_ready":    all_ready,
    }
