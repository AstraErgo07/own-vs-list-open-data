"""Amazon UK published referral fees, used as a labelled benchmark stand-in.

Joybuy has not published a seller commission. These rates come from
sell.amazon.co.uk/pricing and are labelled:

    "Benchmark: Amazon UK published fees, a stand-in until Joybuy
     publishes its own."

They are not Joybuy's fees. A lower introductory commission (5–8%) is
available as a labelled Assumption, because a new marketplace may
undercut to attract sellers.

Amazon charges referral fees on the VAT-inclusive total sales price.
Assumed prices in this model are ex-VAT. Effective take on the ex-VAT
price is therefore fee(VAT-inclusive price) / ex-VAT price.
"""
from __future__ import annotations

from dataclasses import dataclass

from .uk_sources import (
    AMAZON_UK_PRICING_LABEL,
    AMAZON_UK_PRICING_URL,
    UK_VAT_RATE,
)

# Per-item minimum referral fee, Amazon UK published.
MIN_REFERRAL_GBP = 0.25

# Clothing FBA / Seller Fulfilled Prime threshold (VAT-inclusive).
CLOTHING_FBA_THRESHOLD_GBP = 40.0

BENCHMARK_LABEL = AMAZON_UK_PRICING_LABEL
BENCHMARK_URL = AMAZON_UK_PRICING_URL
BENCHMARK_NOTE = (
    "Source: Amazon UK seller pricing page (sell.amazon.co.uk/pricing). "
    "Rates used here: Consumer Electronics 7%; Computers 7%; Full-Size "
    "Appliances 7%; Compact Appliances 15%; Office Products 15%; Clothing "
    "and Accessories 5% up to £15, 10% from £15 to £20, 15% above £20; "
    "for FBA and Seller Fulfilled Prime above £40, 15% on the first £40 "
    "and 7% on the remainder; Beauty, Health and Personal Care 8% up to "
    "£10 and 15% above; Baby Products, and Baby Pushchairs and Safety "
    "Equipment, the same 8% / 15% split. Per-item minimum £0.25. "
    "A clothing change 'from 8% to 5%' for the lowest band was described "
    "as effective 5 January 2026. These are Amazon UK published rates, "
    "used as a stand-in, not as Joybuy's fees."
)


def _min_fee(fee: float) -> float:
    return max(float(fee), MIN_REFERRAL_GBP)


def clothing_standard_fee(price_inc: float) -> float:
    """Amazon UK standard clothing referral, on the VAT-inclusive price."""
    p = float(price_inc)
    if p <= 15.0:
        rate = 0.05
    elif p <= 20.0:
        rate = 0.10
    else:
        rate = 0.15
    return _min_fee(rate * p)


def clothing_fba_fee(price_inc: float) -> float:
    """FBA / Seller Fulfilled Prime clothing rule, on the VAT-inclusive price.

    The reduced 15% / 7% split applies only above £40. At or below £40
    the standard 5 / 10 / 15 schedule is used.
    """
    p = float(price_inc)
    if p <= CLOTHING_FBA_THRESHOLD_GBP:
        return clothing_standard_fee(p)
    return _min_fee(0.15 * CLOTHING_FBA_THRESHOLD_GBP + 0.07 * (p - CLOTHING_FBA_THRESHOLD_GBP))


def two_tier_fee(price_inc: float, threshold: float, low_rate: float, high_rate: float) -> float:
    p = float(price_inc)
    rate = low_rate if p <= threshold else high_rate
    return _min_fee(rate * p)


def flat_fee(price_inc: float, rate: float) -> float:
    return _min_fee(float(rate) * float(price_inc))


# Keys used by archetypes.
FEE_SCHEDULE = {
    "full_size_appliances": {
        "name": "Full-Size Appliances",
        "kind": "flat",
        "rate": 0.07,
        "note": "Amazon UK published referral: Full-Size Appliances 7%.",
    },
    "compact_appliances": {
        "name": "Compact Appliances",
        "kind": "flat",
        "rate": 0.15,
        "note": "Amazon UK published referral: Compact Appliances 15%.",
    },
    "computers": {
        "name": "Computers",
        "kind": "flat",
        "rate": 0.07,
        "note": "Amazon UK published referral: Computers 7%. Consumer Electronics is also 7%.",
    },
    "consumer_electronics": {
        "name": "Consumer Electronics",
        "kind": "flat",
        "rate": 0.07,
        "note": "Amazon UK published referral: Consumer Electronics 7%.",
    },
    "office": {
        "name": "Office Products",
        "kind": "flat",
        "rate": 0.15,
        "note": "Amazon UK published referral: Office Products 15%.",
    },
    "clothing": {
        "name": "Clothing and Accessories",
        "kind": "clothing",
        "note": (
            "Amazon UK published referral: 5% up to £15, 10% from £15 to £20, "
            "15% above £20; for FBA and Seller Fulfilled Prime above £40, "
            "15% on the first £40 and 7% on the remainder."
        ),
    },
    "beauty": {
        "name": "Beauty, Health and Personal Care",
        "kind": "two_tier",
        "threshold": 10.0,
        "low_rate": 0.08,
        "high_rate": 0.15,
        "note": "Amazon UK published referral: 8% up to £10, 15% above £10.",
    },
    "baby": {
        "name": "Baby Products",
        "kind": "two_tier",
        "threshold": 10.0,
        "low_rate": 0.08,
        "high_rate": 0.15,
        "note": "Amazon UK published referral: Baby Products 8% up to £10, 15% above £10.",
    },
    "baby_pushchairs": {
        "name": "Baby Pushchairs and Safety Equipment",
        "kind": "two_tier",
        "threshold": 10.0,
        "low_rate": 0.08,
        "high_rate": 0.15,
        "note": (
            "Amazon UK published referral: Baby Pushchairs and Safety "
            "Equipment 8% up to £10, 15% above £10."
        ),
    },
}


@dataclass(frozen=True)
class AmazonUKFee:
    """A named Amazon UK referral schedule, applied to one sub-category."""

    key: str
    label: str = BENCHMARK_LABEL

    @property
    def schedule(self) -> dict:
        return FEE_SCHEDULE[self.key]

    @property
    def display_name(self) -> str:
        return self.schedule["name"]

    @property
    def note(self) -> str:
        return self.schedule["note"]

    def fee_gbp(self, price_inc: float, clothing_fba: bool = True) -> float:
        """Referral fee in pounds, on a VAT-inclusive selling price."""
        s = self.schedule
        kind = s["kind"]
        if kind == "flat":
            return flat_fee(price_inc, s["rate"])
        if kind == "two_tier":
            return two_tier_fee(price_inc, s["threshold"], s["low_rate"], s["high_rate"])
        if kind == "clothing":
            return clothing_fba_fee(price_inc) if clothing_fba else clothing_standard_fee(price_inc)
        raise ValueError(f"Unknown fee kind: {kind}")

    def effective_rate_on_ex_vat(
        self,
        price_ex_vat: float,
        vat_rate: float = UK_VAT_RATE,
        clothing_fba: bool = True,
        intro_rate: float | None = None,
        apply_on_vat_inc: bool = True,
    ) -> float:
        """Effective take as a share of the ex-VAT price.

        If intro_rate is set, that flat rate is used instead of the Amazon
        schedule (a labelled Assumption). By default the rate is applied
        to the VAT-inclusive equivalent, consistent with Amazon practice.
        """
        price = float(price_ex_vat)
        if price <= 0:
            return float("nan")
        price_inc = price * (1.0 + float(vat_rate)) if apply_on_vat_inc else price
        if intro_rate is not None:
            fee = _min_fee(float(intro_rate) * price_inc)
        else:
            fee = self.fee_gbp(price_inc, clothing_fba=clothing_fba)
        return fee / price

    def nominal_rate_on_vat_inc(self, price_inc: float, clothing_fba: bool = True) -> float:
        """The published percentage applied to the VAT-inclusive price (before the £0.25 floor bites)."""
        fee = self.fee_gbp(price_inc, clothing_fba=clothing_fba)
        if price_inc <= 0:
            return float("nan")
        return fee / float(price_inc)


def intro_effective_rate(
    price_ex_vat: float,
    intro_rate: float,
    vat_rate: float = UK_VAT_RATE,
    apply_on_vat_inc: bool = True,
) -> float:
    """Introductory commission as a share of the ex-VAT price."""
    price = float(price_ex_vat)
    if price <= 0:
        return float("nan")
    price_inc = price * (1.0 + float(vat_rate)) if apply_on_vat_inc else price
    return _min_fee(float(intro_rate) * price_inc) / price


def blended_rate(
    fee: AmazonUKFee,
    price_ex_vat: float,
    maturity: float,
    intro_rate: float,
    vat_rate: float = UK_VAT_RATE,
    clothing_fba: bool = True,
    apply_on_vat_inc: bool = True,
) -> float:
    """Linear blend: maturity 0 = intro commission, 1 = Amazon UK schedule."""
    t = min(max(float(maturity), 0.0), 1.0)
    intro = intro_effective_rate(price_ex_vat, intro_rate, vat_rate, apply_on_vat_inc)
    amazon = fee.effective_rate_on_ex_vat(
        price_ex_vat, vat_rate, clothing_fba, intro_rate=None, apply_on_vat_inc=apply_on_vat_inc
    )
    return (1.0 - t) * intro + t * amazon


