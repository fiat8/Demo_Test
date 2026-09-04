# =============================================================================
# engine/psc.py — Step 4.5: PSC Constraint
# FILL IN 3 + PSC Parameters sum + threshold {13, 24}
# Source: M-Code Document 13, PSC-Constraint + Added PSC Parameters
#
# Confirmed spec:
#   FILL IN 1 ∈ {2, 5}   (origin province)
#   FILL IN 2 ∈ {10, 18}  (dest province)
#   FILL IN 3 ∈ {0, 1}    (pallet condition below)
#   PSC = TRUE ↔ sum ∈ {13, 24}
#   Valid: 2+10+1=13 ✅  5+18+1=24 ✅
# =============================================================================

import pandas as pd
from config import (
    PSC_TRUE_THRESHOLDS,
    PSC_PALLET_MIN,
    PSC_PALLET_MAX,
    PSC_EXCLUDE_SERVICE,
    PSC_CHARGE_CODES,
)


def add_fill_in3(df: pd.DataFrame) -> pd.DataFrame:
    """
    FILL IN 3: 1 ถ้าผ่านทุกเงื่อนไข, 0 ถ้าไม่ผ่าน
    M-Code: PSC-Constraint
        Used Pallet Qty > 24 AND < 41
        AND Load Service ID <> "TL-26P"
        AND Load Charge Code IN {"FLATM", "FLATP"}
    """
    def _fill_in3(row):
        pallet  = row.get("Used Pallet Qty")
        service = row.get("Load Service ID", "")
        charge  = row.get("Load Charge Code", "")
        try:
            pallet_int = int(pallet)
        except (TypeError, ValueError):
            return 0
        if (
            pallet_int > PSC_PALLET_MIN
            and pallet_int < PSC_PALLET_MAX
            and service != PSC_EXCLUDE_SERVICE
            and charge in PSC_CHARGE_CODES
        ):
            return 1
        return 0

    df = df.copy()
    df["FILL IN3"] = df.apply(_fill_in3, axis=1).astype("Int64")
    return df


def add_psc_parameters(df: pd.DataFrame) -> pd.DataFrame:
    """
    PSC Parameters = FILL IN 1 + FILL IN 2 + FILL IN3
    null → 0 ก่อนบวก (M-Code: if [FILL IN 1] = null then 0)
    """
    df = df.copy()
    fi1 = pd.to_numeric(df.get("FILL IN 1", 0), errors="coerce").fillna(0)
    fi2 = pd.to_numeric(df.get("FILL IN 2", 0), errors="coerce").fillna(0)
    fi3 = pd.to_numeric(df.get("FILL IN3",  0), errors="coerce").fillna(0)
    df["PSC Parameters"] = (fi1 + fi2 + fi3).astype("Int64")
    return df


def add_psc_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    PSC = TRUE ↔ PSC Parameters ∈ {13, 24}
    M-Code: Transform PSC Parameters → logical
    """
    df = df.copy()
    df["PSC Parameters"] = df["PSC Parameters"].apply(
        lambda x: x in PSC_TRUE_THRESHOLDS
    )
    return df


def drop_working_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    ลบ FILL IN 1, 2, 3 + Clean Province + Child Tarriff Status
    M-Code: Removed Working Columns
    """
    drop = ["FILL IN 1", "FILL IN 2", "FILL IN3",
            "Clean Origin", "Clean Dest", "Child Tarriff Status"]
    return df.drop(columns=[c for c in drop if c in df.columns], errors="ignore")


def run(df: pd.DataFrame) -> pd.DataFrame:
    df = add_fill_in3(df)
    df = add_psc_parameters(df)
    df = add_psc_flag(df)
    df = drop_working_columns(df)
    return df
