# =============================================================================
# ui/preview_download.py — Preview + Download
# =============================================================================

import streamlit as st
import pandas as pd
from io import BytesIO
from config import PREVIEW_ROWS


def render_preview(df: pd.DataFrame):
    """Preview 50 rows"""
    st.subheader(f"Preview (แสดง {PREVIEW_ROWS} แถวแรก จาก {len(df):,} แถว)")
    st.dataframe(df.head(PREVIEW_ROWS), use_container_width=True)


def render_download(df: pd.DataFrame):
    """Download: ทั้งหมด + Unmatched เท่านั้น"""
    st.subheader("⬇️ Download")

    col1, col2 = st.columns(2)

    # ทั้งหมด
    with col1:
        buf_all = _to_excel(df)
        st.download_button(
            "📥 ดาวน์โหลดทั้งหมด (.xlsx)",
            data=buf_all,
            file_name="Reconcile_Output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # Unmatched เท่านั้น
    with col2:
        unmatched = df[df.get("Prime Status", pd.Series()) != "Matched"] \
            if "Prime Status" in df.columns else df
        buf_un = _to_excel(unmatched)
        st.download_button(
            f"⚠️ ดาวน์โหลด Unmatched ({len(unmatched):,} แถว)",
            data=buf_un,
            file_name="Reconcile_Unmatched.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def _to_excel(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Result")
    return buf.getvalue()
