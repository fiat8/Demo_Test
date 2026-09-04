# =============================================================================
# engine/status.py — Step 5: Status Transform (ท้ายสุด)
# AP: 4 status columns → text labels
# AR: Status Prime(AR) → text label
# Source: M-Code Document 13, AP Status + AR Status Transform
# =============================================================================

import pandas as pd
from config import AP_STATUS, AR_STATUS


# AP status columns ที่ต้อง transform ทั้งหมด
AP_STATUS_COLS = ["Prime Status", "Mandatory-Status", "Carrier-Status", "Truck Status"]


def transform_ap_status(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 5 AP: Active → 1 → Int64 → text → label
    M-Code sequence:
      "Active" → "1"
      null     → "0"
      → Int64 → text
      Prime   : "0" → "Unmatched tariff", "1" → "Matched"
      Mandate : "0" → "Unmatched",        "1" → "Matched"
      Carrier : "0" → "ไม่พบ Carriers",   "1" → "Matched"
      Truck   : "0" → "ไม่พบ Truck Type", "1" → "Matched"
    """
    df = df.copy()
    cols = [c for c in AP_STATUS_COLS if c in df.columns]

    # Active → 1, null → 0, แปลงเป็น int แล้วเป็น string
    for col in cols:
        df[col] = df[col].replace("Active", "1")
        df[col] = df[col].fillna("0")
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int).astype(str)

    # Label แต่ละคอลัมน์
    label_map = {
        "Prime Status":     {"0": AP_STATUS["prime_unmatched"],   "1": AP_STATUS["matched"]},
        "Mandatory-Status": {"0": AP_STATUS["mandate_unmatched"], "1": AP_STATUS["matched"]},
        "Carrier-Status":   {"0": AP_STATUS["carrier_unmatched"], "1": AP_STATUS["matched"]},
        "Truck Status":     {"0": AP_STATUS["truck_unmatched"],   "1": AP_STATUS["matched"]},
    }

    for col, mapping in label_map.items():
        if col in df.columns:
            df[col] = df[col].map(mapping).fillna(df[col])

    return df


def transform_ar_status(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 5 AR: Status Prime(AR)
    M-Code: "Active" → "Matched Tariff", null → "Unmatched tariff"
    """
    df = df.copy()
    col = "Status Prime(AR)"
    if col not in df.columns:
        return df

    df[col] = df[col].apply(
        lambda x: AR_STATUS["matched"]
        if x == "Active"
        else (AR_STATUS["unmatched"] if pd.isna(x) else x)
    )
    return df


def run(df: pd.DataFrame) -> pd.DataFrame:
    df = transform_ap_status(df)
    df = transform_ar_status(df)
    return df
