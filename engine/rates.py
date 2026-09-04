# =============================================================================
# engine/rates.py — Step 4.5: AP Rate Type + Fuel Price join
# Source: M-Code Document 13, Added AP Rate Type + Added SelectedPriceData
# =============================================================================

import pandas as pd
from config import AP_RATE_CHILD, AP_RATE_GENERIC


def add_ap_rate_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    AP Rate Type: Child > Generic > ""
    M-Code: if Child Tarriff Status = "Active" → "Child"
            elif Prime Status = "Active"         → "Generic"
            else ""
    """
    def _rate_type(row):
        if row.get("Child Tarriff Status") == "Active":
            return AP_RATE_CHILD
        elif row.get("Prime Status") == "Active":
            return AP_RATE_GENERIC
        return ""

    df = df.copy()
    df["AP Rate Type"] = df.apply(_rate_type, axis=1)
    return df


def add_ap_rate_charge(df: pd.DataFrame) -> pd.DataFrame:
    """
    SelectedPriceData: เลือก rate จาก Child หรือ Generic ตาม AP Rate Type
    Output columns: AP.Effective Date, AP.Expiration Date, AP Rate Charge
    M-Code: Added SelectedPriceData + Expanded Selected Columns
    """
    def _select(row):
        is_child = row.get("AP Rate Type") == AP_RATE_CHILD
        if is_child:
            return {
                "AP.Effective Date":  row.get("_chd_Effective Date"),
                "AP.Expiration Date": row.get("_chd_Expiration Date"),
                "AP Rate Charge":     row.get("_chd_Rate"),
            }
        return {
            "AP.Effective Date":  row.get("_gen_Effective Date"),
            "AP.Expiration Date": row.get("_gen_Expiration Date"),
            "AP Rate Charge":     row.get("_gen_Rate"),
        }

    df = df.copy()
    rate_cols = df.apply(_select, axis=1, result_type="expand")
    df[["AP.Effective Date", "AP.Expiration Date", "AP Rate Charge"]] = rate_cols

    # ลบ prefix columns หลังเลือกแล้ว
    drop_cols = [c for c in df.columns if c.startswith("_chd_") or c.startswith("_gen_")]
    df = df.drop(columns=drop_cols, errors="ignore")
    return df


def merge_fuel_price(df: pd.DataFrame, fuel_params: pd.DataFrame) -> pd.DataFrame:
    """
    Join Fuel Price Parameters กับ PickupConfirmed Date ∈ [From, To]
    ใช้ merge_asof (nearest) แทน NestedJoin ของ M-Code
    Output columns: Fuel Price, FSC Rate, Range.From, Range.To, Fuel.Latest
    """
    df = df.copy()
    fuel = fuel_params.rename(columns={
        "Fuel Surcharge": "FSC Rate",
        "From":           "Range.From",
        "To":             "Range.To",
        "Latest":         "Fuel.Latest",
    }).copy()

    # เตรียม sort
    df_sorted   = df.sort_values("PickupConfirmed Date").copy()
    fuel_sorted = fuel.sort_values("Range.From").copy()

    # merge_asof: จับ Range.From ≤ PickupConfirmed Date
    merged = pd.merge_asof(
        df_sorted,
        fuel_sorted[["Range.From", "Range.To", "Fuel Price", "FSC Rate", "Fuel.Latest"]],
        left_on="PickupConfirmed Date",
        right_on="Range.From",
        direction="backward",
    )

    # กรอง To: ถ้า PickupConfirmed Date > Range.To → ไม่ match
    mask = merged["PickupConfirmed Date"] > merged["Range.To"]
    merged.loc[mask, ["Fuel Price", "FSC Rate", "Range.From", "Range.To", "Fuel.Latest"]] = None

    # คืน index เดิม
    merged.index = df_sorted.index
    return merged.reindex(df.index)


def run(df: pd.DataFrame, fuel_params: pd.DataFrame) -> pd.DataFrame:
    df = add_ap_rate_type(df)
    df = add_ap_rate_charge(df)
    df = merge_fuel_price(df, fuel_params)
    return df
