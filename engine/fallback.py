# =============================================================================
# engine/fallback.py — 🆕 Fallback Logic (Feature ใหม่ ไม่มีใน M-Code เดิม)
# ชั้นเสริมที่วิ่งหลัง status.py เสร็จ
#
# หน้าที่: วิเคราะห์ 4 status columns แล้วสรุปว่าแต่ละแถว
#          "น่าจะ match ได้ที่ Tier ไหน" และ "เหตุผลที่ Unmatched"
#
# Output columns ใหม่ (ไม่กระทบ 4 status เดิม):
#   Suggested Tier  — Tier ที่แนะนำ (1-4) หรือ "None"
#   Fallback Reason — คำอธิบายสาเหตุที่ Unmatched ในแต่ละ Tier
# =============================================================================

import pandas as pd

# Label ที่ถือว่า "Matched" ในแต่ละ Tier
_MATCHED = "Matched"


def _suggest_tier(row) -> str:
    """
    ดู 4 status แล้วแนะนำ Tier ที่ควรใช้
    ลำดับ: Prime → Mandatory → Carrier → Truck
    """
    if row.get("Prime Status")      == _MATCHED:
        return "Tier 1 (Prime)"
    if row.get("Mandatory-Status")  == _MATCHED:
        return "Tier 2 (Mandate)"
    if row.get("Carrier-Status")    == _MATCHED:
        return "Tier 3 (Carrier)"
    if row.get("Truck Status")      == _MATCHED:
        return "Tier 4 (Truck)"
    return "None"


def _fallback_reason(row) -> str:
    """
    สรุปเหตุผล Unmatched แบบอ่านได้
    """
    reasons = []
    if row.get("Prime Status")     != _MATCHED:
        reasons.append("ไม่พบ Pri-AP")
    if row.get("Mandatory-Status") != _MATCHED:
        reasons.append("ไม่พบ Mandate")
    if row.get("Carrier-Status")   != _MATCHED:
        reasons.append("ไม่พบ Carrier")
    if row.get("Truck Status")     != _MATCHED:
        reasons.append("ไม่พบ Truck")

    if not reasons:
        return "Matched ทุก Tier"
    if row.get("Prime Status") == _MATCHED:
        return "Matched ที่ Prime"
    return " | ".join(reasons)


def add_fallback_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    เพิ่ม Suggested Tier + Fallback Reason
    รันหลัง status.py เท่านั้น (ต้องการ label จาก Step 5 แล้ว)
    """
    df = df.copy()
    df["Suggested Tier"]  = df.apply(_suggest_tier,    axis=1)
    df["Fallback Reason"] = df.apply(_fallback_reason, axis=1)
    return df


def get_fallback_summary(df: pd.DataFrame) -> dict:
    """
    Summary สำหรับ KPI UI:
    - breakdown ตาม Suggested Tier
    - รายการ Tier ที่พบบ่อยที่สุด
    """
    if "Suggested Tier" not in df.columns:
        return {}

    counts = df["Suggested Tier"].value_counts().to_dict()
    return {
        "tier_breakdown": counts,
        "top_tier":       max(counts, key=counts.get) if counts else "N/A",
    }


def run(df: pd.DataFrame) -> pd.DataFrame:
    return add_fallback_columns(df)
