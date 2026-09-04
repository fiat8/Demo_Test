# =============================================================================
# reference_tables/ar_tables.py — AR side master table loaders
# 3 tables + DRAFT Parameters append
# Column names from M-Code Document 13
# =============================================================================

import pandas as pd
from engine.loader import _read_file
from reference_tables.location_fuel import load_draft_parameters


def load_ar_prime(file) -> pd.DataFrame:
    """
    Pre-Mapping_AR (Prime) — Key: Pri-Columns → Output: Status (Status Prime AR)
    Join key ใน Main table: AR-Pri == Pri-Columns
    """
    df = _read_file(file)
    return _select(df, keep=["Pri-Columns", "Status"], source="AR Prime")


def load_arfinal_normal(file) -> pd.DataFrame:
    """
    ARFinal-Mapping (NORMAL) — Key: Final key
    Output: EFFECTIVEDATE, EXPIRATIONDATE, RATE → AR Rate Charge
    Note: ชื่อ column ใช้ UPPER CASE ต่างจากฝั่ง AP ที่ใช้ Title Case
    """
    df = _read_file(file)
    return _select(
        df,
        keep=["Final key", "EFFECTIVEDATE", "EXPIRATIONDATE", "RATE"],
        source="ARFinal Normal",
    )


def load_ar_stop(file) -> pd.DataFrame:
    """
    AR Master (STOP) — Key: Stop-Columns → Output: RATE → AR Stop Charge
    Join key ใน Main table: AR Stop == Stop-Columns
    """
    df = _read_file(file)
    return _select(df, keep=["Stop-Columns", "RATE"], source="AR Stop")


def load_ar_master_all(file) -> pd.DataFrame:
    """
    AR Master (ALL) + append DRAFT PARAMETERS
    ตาม M-Code: AR Master (ALL) = source AR data + append draft_parameters rows
    ใช้เป็น base สำหรับสร้าง ARFinal-Mapping (NORMAL) และ Pre-Mapping_AR
    """
    df = _read_file(file)

    # Append DRAFT PARAMETERS (Tier 2 CSV)
    draft = load_draft_parameters()
    if not draft.empty:
        # Align columns — draft มี: Shpm Item Type, Load Charge Code, EFFECTIVEDATE, EXPIRATIONDATE, RATE
        # ถ้า AR Master มีคอลัมน์เพิ่มเติม ให้ fill NaN
        df = pd.concat([df, draft], ignore_index=True)

    return df.copy()


# ── Internal ──────────────────────────────────────────────────────────────────

def _select(df: pd.DataFrame, keep: list, source: str) -> pd.DataFrame:
    missing = [c for c in keep if c not in df.columns]
    if missing:
        raise ValueError(f"{source}: ไม่พบ columns {missing} (มี: {list(df.columns)})")
    return df[keep].copy()
