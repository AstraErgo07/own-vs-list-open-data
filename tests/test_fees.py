"""Published JD Worldwide category fees."""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from own_vs_list.jd_fees import FEE_ROWS, TX
from own_vs_list.published import JDW_FEE_URL, JDW_TRANSACTION_FEE


def _almost(a, b, places=9):
    assert math.isclose(a, b, rel_tol=0, abs_tol=10 ** (-places)), f"{a} != {b}"


def test_transaction_fee_is_uniform():
    _almost(TX, 0.009)
    _almost(JDW_TRANSACTION_FEE, 0.009)
    for row in FEE_ROWS.values():
        _almost(row.transaction_fee, 0.009)


def test_headline_commission_rates():
    assert FEE_ROWS["ha_major"].commission == 0.03
    assert FEE_ROWS["ha_kitchen"].commission == 0.03
    assert FEE_ROWS["co_pc"].commission == 0.03
    assert FEE_ROWS["co_tablet"].commission == 0.02
    assert FEE_ROWS["beauty_all"].commission == 0.05
    assert FEE_ROWS["apparel_other"].commission == 0.06
    assert FEE_ROWS["baby_other"].commission == 0.02
    assert FEE_ROWS["baby_care"].commission == 0.02
    assert FEE_ROWS["baby_stroller"].commission == 0.03
    assert FEE_ROWS["baby_seat"].commission == 0.03
    assert FEE_ROWS["baby_clothes"].commission == 0.05


def test_take_rate_is_sum():
    for row in FEE_ROWS.values():
        _almost(row.take_rate, row.commission + row.transaction_fee)


def test_category_names_are_jds_own():
    assert FEE_ROWS["ha_major"].first_level == "家用电器"
    assert FEE_ROWS["co_tablet"].second_level == "电脑整机"
    assert FEE_ROWS["co_tablet"].third_level == "平板电脑"
    assert FEE_ROWS["apparel_other"].first_level == "服饰内衣"
    assert FEE_ROWS["beauty_all"].first_level == "美妆护肤"
    assert FEE_ROWS["baby_clothes"].second_level == "童装"


def test_fee_url_is_the_official_rule_page():
    assert JDW_FEE_URL.endswith("ruleId=950583665543483392")
    for row in FEE_ROWS.values():
        assert row.url == JDW_FEE_URL


def test_deposits_are_in_usd_as_published():
    # Apparel merchandise: USD 15,000 at every GMV band, brand-flagship 5,000.
    assert FEE_ROWS["apparel_other"].deposit_usd == (15_000, 15_000, 15_000, 15_000, 5_000)
    # Beauty: 10k / 10k / 15k / 15k, brand 5k.
    assert FEE_ROWS["beauty_all"].deposit_usd == (10_000, 10_000, 15_000, 15_000, 5_000)
