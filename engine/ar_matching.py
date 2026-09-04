# =============================================================================
# engine/ar_matching.py — Step 4: AR join (Prime + Final + Stop)
# Source: M-Code Document 13, Steps 4 & 4.5
# =============================================================================

import pandas as pd


def merge_ar_prime(df: pd.DataFrame, ref: pd.DataFrame) -> pd.DataFrame:
    """
    Pre-Mapping_AR (Prime): AR-Pri == Pri-Columns → Status Prime(AR)
    """
    ref = ref.rename(columns={"Pri-Columns": "AR-Pri", "Status": "Status Prime(AR)"})
    return df.merge(ref[["AR-Pri", "Status Prime(AR)"]], on="AR-Pri", how="left")


def merge_arfinal_normal(df: pd.DataFrame, ref: pd.DataFrame) -> pd.DataFrame:
    """
    ARFinal-Mapping (NORMAL): AR-Final key == Final key
    Output: AR.EFFECTIVEDATE, AR.EXPIRATIONDATE, AR Rate Charge
    หมายเหตุ: column ใช้ UPPER CASE ต่างจากฝั่ง AP
    """
    ref = ref.rename(columns={
        "Final key":    "AR-Final key",
        "EFFECTIVEDATE":  "AR.EFFECTIVEDATE",
        "EXPIRATIONDATE": "AR.EXPIRATIONDATE",
        "RATE":           "AR Rate Charge",
    })
    return df.merge(
        ref[["AR-Final key", "AR.EFFECTIVEDATE", "AR.EXPIRATIONDATE", "AR Rate Charge"]],
        on="AR-Final key",
        how="left",
    )


def merge_ar_stop(df: pd.DataFrame, ref: pd.DataFrame) -> pd.DataFrame:
    """
    AR Master (STOP): AR Stop == Stop-Columns → AR Stop Charge
    """
    ref = ref.rename(columns={"Stop-Columns": "AR Stop", "RATE": "AR Stop Charge"})
    return df.merge(ref[["AR Stop", "AR Stop Charge"]], on="AR Stop", how="left")


def run(
    df: pd.DataFrame,
    ref_ar_prime: pd.DataFrame,
    ref_arfinal_normal: pd.DataFrame,
    ref_ar_stop: pd.DataFrame,
) -> pd.DataFrame:
    df = merge_ar_prime(df, ref_ar_prime)
    df = merge_arfinal_normal(df, ref_arfinal_normal)
    df = merge_ar_stop(df, ref_ar_stop)
    return df
