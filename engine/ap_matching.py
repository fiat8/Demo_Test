# =============================================================================
# engine/ap_matching.py — Step 4: AP parallel join (4 Tiers)
# พฤติกรรม: parallel status (ไม่ cascade) ตาม M-Code จริง
# ทุก Tier join พร้อมกัน → ได้ 4 status columns
# Source: M-Code Document 13, Steps 4 & 4.5
# =============================================================================

import pandas as pd


def merge_ap_prime(df: pd.DataFrame, ref: pd.DataFrame) -> pd.DataFrame:
    """
    Tier 1: Pri-AP == Pri-Columns → Prime Status (Tarriff Status)
    """
    ref = ref.rename(columns={"Pri-Columns": "Pri-AP", "Tarriff Status": "Prime Status"})
    return df.merge(ref[["Pri-AP", "Prime Status"]], on="Pri-AP", how="left")


def merge_ap_child_master(df: pd.DataFrame, ref: pd.DataFrame) -> pd.DataFrame:
    """
    Pre-Mapping AP (Child): Pri-AP == Pri-Columns → Child Tarriff Status
    ใช้ตัดสิน AP Rate Type (Child vs Generic) ใน rates.py
    """
    ref = ref.rename(columns={"Pri-Columns": "Pri-AP", "Status": "Child Tarriff Status"})
    return df.merge(ref[["Pri-AP", "Child Tarriff Status"]], on="Pri-AP", how="left")


def merge_ap_mandate(df: pd.DataFrame, ref: pd.DataFrame) -> pd.DataFrame:
    """
    Tier 2: Mandate Key == Mandate-key → Mandatory-Status
    """
    ref = ref.rename(columns={"Mandate-key": "Mandate Key", "Status": "Mandatory-Status"})
    return df.merge(ref[["Mandate Key", "Mandatory-Status"]], on="Mandate Key", how="left")


def merge_ap_carrier(df: pd.DataFrame, ref: pd.DataFrame) -> pd.DataFrame:
    """
    Tier 3: Sup-Carrier == Sub-key2 → Carrier-Status
    """
    ref = ref.rename(columns={"Sub-key2": "Sup-Carrier", "Status": "Carrier-Status"})
    return df.merge(ref[["Sup-Carrier", "Carrier-Status"]], on="Sup-Carrier", how="left")


def merge_ap_truck(df: pd.DataFrame, ref: pd.DataFrame) -> pd.DataFrame:
    """
    Tier 4: Sup-Truck == Sub-key1 → Truck Status
    """
    ref = ref.rename(columns={"Sub-key1": "Sup-Truck", "Status": "Truck Status"})
    return df.merge(ref[["Sup-Truck", "Truck Status"]], on="Sup-Truck", how="left")


def merge_apfinal(
    df: pd.DataFrame,
    ref_generic: pd.DataFrame,
    ref_child: pd.DataFrame,
) -> pd.DataFrame:
    """
    APFinal-Mapping: Final key → AP Rate (Generic + Child nested tables)
    เก็บเป็น nested DataFrame per row แล้ว rates.py เลือก Child หรือ Generic
    M-Code: Final Merge[Prime Generic] + Final Merge[Prime Child]
    """
    # Generic: Final key (same column name)
    ref_generic = ref_generic.add_prefix("_gen_").rename(
        columns={"_gen_Final key": "Final key"}
    )
    df = df.merge(ref_generic, on="Final key", how="left")

    # Child: Final-key (dash) → align to Final key
    ref_child = ref_child.rename(columns={"Final-key": "Final key"}).add_prefix("_chd_").rename(
        columns={"_chd_Final key": "Final key"}
    )
    df = df.merge(ref_child, on="Final key", how="left")

    return df


def merge_ap_stop(df: pd.DataFrame, ref: pd.DataFrame) -> pd.DataFrame:
    """
    AP Master (STOP): AP Stop == Stop-Columns → AP Stop Charge
    """
    ref = ref.rename(columns={"Stop-Columns": "AP Stop", "Rate": "AP Stop Charge"})
    return df.merge(ref[["AP Stop", "AP Stop Charge"]], on="AP Stop", how="left")


def run(
    df: pd.DataFrame,
    ref_prime: pd.DataFrame,
    ref_child_master: pd.DataFrame,
    ref_mandate: pd.DataFrame,
    ref_carrier: pd.DataFrame,
    ref_truck: pd.DataFrame,
    ref_apfinal_generic: pd.DataFrame,
    ref_apfinal_child: pd.DataFrame,
    ref_ap_stop: pd.DataFrame,
) -> pd.DataFrame:
    """
    รัน AP matching ทั้งหมด (parallel, ไม่ cascade)
    """
    df = merge_ap_prime(df, ref_prime)
    df = merge_ap_child_master(df, ref_child_master)
    df = merge_ap_mandate(df, ref_mandate)
    df = merge_ap_carrier(df, ref_carrier)
    df = merge_ap_truck(df, ref_truck)
    df = merge_apfinal(df, ref_apfinal_generic, ref_apfinal_child)
    df = merge_ap_stop(df, ref_ap_stop)
    return df
