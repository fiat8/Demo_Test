# =============================================================================
# reference_tables/ap_tables.py — AP side master table loaders
# 8 tables: Pre-Mapping_AP x5, APFinal-Mapping x2, AP Master x3
# Column names from M-Code Document 13
# =============================================================================

import pandas as pd
from pathlib import Path
from engine.loader import _read_file


def load_ap_prime(file) -> pd.DataFrame:
    """
    Pre-Mapping_AP (Prime) — Key: Pri-Columns → Output: Tarriff Status
    Join key ใน Main table: Pri-AP == Pri-Columns
    """
    df = _read_file(file)
    return _select(df, keep=["Pri-Columns", "Tarriff Status"], source="AP Prime")


def load_ap_child_master(file) -> pd.DataFrame:
    """
    Pre-Mapping AP (Child) — Key: Pri-Columns → Output: Status (Child Tarriff Status)
    ใช้ตัดสินว่าจะใช้ Child หรือ Generic rate
    Join key ใน Main table: Pri-AP == Pri-Columns
    """
    df = _read_file(file)
    return _select(df, keep=["Pri-Columns", "Status"], source="AP Child Master")


def load_ap_mandate(file) -> pd.DataFrame:
    """
    Pre-Mapping_AP (Mandate) — Key: Mandate-key → Output: Status (Mandatory-Status)
    Fallback Tier 2
    """
    df = _read_file(file)
    return _select(df, keep=["Mandate-key", "Status"], source="AP Mandate")


def load_ap_carrier(file) -> pd.DataFrame:
    """
    Pre-Mapping_AP (Carrier) — Key: Sub-key2 → Output: Status (Carrier-Status)
    Fallback Tier 3
    Join key ใน Main table: Sup-Carrier == Sub-key2
    """
    df = _read_file(file)
    return _select(df, keep=["Sub-key2", "Status"], source="AP Carrier")


def load_ap_truck(file) -> pd.DataFrame:
    """
    Pre-Mapping_AP (Truck) — Key: Sub-key1 → Output: Status (Truck Status)
    Fallback Tier 4
    Join key ใน Main table: Sup-Truck == Sub-key1
    """
    df = _read_file(file)
    return _select(df, keep=["Sub-key1", "Status"], source="AP Truck")


def load_apfinal_generic(file) -> pd.DataFrame:
    """
    APFinal-Mapping (Generic) — Key: Final key
    Output: Effective Date, Expiration Date, Rate → AP Rate Charge
    """
    df = _read_file(file)
    return _select(
        df,
        keep=["Final key", "Effective Date", "Expiration Date", "Rate"],
        source="APFinal Generic",
    )


def load_apfinal_child(file) -> pd.DataFrame:
    """
    APFinal-Mapping (Child) — Key: Final-key (สังเกต dash ต่างจาก Generic)
    Output: Effective Date, Expiration Date, Rate → AP Rate Charge (Child)
    """
    df = _read_file(file)
    return _select(
        df,
        keep=["Final-key", "Effective Date", "Expiration Date", "Rate"],
        source="APFinal Child",
    )


def load_ap_stop(file) -> pd.DataFrame:
    """
    AP Master (STOP) — Key: Stop-Columns
    Output: Rate → AP Stop Charge
    Join key ใน Main table: AP Stop == Stop-Columns
    """
    df = _read_file(file)
    return _select(df, keep=["Stop-Columns", "Rate"], source="AP Stop")


# ── Internal ──────────────────────────────────────────────────────────────────

def _select(df: pd.DataFrame, keep: list, source: str) -> pd.DataFrame:
    missing = [c for c in keep if c not in df.columns]
    if missing:
        raise ValueError(f"{source}: ไม่พบ columns {missing} (มี: {list(df.columns)})")
    return df[keep].copy()
