# =============================================================================
# config.py — Central configuration for Billing Reconcile
# All business constants sourced from M-Code (Document 13)
# =============================================================================

from pathlib import Path

# ── Project paths ─────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
DATA_DIR   = BASE_DIR / "data" / "tier2"
DOCS_DIR   = BASE_DIR / "docs"

# Tier 2 — static reference files (committed to GitHub)
TIER2_FILES = {
    "location1":         DATA_DIR / "location1.csv",
    "location2":         DATA_DIR / "location2.csv",
    "draft_parameters":  DATA_DIR / "draft_parameters.csv",
}

# ── Charge Code classification ────────────────────────────────────────────────
# Source: M-Code Step 2 — chargeType logic
CASE_CODES = {
    "CASEP", "CASE", "PS-CASE",
    "COD_CHARGE", "WEIGHT", "PALLET",
}

FLAT_CODES = {
    "CO", "FLAT", "FLATM", "DFTFREE", "FLATB",
    "SDFLAT", "FLATP", "AR_OVR", "FLATP_OVR", "AR_FLATP",
}

COMPOUND_CODES = {
    "DRAFTFLAT",   # chargeType = "COMPOUND" (แตกต่างจาก Project Background เดิมที่บันทึกเป็น FLAT)
}

# ── DRAFTFLAT condition ───────────────────────────────────────────────────────
# Source: M-Code Step 2 — rateCode substitution
DRAFTFLAT_REPLACE_FROM = "DFTCASE"
DRAFTFLAT_REPLACE_TO   = "DFTFLAT"

# ── CO condition ──────────────────────────────────────────────────────────────
# Source: M-Code Step 2 — apItemType = "" when chargeCode == "CO"
CO_CHARGE_CODE = "CO"

# ── PSC Constraint ────────────────────────────────────────────────────────────
# Source: M-Code Step 4.5 + confirmed spec
#
# FILL IN 1  (Origin Province)  →  location1.csv  →  values: {2, 5}
# FILL IN 2  (Dest Province)    →  location2.csv  →  values: {10, 18}
# FILL IN 3  (Pallet condition) →  psc.py logic   →  values: {0, 1}
#
# PSC = TRUE when (FILL IN1 + FILL IN2 + FILL IN3) ∈ PSC_TRUE_THRESHOLDS
# Confirmed combinations:
#   2 + 10 + 1 = 13  ✅
#   5 + 18 + 1 = 24  ✅
PSC_TRUE_THRESHOLDS = {13, 24}

# FILL IN 3 pallet condition (from M-Code Step 4.5)
PSC_PALLET_MIN      = 24          # Used Pallet Qty > 24
PSC_PALLET_MAX      = 41          # Used Pallet Qty < 41
PSC_EXCLUDE_SERVICE = "TL-26P"    # ยกเว้น service นี้
PSC_CHARGE_CODES    = {"FLATM", "FLATP"}  # เฉพาะ charge code เหล่านี้

# ── Fuel Surcharge formula ────────────────────────────────────────────────────
# Source: M-Code Fuel Price Parameters query
# Fuel Surcharge = (Fuel Price - BASE_FUEL_PRICE) × FUEL_RATE
FUEL_BASE_PRICE     = 27
FUEL_RATE           = 1.75 / 100   # 1.75%
FUEL_EXTEND_DAYS    = 150          # ขยาย To date ของ range สุดท้าย

# ── AP Rate Type priority ─────────────────────────────────────────────────────
# Source: M-Code Step 4.5 — Added AP Rate Type
# Child tariff takes priority over Generic
AP_RATE_CHILD   = "Child"
AP_RATE_GENERIC = "Generic"

# ── Status labels ─────────────────────────────────────────────────────────────
# Source: M-Code Step 5 — Status Transform
AP_STATUS = {
    "matched":            "Matched",
    "prime_unmatched":    "Unmatched tariff",
    "carrier_unmatched":  "ไม่พบ Carriers",
    "truck_unmatched":    "ไม่พบ Truck Type",
    "mandate_unmatched":  "Unmatched",
}

AR_STATUS = {
    "matched":   "Matched Tariff",
    "unmatched": "Unmatched tariff",
}

# ── AR CO key marker ──────────────────────────────────────────────────────────
# Source: M-Code Step 2 — arPri when chargeCode == "CO"
AR_CO_MARKER = "AR_CO"

# ── Preview row limit (UI) ────────────────────────────────────────────────────
PREVIEW_ROWS = 50

# ── Column sets ───────────────────────────────────────────────────────────────
# 9 keys ที่สร้างใน Step 2
KEY_COLUMNS = [
    "Pri-AP",
    "Final key",
    "AP Stop",
    "Mandate Key",
    "Sup-Carrier",
    "Sup-Truck",
    "AR-Pri",
    "AR-Final key",
    "AR Stop",
    "Charge Type",
]

# Working columns ที่ลบออกหลัง Step 5
WORKING_COLUMNS_TO_DROP = [
    "FILL IN 1", "FILL IN 2", "FILL IN3",
    "Clean Origin", "Clean Dest",
    "Child Tarriff Status",
]
