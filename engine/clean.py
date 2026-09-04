# =============================================================================
# engine/clean.py — Step 1 + Step 1.5
# Step 1  : Clean Used Pallet Qty (text → Int64, take first 2 chars)
# Step 1.5: Clean Province (ตัด จ./จังหวัด/จ prefix)
# Source  : M-Code Document 13, Load Charge Data Steps 1 & 1.5
# =============================================================================

import pandas as pd


def clean_used_pallet_qty(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 1: Used Pallet Qty
    M-Code: Text.Start(Text.Trim(Text.From(_)), 2) → try Int64 otherwise 0
    """
    def _parse(val):
        try:
            txt = str(val).strip()[:2]
            return int(txt)
        except (ValueError, TypeError):
            return 0

    df = df.copy()
    df["Used Pallet Qty"] = df["Used Pallet Qty"].apply(_parse).astype("Int64")
    return df


def clean_province(prov) -> str:
    """
    Step 1.5: ตัด prefix จังหวัด/จ./จ ออก
    M-Code: fnCleanProvince
    """
    if prov is None or (isinstance(prov, float)):
        return ""
    txt = str(prov).strip()
    for prefix in ["จังหวัด", "จ.", "จ "]:
        txt = txt.replace(prefix, "")
    return txt.strip()


def add_clean_provinces(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 1.5: เพิ่ม Clean Origin + Clean Dest columns
    M-Code: Added Clean Province
    """
    df = df.copy()
    df["Clean Origin"] = df["Shpm Origin Province"].apply(clean_province)
    df["Clean Dest"]   = df["Shpm Dest Province"].apply(clean_province)
    return df


def run(df: pd.DataFrame) -> pd.DataFrame:
    """
    รัน Step 1 + Step 1.5 ต่อเนื่อง
    """
    df = clean_used_pallet_qty(df)
    df = add_clean_provinces(df)
    return df
