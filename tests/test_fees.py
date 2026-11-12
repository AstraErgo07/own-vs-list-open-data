"""Amazon UK referral fees and VAT treatment."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from own_vs_list.amazon_uk_fees import (
    AmazonUKFee,
    BENCHMARK_LABEL,
    blended_rate,
    intro_effective_rate,
)
from own_vs_list.uk_sources import UK_VAT_RATE


def test_computers_flat_7_percent_grossed_up_for_vat():
    fee = AmazonUKFee("computers")
    # £700 ex-VAT → £840 inc; 7% of 840 = £58.80; 58.80/700 = 8.4%.
    assert abs(fee.effective_rate_on_ex_vat(700) - 0.07 * (1 + UK_VAT_RATE)) < 1e-12
    assert BENCHMARK_LABEL.startswith("Benchmark: Amazon UK")


def test_full_size_appliances_7_and_compact_15():
    full = AmazonUKFee("full_size_appliances")
    compact = AmazonUKFee("compact_appliances")
    assert abs(full.effective_rate_on_ex_vat(400) - 0.084) < 1e-12
    assert abs(compact.effective_rate_on_ex_vat(80) - 0.15 * 1.2) < 1e-12


def test_beauty_above_ten_pounds_is_15_percent():
    fee = AmazonUKFee("beauty")
    # Mid skincare £28 ex → £33.60 inc, above £10, so 15% of inc = 18% of ex.
    assert abs(fee.effective_rate_on_ex_vat(28) - 0.18) < 1e-12
    # A £8 ex-VAT price is £9.60 inc, at or below £10, so 8% of inc = 9.6% of ex.
    assert abs(fee.effective_rate_on_ex_vat(8) - 0.08 * 1.2) < 1e-12


def test_clothing_fba_rule_above_40():
    fee = AmazonUKFee("clothing")
    # £80 ex → £96 inc. FBA: 15% of first £40 + 7% of £56 = 6 + 3.92 = 9.92; /80 = 12.4%.
    assert abs(fee.effective_rate_on_ex_vat(80, clothing_fba=True) - 9.92 / 80) < 1e-12
    # Below £40 inc, FBA special does not apply. £30 ex → £36 inc, standard 15%.
    assert abs(fee.effective_rate_on_ex_vat(30, clothing_fba=True) - 0.18) < 1e-12


def test_minimum_referral_25p():
    fee = AmazonUKFee("computers")
    # A £1 ex-VAT item: 7% of £1.20 = £0.084, floored at £0.25, so 25% of ex-VAT.
    assert abs(fee.effective_rate_on_ex_vat(1.0) - 0.25 / 1.0) < 1e-12


def test_intro_commission_and_blend():
    fee = AmazonUKFee("computers")
    intro = intro_effective_rate(700, 0.07)  # 7% of 840 / 700 = 8.4%
    assert abs(intro - 0.084) < 1e-12
    assert abs(blended_rate(fee, 700, 0.0, 0.07) - intro) < 1e-12
    amazon = fee.effective_rate_on_ex_vat(700)
    assert abs(blended_rate(fee, 700, 1.0, 0.07) - amazon) < 1e-12
    mid = blended_rate(fee, 700, 0.5, 0.07)
    assert abs(mid - 0.5 * (intro + amazon)) < 1e-12


def test_benchmark_label_is_a_stand_in():
    assert "stand-in" in BENCHMARK_LABEL.lower()
    assert "joybuy publishes" in BENCHMARK_LABEL.lower() or "until Joybuy" in BENCHMARK_LABEL
