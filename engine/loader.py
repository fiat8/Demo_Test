# =============================================================================
# engine/loader.py — Tier 1 raw data loaders
# Reads: Load Confirm, AP Rate, AR Rate, Fuel Price (upload via web)
# Column names sourced directly from M-Code Document 13
# Date format: DD/MM/YYYY (Thai Excel standard)
# =============================================================================

import pandas as pd
from pathlib import Path


# ── Load Confirm columns (48 cols from M-Code) ───────────────────────────────
LOAD_CONFIRM_DTYPES = {
    "Company Code":               str,
    "Load ID":                    "Int64",
    "Shpm Num":                   str,
    "Shpm Leg ID":                "Int64",
    "Multi Drop":                 str,
    "Load Operational Status":    str,
    "Load Financial Status":      str,
    "Shipment Financial Status":  str,
    "Load Suspend Status":        str,
    "Load Tariff ID":             "Int64",
    "Load Service ID":            str,
    "Carrier ID":                 "Int64",
    "Load Equp Type":             str,
    "Shpm Item Type":             str,
    "Shpm Origin Loc":            "Int64",
    "Shpm Origin Name":           str,
    "Shpm Origin Province":       str,
    "Shpm Lane Origin Zone/Hub":  str,
    "Shpm Dest Loc":              str,
    "Shpm Dest Name":             str,
    "Shpm Dest Province":         str,
    "Shpm Lane Dest Zone/Hub":    str,
    "Shpm Customer Service ID":   str,
    "Shpm AP Service ID":         str,
    "Shipment Rating Valid":      str,
    "Shpm Customer Code":         "Int64",
    "Shpm Customer Name":         str,
    "Shpm Flex Qty 1":            float,
    "Shpm Flex Qty 2":            float,
    "Shipment AR Amount":         float,
    "Shpm Rate Code":             str,
    "Applied RateCode":           str,
    "Load Rating Valid":          str,
    "Load Charge Code":           str,
    "AP Load Amt":                float,
    "Load Rated Amount":          float,
    "Shpm Palletes":              "Int64",
    "Shpm Pieces":                "Int64",
    "Shpm Weight":                float,
    "Location Type":              str,
    "MT Equipment Charge Y/N":    str,
    "Used Pallet Qty":            str,   # cleaned → Int64 in clean.py
    "No. of drops":               "Int64",
}

LOAD_CONFIRM_DATE_COLS = [
    "Load Created Date",
    "Shipment Early Picked Date",
    "PickupConfirmed Date",
    "Completed Date",
    "POD Date",
]

LOAD_CONFIRM_REQUIRED_COLS = list(LOAD_CONFIRM_DTYPES.keys()) + LOAD_CONFIRM_DATE_COLS


def load_raw_data(file) -> pd.DataFrame:
    """
    Load Confirm Data — อ่านจาก uploaded file object หรือ Path
    รองรับ .xlsx .xls .xlsb .csv
    Date format: DD/MM/YYYY (Thai Excel standard)
    """
    df = _read_file(file)

    missing = [c for c in LOAD_CONFIRM_REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Load Confirm ขาด column: {missing}\n"
            f"Columns ที่พบ: {list(df.columns)}"
        )

    # Parse dates — dayfirst=True สำหรับ DD/MM/YYYY
    for col in LOAD_CONFIRM_DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")

    # แปลง numeric dtypes
    for col, dtype in LOAD_CONFIRM_DTYPES.items():
        if col in df.columns and dtype != str:
            try:
                df[col] = df[col].astype(dtype)
            except (ValueError, TypeError):
                pass  # clean.py จัดการต่อ

    return df


def load_fuel_price(file) -> pd.DataFrame:
    """
    Fuel Price Template — 2 columns: Date (DD/MM/YYYY), Fuel Price (integer)
    Upload ผ่านเว็บทุกงวด (Tier 3)

    Logic:
    - แต่ละแถว = 1 วัน (รายวัน)
    - From = Date[i]
    - To   = Date[i+1] - 1 day  (วันก่อนแถวถัดไป)
    - Row สุดท้าย: To = From + FUEL_EXTEND_DAYS
    """
    df = _read_file(file)

    required = ["Date", "Fuel Price"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"Fuel Price ต้องมี columns: {required}\n"
            f"Columns ที่พบ: {list(df.columns)}\n"
            f"หมายเหตุ: Date ใช้รูปแบบ DD/MM/YYYY"
        )

    # Parse DD/MM/YYYY — dayfirst=True
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    invalid_dates = df["Date"].isna().sum()
    if invalid_dates > 0:
        raise ValueError(
            f"Fuel Price: พบวันที่ที่แปลงไม่ได้ {invalid_dates} แถว\n"
            f"กรุณาใช้รูปแบบ DD/MM/YYYY (เช่น 16/05/2026)"
        )

    df["Fuel Price"] = pd.to_numeric(df["Fuel Price"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["Date", "Fuel Price"]).reset_index(drop=True)
    df = df.sort_values("Date").reset_index(drop=True)

    return df


# ── Internal helpers ──────────────────────────────────────────────────────────

def _read_file(file) -> pd.DataFrame:
    """
    อ่านไฟล์จาก path หรือ Streamlit UploadedFile
    รองรับ .xlsx .xls .xlsb .csv
    """
    if isinstance(file, (str, Path)):
        ext = Path(file).suffix.lower()
    else:
        ext = Path(getattr(file, "name", "")).suffix.lower()

    if ext == ".csv":
        return pd.read_csv(file, encoding="utf-8-sig")
    elif ext == ".xlsb":
        return pd.read_excel(file, engine="pyxlsb")
    elif ext in (".xls",):
        return pd.read_excel(file, engine="xlrd")
    else:
        # .xlsx หรือไม่มี ext — default openpyxl
        return pd.read_excel(file, engine="openpyxl")
