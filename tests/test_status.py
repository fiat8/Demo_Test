# =============================================================================
# tests/test_status.py — Unit tests for engine/status.py
# =============================================================================

import sys
sys.path.insert(0, ".")

import pandas as pd
from engine.status import transform_ap_status, transform_ar_status


def test_ap_active_becomes_matched():
    df = pd.DataFrame([{
        "Prime Status": "Active", "Mandatory-Status": "Active",
        "Carrier-Status": "Active", "Truck Status": "Active",
    }])
    df = transform_ap_status(df)
    assert df["Prime Status"].iloc[0] == "Matched"


def test_ap_null_prime_becomes_unmatched_tariff():
    df = pd.DataFrame([{
        "Prime Status": None, "Mandatory-Status": None,
        "Carrier-Status": None, "Truck Status": None,
    }])
    df = transform_ap_status(df)
    assert df["Prime Status"].iloc[0] == "Unmatched tariff"
    assert df["Carrier-Status"].iloc[0] == "ไม่พบ Carriers"
    assert df["Truck Status"].iloc[0] == "ไม่พบ Truck Type"


def test_ar_active_becomes_matched_tariff():
    df = pd.DataFrame([{"Status Prime(AR)": "Active"}])
    df = transform_ar_status(df)
    assert df["Status Prime(AR)"].iloc[0] == "Matched Tariff"


def test_ar_null_becomes_unmatched_tariff():
    df = pd.DataFrame([{"Status Prime(AR)": None}])
    df = transform_ar_status(df)
    assert df["Status Prime(AR)"].iloc[0] == "Unmatched tariff"
