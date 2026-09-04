# =============================================================================
# tests/test_keys.py — Unit tests for engine/keys.py
# ตรวจสอบว่า 9 Keys ตรงกับ M-Code จริง
# =============================================================================

import sys
sys.path.insert(0, ".")

import pandas as pd
import pytest
from engine.keys import _build_keys_row


BASE_ROW = {
    "Shpm Lane Origin Zone/Hub": "BKK",
    "Shpm Lane Dest Zone/Hub":   "CNX",
    "Carrier ID":                "100",
    "Load Service ID":           "FTL",
    "Shpm Item Type":            "CASE",
    "Load Charge Code":          "FLAT",
    "Shpm Customer Code":        "9999",
    "Shpm Customer Service ID":  "STD",
    "Applied RateCode":          None,
    "Shpm Rate Code":            "RC001",
    "PickupConfirmed Date":      pd.Timestamp("2026-05-16"),
}


def test_normal_pri_ap():
    row = {**BASE_ROW}
    keys = _build_keys_row(row)
    expected = "BKK" + "CNX" + "100" + "FTL" + "CASE" + "FLAT" + "RC001"
    assert keys["Pri-AP"] == expected


def test_final_key_appends_date():
    row = {**BASE_ROW}
    keys = _build_keys_row(row)
    assert keys["Final key"].endswith("16/05/2026")


def test_draftflat_replaces_dftcase():
    row = {**BASE_ROW, "Load Charge Code": "DRAFTFLAT", "Shpm Rate Code": "DFTCASE-001"}
    keys = _build_keys_row(row)
    assert "DFTFLAT" in keys["Pri-AP"]
    assert "DFTCASE" not in keys["Pri-AP"]


def test_co_clears_item_type_in_ap():
    row = {**BASE_ROW, "Load Charge Code": "CO"}
    keys = _build_keys_row(row)
    assert "CASE" not in keys["Pri-AP"]


def test_co_ar_pri_uses_ar_co_marker():
    row = {**BASE_ROW, "Load Charge Code": "CO"}
    keys = _build_keys_row(row)
    assert "AR_CO" in keys["AR-Pri"]


def test_draftflat_ar_pri():
    row = {**BASE_ROW, "Load Charge Code": "DRAFTFLAT"}
    keys = _build_keys_row(row)
    assert keys["AR-Pri"] == "CASEDRAFTFLAT"


def test_charge_type_case():
    row = {**BASE_ROW, "Load Charge Code": "CASE"}
    keys = _build_keys_row(row)
    assert keys["Charge Type"] == "CASE"


def test_charge_type_flat():
    row = {**BASE_ROW, "Load Charge Code": "FLATM"}
    keys = _build_keys_row(row)
    assert keys["Charge Type"] == "FLAT"


def test_charge_type_compound():
    row = {**BASE_ROW, "Load Charge Code": "DRAFTFLAT"}
    keys = _build_keys_row(row)
    assert keys["Charge Type"] == "COMPOUND"


def test_ap_stop_uses_applied_rate_when_present():
    row = {**BASE_ROW, "Applied RateCode": "ARC999"}
    keys = _build_keys_row(row)
    assert "ARC999" in keys["AP Stop"]


def test_ap_stop_uses_rate_code_when_no_applied():
    row = {**BASE_ROW, "Applied RateCode": None}
    keys = _build_keys_row(row)
    assert "RC001" in keys["AP Stop"]
