# =============================================================================
# engine/pipeline.py — Orchestrator: รัน Step 1→5 ตามลำดับ
# รับ raw DataFrames ทั้งหมด คืน final reconcile DataFrame
# =============================================================================

import pandas as pd
from engine import clean, keys, fuzzy_match, ap_matching, ar_matching, rates, psc, status, fallback
from reference_tables.location_fuel import build_fuel_parameters


def run(
    # ── Tier 1: Main data ──────────────────────────────────────────────────
    load_confirm_df:     pd.DataFrame,
    fuel_price_df:       pd.DataFrame,
    # ── AP reference tables ────────────────────────────────────────────────
    ref_ap_prime:        pd.DataFrame,
    ref_ap_child_master: pd.DataFrame,
    ref_ap_mandate:      pd.DataFrame,
    ref_ap_carrier:      pd.DataFrame,
    ref_ap_truck:        pd.DataFrame,
    ref_apfinal_generic: pd.DataFrame,
    ref_apfinal_child:   pd.DataFrame,
    ref_ap_stop:         pd.DataFrame,
    # ── AR reference tables ────────────────────────────────────────────────
    ref_ar_prime:        pd.DataFrame,
    ref_arfinal_normal:  pd.DataFrame,
    ref_ar_stop:         pd.DataFrame,
    # ── Tier 2: Location (fuzzy) ───────────────────────────────────────────
    loc1_df:             pd.DataFrame,
    loc2_df:             pd.DataFrame,
) -> pd.DataFrame:
    """
    Full pipeline: Step 1 → Step 5 + Fallback
    Returns final DataFrame (68+ columns)
    """

    # ── Step 1 + 1.5: Clean ────────────────────────────────────────────────
    df = clean.run(load_confirm_df)

    # ── Step 2: Build 9 Keys ───────────────────────────────────────────────
    df = keys.run(df)

    # ── Step 3: Build Fuel Parameters (จาก Tier 3 upload) ──────────────────
    fuel_params = build_fuel_parameters(fuel_price_df)

    # ── Step 3.5: Fuzzy Province → FILL IN 1 + 2 ──────────────────────────
    df = fuzzy_match.run(df, loc1_df, loc2_df)

    # ── Step 4: AP Matching (parallel 4 tiers) ─────────────────────────────
    df = ap_matching.run(
        df,
        ref_prime        = ref_ap_prime,
        ref_child_master = ref_ap_child_master,
        ref_mandate      = ref_ap_mandate,
        ref_carrier      = ref_ap_carrier,
        ref_truck        = ref_ap_truck,
        ref_apfinal_generic = ref_apfinal_generic,
        ref_apfinal_child   = ref_apfinal_child,
        ref_ap_stop      = ref_ap_stop,
    )

    # ── Step 4: AR Matching ────────────────────────────────────────────────
    df = ar_matching.run(df, ref_ar_prime, ref_arfinal_normal, ref_ar_stop)

    # ── Step 4.5: AP Rate Type + Rate Charge + Fuel Price ──────────────────
    df = rates.run(df, fuel_params)

    # ── Step 4.5: PSC Constraint + Clean working cols ──────────────────────
    df = psc.run(df)

    # ── Step 5: Status Transform ───────────────────────────────────────────
    df = status.run(df)

    # ── Fallback Logic (🆕 Feature) ────────────────────────────────────────
    df = fallback.run(df)

    return df


def get_kpi(df: pd.DataFrame) -> dict:
    """
    KPI Summary สำหรับ UI
    """
    total    = len(df)
    matched  = (df.get("Prime Status", pd.Series()) == "Matched").sum()
    psc_true = df.get("PSC Parameters", pd.Series(dtype=bool)).sum() if "PSC Parameters" in df.columns else 0

    return {
        "total":      int(total),
        "matched":    int(matched),
        "unmatched":  int(total - matched),
        "psc":        int(psc_true),
        "match_pct":  round(matched / total * 100, 1) if total > 0 else 0,
        "fallback":   fallback.get_fallback_summary(df),
    }
