# =============================================================================
# engine/keys.py — Step 2: Build 9 Keys + Charge Type
# 1-pass inline logic (ตาม M-Code "Added Combined Keys" let block)
# Source: M-Code Document 13, Load Charge Data Step 2
# =============================================================================

import pandas as pd
from config import CASE_CODES, FLAT_CODES, COMPOUND_CODES, AR_CO_MARKER


def _safe_str(val) -> str:
    """แปลง null/NaN เป็น empty string เหมือน M-Code"""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return str(val)


def _build_keys_row(row) -> dict:
    """
    สร้าง 9 Keys + Charge Type จาก 1 row
    Mirror M-Code 'Added Combined Keys' let block ทุก condition

    Keys:
        AP side (6): Pri-AP, Final key, AP Stop,
                     Mandate Key, Sup-Carrier, Sup-Truck
        AR side (3): AR-Pri, AR-Final key, AR Stop
    """
    # ── Raw fields ────────────────────────────────────────────────────────────
    orig_zone    = _safe_str(row.get("Shpm Lane Origin Zone/Hub"))
    dest_zone    = _safe_str(row.get("Shpm Lane Dest Zone/Hub"))
    carrier      = _safe_str(row.get("Carrier ID"))
    service      = _safe_str(row.get("Load Service ID"))
    item_type    = _safe_str(row.get("Shpm Item Type"))
    charge_code  = _safe_str(row.get("Load Charge Code"))
    cust_code    = _safe_str(row.get("Shpm Customer Code"))
    cust_service = _safe_str(row.get("Shpm Customer Service ID"))
    applied_code = _safe_str(row.get("Applied RateCode"))
    rate_raw     = _safe_str(row.get("Shpm Rate Code"))

    # ── PickupConfirmed Date → en-AU format (DD/MM/YYYY) ─────────────────────
    pickup = row.get("PickupConfirmed Date")
    if pickup is not None and not (isinstance(pickup, float) and pd.isna(pickup)):
        try:
            pickup_str = pd.Timestamp(pickup).strftime("%d/%m/%Y")
        except Exception:
            pickup_str = ""
    else:
        pickup_str = ""

    # ── DRAFTFLAT condition ───────────────────────────────────────────────────
    # M-Code: rateCode = Text.Replace(rateCodeRaw, "DFTCASE", "DFTFLAT")
    #         when chargeCode = "DRAFTFLAT"
    rate_code = (
        rate_raw.replace("DFTCASE", "DFTFLAT")
        if charge_code == "DRAFTFLAT"
        else rate_raw
    )

    # ── CO condition ──────────────────────────────────────────────────────────
    # M-Code: apItemType = "" when chargeCode = "CO"
    ap_item_type = "" if charge_code == "CO" else item_type

    # ── Charge Type ───────────────────────────────────────────────────────────
    if charge_code in CASE_CODES:
        charge_type = "CASE"
    elif charge_code in FLAT_CODES:
        charge_type = "FLAT"
    elif charge_code in COMPOUND_CODES:
        charge_type = "COMPOUND"
    else:
        charge_type = ""

    # ── AP Keys (6) ───────────────────────────────────────────────────────────
    pri_ap      = orig_zone + dest_zone + carrier + service + ap_item_type + charge_code + rate_code
    final_key   = pri_ap + pickup_str
    ap_stop     = (
        carrier + service + applied_code
        if applied_code != ""
        else carrier + service + rate_code
    )
    mandate_key = orig_zone + dest_zone + ap_item_type + charge_code + rate_code
    sup_carrier = orig_zone + dest_zone + ap_item_type + charge_code + rate_code + carrier
    sup_truck   = orig_zone + dest_zone + ap_item_type + charge_code + rate_code + service

    # ── AR Keys (3) ───────────────────────────────────────────────────────────
    # 3 cases: DRAFTFLAT / CO / normal
    if charge_code == "DRAFTFLAT":
        ar_pri = item_type + charge_code
    elif charge_code == "CO":
        ar_pri = cust_code + cust_service + AR_CO_MARKER + rate_raw
    else:
        ar_pri = cust_code + cust_service + charge_code + rate_raw

    ar_final_key = ar_pri + pickup_str
    ar_stop      = cust_code + cust_service + rate_raw

    return {
        "Pri-AP":       pri_ap,
        "Final key":    final_key,
        "AP Stop":      ap_stop,
        "Mandate Key":  mandate_key,
        "Sup-Carrier":  sup_carrier,
        "Sup-Truck":    sup_truck,
        "AR-Pri":       ar_pri,
        "AR-Final key": ar_final_key,
        "AR Stop":      ar_stop,
        "Charge Type":  charge_type,
    }


def build_keys(df: pd.DataFrame) -> pd.DataFrame:
    """
    Step 2: เพิ่ม 9 Keys + Charge Type เข้า DataFrame
    ใช้ apply row-wise (1 pass เหมือน M-Code inline let block)
    """
    keys_df = df.apply(_build_keys_row, axis=1, result_type="expand")
    return pd.concat([df, keys_df], axis=1)


def run(df: pd.DataFrame) -> pd.DataFrame:
    return build_keys(df)
