# =============================================================================
# engine/fuzzy_match.py — Step 3.5: Province Fuzzy Matching
# Solution C: Pre-group distinct (~77 rows) → Fuzzy → Join back
# เร็วกว่า FuzzyJoin บน 10,000 rows โดยตรง ~130x
# Source: M-Code Document 13, Steps 3.5 + Fuzzy_Origin/Dest
# =============================================================================

import pandas as pd
from rapidfuzz import process, fuzz


# ── Score threshold (เทียบกับ M-Code IgnoreCase+IgnoreSpace, NumberOfMatches=1) ──
FUZZY_THRESHOLD = 80


def _fuzzy_match_province(
    query: str,
    choices: list[str],
    threshold: int = FUZZY_THRESHOLD,
) -> str | None:
    """
    Match 1 province string กับ list ของ reference provinces
    Return: matched reference province หรือ None ถ้า score < threshold
    M-Code options: IgnoreCase=true, IgnoreSpace=true, NumberOfMatches=1
    """
    if not query or not query.strip():
        return None

    query_clean = query.strip().lower().replace(" ", "")
    choices_clean = [c.strip().lower().replace(" ", "") for c in choices]

    result = process.extractOne(
        query_clean,
        choices_clean,
        scorer=fuzz.ratio,
        score_cutoff=threshold,
    )

    if result is None:
        return None

    # คืน choice ต้นฉบับ (ก่อน clean) ตาม index ที่ match
    matched_idx = choices_clean.index(result[0])
    return choices[matched_idx]


def build_fuzzy_map(
    distinct_provinces: list[str],
    ref_df: pd.DataFrame,
    province_col: str = "Province",
    fill_in_col: str = "FILL IN",
    threshold: int = FUZZY_THRESHOLD,
) -> pd.DataFrame:
    """
    Fuzzy match distinct province list กับ reference table
    Returns DataFrame: {query_province → matched_province → FILL IN value}

    Steps (ตาม M-Code Solution C):
    1. Distinct provinces (~77 rows) — ส่งมาจากภายนอก
    2. Fuzzy match แต่ละตัวกับ ref_df["Province"]
    3. คืน mapping table: Clean Province → FILL IN
    """
    ref_provinces = ref_df[province_col].tolist()
    ref_fill_map  = dict(zip(ref_df[province_col], ref_df[fill_in_col]))

    records = []
    for prov in distinct_provinces:
        matched = _fuzzy_match_province(prov, ref_provinces, threshold)
        fill_in = ref_fill_map.get(matched) if matched else None
        records.append({
            "Clean Province": prov,
            fill_in_col:      fill_in,
        })

    return pd.DataFrame(records)


def add_fill_in_columns(
    df: pd.DataFrame,
    loc1_df: pd.DataFrame,
    loc2_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Step 3.5: เพิ่ม FILL IN 1 + FILL IN 2 เข้า Main table

    Flow (Solution C):
    1. Distinct Clean Origin  → Fuzzy → map → join กลับ (FILL IN 1)
    2. Distinct Clean Dest    → Fuzzy → map → join กลับ (FILL IN 2)
    """
    df = df.copy()

    # ── Origin (FILL IN 1) ────────────────────────────────────────────────────
    distinct_origin = df["Clean Origin"].dropna().unique().tolist()
    origin_map = build_fuzzy_map(
        distinct_origin, loc1_df,
        province_col="Province", fill_in_col="FILL IN",
    )
    origin_map = origin_map.rename(columns={
        "Clean Province": "Clean Origin",
        "FILL IN":        "FILL IN 1",
    })
    df = df.merge(origin_map, on="Clean Origin", how="left")

    # ── Dest (FILL IN 2) ──────────────────────────────────────────────────────
    distinct_dest = df["Clean Dest"].dropna().unique().tolist()
    dest_map = build_fuzzy_map(
        distinct_dest, loc2_df,
        province_col="Province", fill_in_col="FILL IN",
    )
    dest_map = dest_map.rename(columns={
        "Clean Province": "Clean Dest",
        "FILL IN":        "FILL IN 2",
    })
    df = df.merge(dest_map, on="Clean Dest", how="left")

    return df


def run(
    df: pd.DataFrame,
    loc1_df: pd.DataFrame,
    loc2_df: pd.DataFrame,
) -> pd.DataFrame:
    return add_fill_in_columns(df, loc1_df, loc2_df)
