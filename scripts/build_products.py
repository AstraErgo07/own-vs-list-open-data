#!/usr/bin/env python3
"""Build the product-level table from the official Olist raw files.

Olist is the 3P (marketplace sellers) catalogue. 1P per-unit costs are
applied later, from published retailer benchmarks, in the decision engine.
UCI Online Retail II is no longer included: its wholesale gift-retailer
prices are not a credible 1P cost basis. The UCI helpers in this file
are unused by main() and are kept only so a local raw copy can still be
inspected if needed.

Outputs, small enough for Streamlit Cloud:
  data/processed/products.csv.gz
  data/processed/build_summary.json

Raw files stay in data/raw/ and are gitignored.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from own_vs_list.categories import (  # noqa: E402
    UCI_UNMAPPED,
    map_olist_category,
    map_uci_description,
)
from own_vs_list.fees import (  # noqa: E402
    AMAZON_CATEGORY_NAME,
    amazon_category_for,
    assumed_size_for_category,
    fba_fulfilment_gbp,
    referral_fee,
)

RAW_UCI = ROOT / "data" / "raw" / "uci"
RAW_OLIST = ROOT / "data" / "raw" / "olist"
OUT = ROOT / "data" / "processed"

# ECB euro reference rates, Brazilian real and pound sterling against the euro.
# BRL per GBP = (BRL per EUR) / (GBP per EUR). Daily observations, 4 Sep 2016
# to 17 Oct 2018 (the Olist order window), arithmetic mean.
# Source: ECB Statistical Data Warehouse, series EXR.D.BRL.EUR.SP00.A and
# EXR.D.GBP.EUR.SP00.A, downloaded 12 November 2026.
# 1 GBP = 4.399308 BRL, so GBP = BRL / BRL_PER_GBP.
BRL_PER_GBP = 4.399308
FX_WINDOW = "4 September 2016 to 17 October 2018"
FX_SOURCE = (
    "European Central Bank Statistical Data Warehouse, "
    "EXR.D.BRL.EUR.SP00.A and EXR.D.GBP.EUR.SP00.A, daily, "
    "downloaded 12 November 2026"
)
FX_LABEL = (
    f"Published (ECB daily rates, mean {BRL_PER_GBP:.4f} BRL per GBP, "
    f"{FX_WINDOW})"
)

UCI_SOURCE_LABEL = "UK online gift retailer, December 2009 to December 2011"
OLIST_SOURCE_LABEL = "Brazilian marketplace sellers, September 2016 to October 2018"

# Minimum history for a product-level coefficient of variation.
MIN_SALES_WEEKS_UCI = 12
MIN_ORDERS_OLIST = 5
MIN_WEEKS_FOR_PRODUCT_CV = 12
MIN_POSITIVE_WEEKS_FOR_PRODUCT_CV = 8

# Wholesale flag on the UCI side: share of units from invoice lines of 50 or more.
WHOLESALE_QTY = 50

# Non-product UCI stock codes (postage, fees, adjustments). Real products are
# a 5-digit code with an optional one- or two-letter suffix (e.g. 85123A, 15056BL).
UCI_PRODUCT_CODE = re.compile(r"^\d{5}[A-Z]{0,2}$")


def _mode_text(s: pd.Series) -> str:
    s = s.dropna().astype(str).str.upper().str.strip()
    if s.empty:
        return ""
    return s.mode().iloc[0]


def _weekly_cv(week_units: pd.Series, first, last) -> tuple[float, float, int, int, str]:
    """Mean weekly units and CV, including zero weeks from first to last sale.

    Returns mean, cv, n_weeks_span, n_positive, basis.
    """
    if week_units.empty or pd.isna(first) or pd.isna(last):
        return np.nan, np.nan, 0, 0, "insufficient"
    weeks = pd.period_range(first, last, freq="W")
    if len(weeks) == 0:
        return np.nan, np.nan, 0, 0, "insufficient"
    series = week_units.reindex(weeks, fill_value=0.0).astype(float)
    mean = float(series.mean())
    n_pos = int((series > 0).sum())
    n = int(len(series))
    if mean <= 0 or n < 2:
        return mean, np.nan, n, n_pos, "insufficient"
    cv = float(series.std(ddof=1) / mean)
    basis = "observed_product"
    if n < MIN_WEEKS_FOR_PRODUCT_CV or n_pos < MIN_POSITIVE_WEEKS_FOR_PRODUCT_CV:
        basis = "observed_product_short"  # caller may replace with category CV
    return mean, cv, n, n_pos, basis


def _load_uci() -> pd.DataFrame:
    gz = RAW_UCI / "online_retail_II.csv.gz"
    xlsx = RAW_UCI / "online_retail_II.xlsx"
    if gz.exists():
        df = pd.read_csv(gz, parse_dates=["InvoiceDate"], low_memory=False)
    elif xlsx.exists():
        frames = [pd.read_excel(xlsx, sheet_name=s) for s in
                  pd.ExcelFile(xlsx).sheet_names]
        df = pd.concat(frames, ignore_index=True)
    else:
        raise FileNotFoundError(
            f"UCI data not found in {RAW_UCI}. Run scripts/download_data.py first."
        )
    # The official workbook uses 'Price'; some mirrors use 'UnitPrice'.
    if "Price" not in df.columns and "UnitPrice" in df.columns:
        df = df.rename(columns={"UnitPrice": "Price"})
    return df


def build_uci(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df["Invoice"] = df["Invoice"].astype(str)
    df["StockCode"] = df["StockCode"].astype(str).str.strip().str.upper()
    df["is_cancel"] = df["Invoice"].str.upper().str.startswith("C")
    df["is_product"] = df["StockCode"].str.fullmatch(UCI_PRODUCT_CODE)
    goods = df[(df["is_product"]) & (~df["is_cancel"]) & (df["Price"] > 0) & (df["Quantity"] > 0)].copy()
    cancels = df[(df["is_product"]) & (df["is_cancel"])].copy()
    goods["line_value"] = goods["Price"] * goods["Quantity"]
    goods["week"] = goods["InvoiceDate"].dt.to_period("W")
    goods["wholesale_units"] = np.where(goods["Quantity"] >= WHOLESALE_QTY, goods["Quantity"], 0)

    # Product-level sales
    grp = goods.groupby("StockCode", sort=False)
    weekly = goods.groupby(["StockCode", "week"], sort=False)["Quantity"].sum()
    cancels = cancels.copy()
    cancels["cancel_value"] = cancels["Price"] * cancels["Quantity"].abs()
    cancel_val_by_sku = cancels.groupby("StockCode")["cancel_value"].sum()

    rows = []
    for sku, g in grp:
        desc = _mode_text(g["Description"])
        cat, shared = map_uci_description(desc)
        first = g["InvoiceDate"].min()
        last = g["InvoiceDate"].max()
        wu_series = weekly.loc[sku] if sku in weekly.index.get_level_values(0) else pd.Series(dtype=float)
        if isinstance(wu_series, pd.DataFrame):
            wu_series = wu_series.iloc[:, 0]
        # wu_series is indexed by week when we used groupby StockCode,week; after loc[sku] index is week
        mean_w, cv, n_weeks, n_pos, cv_basis = _weekly_cv(wu_series, first.to_period("W"), last.to_period("W"))
        if n_pos < MIN_SALES_WEEKS_UCI:
            continue
        units = float(g["Quantity"].sum())
        gmv = float(g["line_value"].sum())
        med_price = float(g["Price"].median())
        if med_price <= 0 or not np.isfinite(med_price):
            continue
        # Return proxy: cancelled invoice value / gross sales value, capped at 1.
        cancel_val = float(cancel_val_by_sku.get(sku, 0.0))
        ret = min(cancel_val / gmv, 1.0) if gmv > 0 else np.nan
        wholesale_share = float(g["wholesale_units"].sum()) / units if units else 0.0
        rows.append({
            "sku": f"UCI-{sku}",
            "title": desc.title() if desc else f"Product {sku}",
            "category": cat,
            "category_shared": bool(shared and cat != UCI_UNMAPPED),
            "category_mapping": "keyword on product description" if cat != UCI_UNMAPPED else "unmapped giftware",
            "source": "uci_retail",
            "source_label": UCI_SOURCE_LABEL,
            "listing_origin": "1P observed (retailer own stock)",
            "price": med_price,
            "price_original": med_price,
            "currency_original": "GBP",
            "weekly_units": mean_w,
            "weekly_units_cv": cv,
            "cv_basis": cv_basis,
            "n_orders": int(g["Invoice"].nunique()),
            "n_weeks_span": n_weeks,
            "n_positive_weeks": n_pos,
            "first_date": first.date().isoformat(),
            "last_date": last.date().isoformat(),
            "return_rate": ret if np.isfinite(ret) else np.nan,
            "return_rate_basis": "observed_cancellations" if np.isfinite(ret) else "assumption",
            "wholesale_unit_share": wholesale_share,
            "n_sellers": np.nan,
            "review_score_mean": np.nan,
            "delivery_days_mean": np.nan,
            "mean_freight_gbp": np.nan,
            "weight_kg": np.nan,
            "length_cm": np.nan,
            "width_cm": np.nan,
            "height_cm": np.nan,
        })
    out = pd.DataFrame(rows)
    # Category-level CV for short-history products (should be rare given the 12-week filter)
    if not out.empty:
        cat_cv = out.groupby("category")["weekly_units_cv"].median()
        short = out["cv_basis"].eq("observed_product_short") & out["weekly_units_cv"].notna()
        if bool(short.any()):
            mapped = out.loc[short, "category"].map(cat_cv)
            out.loc[short, "weekly_units_cv"] = pd.to_numeric(mapped, errors="coerce").to_numpy()
            out.loc[short, "cv_basis"] = "observed_category"
    return out


def _load_olist() -> dict[str, pd.DataFrame]:
    needed = {
        "orders": "olist_orders_dataset.csv",
        "items": "olist_order_items_dataset.csv",
        "products": "olist_products_dataset.csv",
        "reviews": "olist_order_reviews_dataset.csv",
        "trans": "product_category_name_translation.csv",
    }
    out = {}
    for key, name in needed.items():
        path = RAW_OLIST / name
        if not path.exists():
            raise FileNotFoundError(f"{path} missing. Run scripts/download_data.py first.")
        out[key] = pd.read_csv(path)
    return out


def build_olist(tables: dict) -> pd.DataFrame:
    orders = tables["orders"].copy()
    items = tables["items"].copy()
    products = tables["products"].copy()
    reviews = tables["reviews"].copy()
    trans = tables["trans"].copy()
    for c in ["order_purchase_timestamp", "order_delivered_customer_date",
              "order_estimated_delivery_date"]:
        if c in orders.columns:
            orders[c] = pd.to_datetime(orders[c], errors="coerce")

    # Delivered orders only, for demand. Cancelled orders are not used as returns:
    # they are not product returns and the rate would be misleadingly low.
    delivered = orders[orders["order_status"] == "delivered"]
    d = items.merge(
        delivered[["order_id", "order_purchase_timestamp", "order_delivered_customer_date",
                   "order_estimated_delivery_date"]],
        on="order_id", how="inner",
    )
    d = d.merge(products, on="product_id", how="left")
    d = d.merge(trans, on="product_category_name", how="left")
    d["week"] = d["order_purchase_timestamp"].dt.to_period("W")
    d["price_gbp"] = d["price"] / BRL_PER_GBP
    d["freight_gbp"] = d["freight_value"] / BRL_PER_GBP
    d["delivery_days"] = (
        d["order_delivered_customer_date"] - d["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400.0

    # Reviews: mean score per product, via orders.
    rev = reviews.merge(d[["order_id", "product_id"]].drop_duplicates(), on="order_id", how="inner")
    review_mean = rev.groupby("product_id")["review_score"].mean()

    # Category weekly series, for CV fallback.
    cat_week = d.groupby(["product_category_name_english", "week"], sort=False)["order_item_id"].count()
    cat_cv = {}
    for cat, s in cat_week.groupby(level=0):
        s = s.droplevel(0)
        if s.empty:
            continue
        mean, cv, n, n_pos, _ = _weekly_cv(s, s.index.min(), s.index.max())
        cat_cv[cat] = cv

    weekly = d.groupby(["product_id", "week"], sort=False)["order_item_id"].count()
    grp = d.groupby("product_id", sort=False)

    rows = []
    for pid, g in grp:
        n_orders = int(g["order_id"].nunique())
        if n_orders < MIN_ORDERS_OLIST:
            continue
        raw_cat = g["product_category_name_english"].dropna()
        raw_en = raw_cat.mode().iloc[0] if len(raw_cat) else ""
        cat, shared, orig = map_olist_category(raw_en)
        first = g["order_purchase_timestamp"].min()
        last = g["order_purchase_timestamp"].max()
        wu_series = weekly.loc[pid]
        if isinstance(wu_series, pd.DataFrame):
            wu_series = wu_series.iloc[:, 0]
        mean_w, cv, n_weeks, n_pos, cv_basis = _weekly_cv(
            wu_series, first.to_period("W"), last.to_period("W")
        )
        if cv_basis != "observed_product":
            fallback = cat_cv.get(raw_en, np.nan)
            if np.isfinite(fallback):
                cv = float(fallback)
                cv_basis = "observed_category"
        med_price = float(g["price_gbp"].median())
        if med_price <= 0 or not np.isfinite(med_price):
            continue
        weight_g = g["product_weight_g"].median() if "product_weight_g" in g else np.nan
        length = g["product_length_cm"].median() if "product_length_cm" in g else np.nan
        height = g["product_height_cm"].median() if "product_height_cm" in g else np.nan
        width = g["product_width_cm"].median() if "product_width_cm" in g else np.nan
        short = str(pid)[:8]
        rows.append({
            "sku": f"OLS-{short}",
            "title": f"{cat} item {short}",
            "category": cat,
            "category_shared": bool(shared),
            "category_mapping": (
                f"Olist English category '{orig}' mapped to shared '{cat}'" if shared
                else f"Olist English category '{orig}', marketplace only"
            ),
            "source": "olist_marketplace",
            "source_label": OLIST_SOURCE_LABEL,
            "listing_origin": "3P observed (marketplace sellers)",
            "price": med_price,
            "price_original": float(g["price"].median()),
            "currency_original": "BRL",
            "weekly_units": mean_w,
            "weekly_units_cv": cv,
            "cv_basis": cv_basis,
            "n_orders": n_orders,
            "n_weeks_span": n_weeks,
            "n_positive_weeks": n_pos,
            "first_date": first.date().isoformat() if pd.notna(first) else "",
            "last_date": last.date().isoformat() if pd.notna(last) else "",
            "return_rate": np.nan,
            "return_rate_basis": "assumption",
            "wholesale_unit_share": np.nan,
            "n_sellers": int(g["seller_id"].nunique()),
            "review_score_mean": float(review_mean.get(pid, np.nan)),
            "delivery_days_mean": float(g["delivery_days"].mean()),
            "mean_freight_gbp": float(g["freight_gbp"].mean()),
            "weight_kg": float(weight_g) / 1000.0 if pd.notna(weight_g) and weight_g > 0 else np.nan,
            "length_cm": float(length) if pd.notna(length) else np.nan,
            "width_cm": float(width) if pd.notna(width) else np.nan,
            "height_cm": float(height) if pd.notna(height) else np.nan,
        })
    return pd.DataFrame(rows)


def attach_fees(df: pd.DataFrame) -> pd.DataFrame:
    """Published Amazon UK referral (at the product's GBP price) and FBA fulfilment."""
    recs = []
    for r in df.itertuples(index=False):
        amz = amazon_category_for(r.category)
        ref = referral_fee(amz, float(r.price))
        # Fulfilment: Observed weight and dimensions where present (Olist),
        # otherwise assumed size for the category (UCI, and Olist rows with
        # missing measurements).
        weight = r.weight_kg if pd.notna(r.weight_kg) and r.weight_kg > 0 else None
        dims = (r.length_cm, r.width_cm, r.height_cm)
        dims_ok = all(pd.notna(x) and x > 0 for x in dims)
        if weight is None:
            weight, assumed = assumed_size_for_category(r.category)
            if not dims_ok:
                dims = assumed
                dims_ok = True
            size_basis = "assumption_category_typical_size"
        elif not dims_ok:
            _, assumed = assumed_size_for_category(r.category)
            dims = assumed
            dims_ok = True
            size_basis = "observed_weight_assumed_dimensions"
        else:
            size_basis = "observed_weight_and_dimensions"
        fba = fba_fulfilment_gbp(weight, dims[0], dims[1], dims[2], apply_surcharge=True)
        recs.append({
            **r._asdict(),
            "amazon_fee_category": ref["amazon_fee_category"],
            "amazon_category_name": ref["amazon_category_name"],
            "commission_rate": ref["commission_rate"],
            "referral_fee": ref["referral_fee"],
            "referral_rule": ref["referral_rule"],
            "commission_label": ref["commission_label"],
            "fulfilment_cost": fba["fulfilment_cost"],
            "fba_tier": fba["fba_tier"],
            "fba_table_fee": fba["table_fee"],
            "fba_fuel_surcharge": fba["fuel_surcharge"],
            "fulfilment_basis": (
                "Published Amazon UK FBA rate (standard, with 2% fuel surcharge), "
                + ("Observed product weight and dimensions" if size_basis == "observed_weight_and_dimensions"
                   else "Observed weight, assumed dimensions" if size_basis == "observed_weight_assumed_dimensions"
                   else "Assumed typical size for this category")
            ),
            "size_basis": size_basis,
            "fx_brl_per_gbp": BRL_PER_GBP if r.currency_original == "BRL" else np.nan,
            "fx_label": FX_LABEL if r.currency_original == "BRL" else "n/a (already GBP)",
        })
    return pd.DataFrame(recs)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    # UCI Online Retail II is no longer in the processed table: its wholesale
    # giftware prices are not a credible 1P cost basis. 1P costs now come from
    # published retailer filings, applied to these Olist products.
    print("Building Olist marketplace products...")
    olist = build_olist(_load_olist())
    print(f"  Olist products: {len(olist)}")
    combined = olist
    print("Attaching Amazon UK published fees...")
    combined = attach_fees(combined)
    # Default return rate fill is left as NaN for Olist; the engine uses the
    # assumption when use_observed_returns is on and the value is missing.
    dest = OUT / "products.csv.gz"
    combined.to_csv(dest, index=False, compression="gzip")
    print(f"wrote {dest} ({dest.stat().st_size / 1024:.1f} KB), {len(combined)} rows")

    def counts(frame):
        return {
            "n": int(len(frame)),
            "categories": {str(k): int(v) for k, v in frame["category"].value_counts().items()},
            "shared": int(frame["category_shared"].sum()) if "category_shared" in frame else 0,
            "median_price_gbp": float(frame["price"].median()) if len(frame) else None,
        }

    summary = {
        "olist": counts(combined),
        "uci": "removed: UK gift-retailer wholesale prices are not a credible 1P cost basis",
        "total": int(len(combined)),
        "shared_categories": sorted(
            combined.loc[combined["category_shared"], "category"].dropna().unique().tolist()
        ),
        "fx": {
            "brl_per_gbp": BRL_PER_GBP,
            "window": FX_WINDOW,
            "source": FX_SOURCE,
            "label": FX_LABEL,
        },
        "filters": {
            "olist_min_orders": MIN_ORDERS_OLIST,
            "product_cv_min_weeks": MIN_WEEKS_FOR_PRODUCT_CV,
            "uci_included": False,
        },
    }
    (OUT / "build_summary.json").write_text(json.dumps(summary, indent=2))
    olist_brief = {**summary["olist"], "categories": "…"}
    print(json.dumps({**summary, "olist": olist_brief}, indent=2)[:2000])
    print("category counts:\n", combined.groupby(["source", "category"]).size().to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
