# =============================================================================
# tests/test_psc.py — Unit tests for engine/psc.py
# =============================================================================

import sys
sys.path.insert(0, ".")

import pandas as pd
import pytest
from engine.psc import add_fill_in3, add_psc_parameters, add_psc_flag


def _make_row(**kwargs):
    defaults = {
        "Used Pallet Qty": 30,
        "Load Service ID": "FTL",
        "Load Charge Code": "FLATM",
    }
    defaults.update(kwargs)
    return pd.DataFrame([defaults])


def test_fill_in3_passes():
    df = add_fill_in3(_make_row(Used_Pallet_Qty=30))
    # สร้างแบบ dict ตรงๆ
    df2 = pd.DataFrame([{
        "Used Pallet Qty": 30,
        "Load Service ID": "FTL",
        "Load Charge Code": "FLATM",
    }])
    df2 = add_fill_in3(df2)
    assert df2["FILL IN3"].iloc[0] == 1


def test_fill_in3_fails_service():
    df = pd.DataFrame([{
        "Used Pallet Qty": 30,
        "Load Service ID": "TL-26P",   # excluded
        "Load Charge Code": "FLATM",
    }])
    df = add_fill_in3(df)
    assert df["FILL IN3"].iloc[0] == 0


def test_fill_in3_fails_pallet_too_low():
    df = pd.DataFrame([{
        "Used Pallet Qty": 24,          # not > 24
        "Load Service ID": "FTL",
        "Load Charge Code": "FLATM",
    }])
    df = add_fill_in3(df)
    assert df["FILL IN3"].iloc[0] == 0


def test_psc_true_2_10_1():
    df = pd.DataFrame([{"FILL IN 1": 2, "FILL IN 2": 10, "FILL IN3": 1}])
    df = add_psc_parameters(df)
    df = add_psc_flag(df)
    assert df["PSC Parameters"].iloc[0] == True


def test_psc_true_5_18_1():
    df = pd.DataFrame([{"FILL IN 1": 5, "FILL IN 2": 18, "FILL IN3": 1}])
    df = add_psc_parameters(df)
    df = add_psc_flag(df)
    assert df["PSC Parameters"].iloc[0] == True


def test_psc_false_other():
    df = pd.DataFrame([{"FILL IN 1": 2, "FILL IN 2": 10, "FILL IN3": 0}])
    df = add_psc_parameters(df)
    df = add_psc_flag(df)
    assert df["PSC Parameters"].iloc[0] == False
