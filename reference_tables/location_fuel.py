# =============================================================================
# reference_tables/location_fuel.py — Tier 2 & Tier 3 reference loaders
# Tier 2: location1.csv, location2.csv  (GitHub repo, static)
# Tier 3: Fuel Price Parameters         (upload via web, per period)
#
# Fuel Price spec (confirmed):
#   - Format   : DD/MM/YYYY (Thai Excel standard)
#   - Frequency: รายวัน (1 แถว = 1 วัน)
#   - Range    : From = Date[i], To = Date[i+1] - 1 day
#   - Last row : To = From + FUEL_EXTEND_DAYS
#   - No match : ใช้ range ครอบคลุม (From→To) ไม่มี fallback ล่าสุด
# =============================================================================

import pandas as pd
from pathlib import Path
from config import TIER2_FILES, FUEL_BASE_PRICE, FUEL_RATE, FUEL_EXTEND_DAYS


def _read_csv_thai(path) -> pd.DataFrame:
    """
    อ่าน CSV รองรับ encoding ภาษาไทยทุกแบบ
    ลำดับ: utf-8-sig → utf-8 → tis-620 (cp874) → latin-1
    """
    for enc in ["utf-8-sig", "utf-8", "tis-620", "cp874", "latin-1"]:
        try:
            return pd.read_csv(path, encoding=enc)
        except (UnicodeDecodeError, LookupError):
            continue
    raise ValueError(f"ไม่สามารถอ่านไฟล์ {path} ได้ — กรุณาบันทึกไฟล์ใหม่เป็น UTF-8")


def load_location1() -> pd.DataFrame:
    """
    location1.csv — Origin Province → FILL IN 1
    Valid values: {2, 5}
    """
    path = TIER2_FILES["location1"]
    df = _read_csv_thai(path)
    _validate_location(df, "location1.csv", expected_values={2, 5})
    df["FILL IN"] = pd.to_numeric(df["FILL IN"], errors="coerce").astype("Int64")
    return df[["Province", "FILL IN"]].copy()


def load_location2() -> pd.DataFrame:
    """
    location2.csv — Dest Province → FILL IN 2
    Valid values: {10, 18}
    """
    path = TIER2_FILES["location2"]
    df = _read_csv_thai(path)
    _validate_location(df, "location2.csv", expected_values={10, 18})
    df["FILL IN"] = pd.to_numeric(df["FILL IN"], errors="coerce").astype("Int64")
    return df[["Province", "FILL IN"]].copy()


def load_draft_parameters() -> pd.DataFrame:
    """
    draft_parameters.csv — Tier 2 static
    Columns: Shpm Item Type, Load Charge Code, EFFECTIVEDATE, EXPIRATIONDATE, RATE
    """
    path = TIER2_FILES["draft_parameters"]
    df = _read_csv_thai(path)

    required = ["Shpm Item Type", "Load Charge Code",
                "EFFECTIVEDATE", "EXPIRATIONDATE", "RATE"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"draft_parameters.csv ขาด columns: {missing}")

    # Date: dayfirst=True รองรับทั้ง DD/MM/YYYY และ YYYY-MM-DD
    df["EFFECTIVEDATE"]  = pd.to_datetime(df["EFFECTIVEDATE"],  dayfirst=True, errors="coerce")
    df["EXPIRATIONDATE"] = pd.to_datetime(df["EXPIRATIONDATE"], dayfirst=True, errors="coerce")
    df["RATE"]           = pd.to_numeric(df["RATE"], errors="coerce")
    return df.copy()


def build_fuel_parameters(fuel_df: pd.DataFrame) -> pd.DataFrame:
    """
    แปลง Fuel Price (Date DD/MM/YYYY, Fuel Price int) → Fuel Parameters table

    Logic (รายวัน, confirmed spec):
        From  = Date[i]
        To    = Date[i+1] - 1 day   ← วันก่อนแถวถัดไป
        To    = From + FUEL_EXTEND_DAYS  ← row สุดท้าย
        Fuel Surcharge = (Fuel Price - BASE) × RATE%
        Latest = Fuel Price ของ row สุดท้าย (broadcast ทุก row)

    Output columns:
        Date | Fuel Price | Fuel Surcharge | From | To | Latest

    Join กับ Main table:
        PickupConfirmed Date ∈ [From, To]  →  merge_asof ใน rates.py
    """
    df = fuel_df.copy()
    df = df.sort_values("Date").reset_index(drop=True)

    # Fuel Surcharge
    df["Fuel Surcharge"] = (
        (df["Fuel Price"] - FUEL_BASE_PRICE) * FUEL_RATE
    ).round(6)

    # Date range
    df["From"] = df["Date"]
    df["To"]   = df["Date"].shift(-1) - pd.Timedelta(days=1)

    # Row สุดท้าย
    last = df.index[-1]
    df.loc[last, "To"] = df.loc[last, "From"] + pd.Timedelta(days=FUEL_EXTEND_DAYS)

    # Latest = Fuel Price วันสุดท้ายที่มีในตาราง
    df["Latest"] = int(df["Fuel Price"].iloc[-1])

    return df[["Date", "Fuel Price", "Fuel Surcharge", "From", "To", "Latest"]].copy()


# ── Validation ────────────────────────────────────────────────────────────────

def _validate_location(df: pd.DataFrame, filename: str, expected_values: set):
    required = ["Province", "FILL IN"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{filename} ขาด columns: {missing}")

    if df.empty:
        raise ValueError(
            f"{filename} ยังไม่มีข้อมูล — กรุณากรอกจังหวัดและ FILL IN "
            f"{expected_values} แล้ว commit ขึ้น GitHub"
        )

    actual = set(pd.to_numeric(df["FILL IN"], errors="coerce").dropna().unique())
    unexpected = actual - expected_values
    if unexpected:
        raise ValueError(
            f"{filename}: พบค่า FILL IN ที่ไม่ถูกต้อง {unexpected} "
            f"(ค่าที่ถูกต้อง: {expected_values})"
        )
