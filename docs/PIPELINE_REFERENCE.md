# Pipeline Reference — Billing Reconcile
**Last updated:** Stage 0 | **Source:** M-Code Document 13

## PSC Constraint — Confirmed Spec
| Part | Source | Values |
|------|--------|--------|
| FILL IN 1 | location1.csv (Origin Province fuzzy match) | {2, 5} |
| FILL IN 2 | location2.csv (Dest Province fuzzy match) | {10, 18} |
| FILL IN 3 | Pallet condition (psc.py) | {0, 1} |

**PSC = TRUE when (FILL IN1 + FILL IN2 + FILL IN3) ∈ {13, 24}**

Valid combinations:
- 2 + 10 + 1 = 13 ✅
- 5 + 18 + 1 = 24 ✅

## Charge Type (Step 2)
| Group | Codes |
|-------|-------|
| CASE | CASEP, CASE, PS-CASE, COD_CHARGE, WEIGHT, PALLET |
| FLAT | CO, FLAT, FLATM, DFTFREE, FLATB, SDFLAT, FLATP, AR_OVR, FLATP_OVR, AR_FLATP |
| COMPOUND | DRAFTFLAT ← ⚠️ ต่างจาก doc เดิมที่บันทึกเป็น FLAT |

## Corrections from original Project Background
| Item | Original | Actual (from M-Code) |
|------|----------|----------------------|
| PSC threshold | {3, 7} | {13, 24} |
| DRAFTFLAT charge type | FLAT | COMPOUND |
| 4-Tier matching | cascade | parallel (4 status columns) |

## Data Tiers
| Tier | Files | Storage | Update frequency |
|------|-------|---------|-----------------|
| 1 | Load Confirm, AP Rate, AR Rate | Web upload | Every period |
| 2 | draft_parameters.csv, location1.csv, location2.csv | GitHub data/tier2/ | When business rules change |
| 3 | fuel_price.xlsx (2 cols: Date, Fuel Price) | Web upload | Every period |
