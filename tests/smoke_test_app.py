"""Streamlit AppTest smoke: the app loads, shows counts, and has no exceptions."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("streamlit")


def _captions(at) -> str:
    return " ".join(str(c.value) for c in at.caption)


def _titles(at) -> str:
    return " ".join(str(t.value) for t in at.title)


def _blob(at) -> str:
    parts = [_titles(at), _captions(at)]
    parts += [str(getattr(m, "value", m)) for m in at.markdown]
    return " ".join(parts)


def test_main_page_loads_without_exception():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=90)
    at.run()
    assert not at.exception, f"App raised: {at.exception}"
    blob = _blob(at)
    assert "Own stock vs marketplace listing" in _titles(at)
    assert "Made by Ami Sata" in blob
    assert len(at.metric) >= 4
    metric_labels = [m.label for m in at.metric]
    assert "Bring in-house" in metric_labels
    assert "Test as 3P first" in metric_labels
    assert "Keep 3P" in metric_labels
    metric_values = {m.label: str(m.value) for m in at.metric}
    # Headline metrics are the mid-price band of each sub-category (20 rows).
    assert metric_values["Bring in-house"] == "14"
    assert metric_values["Test as 3P first"] == "3"
    assert metric_values["Keep 3P"] == "3"
    expander_labels = [e.label for e in at.expander]
    assert any("flip rules" in x.lower() or "grounded" in x.lower() for x in expander_labels)
    assert any("mid-tail" in x.lower() or "cannot tell" in x.lower() or "worked" in x.lower()
               or "recommendation" in x.lower() or "published" in x.lower()
               for x in expander_labels)
    assert "JD" in blob
    assert "Amazon" in blob or "JD" in blob
    assert "Joybuy" not in blob
    assert "OnBuy" not in blob
    assert "Walmart" not in blob
    assert "Olist" not in blob
    # Currency is RMB, not a sterling headline.
    assert "家用电器" in blob or "Home appliances" in blob or "Home appliances" in _blob(at)
    assert "breakeven" in blob.lower() or "Break-even" in blob or "Breakeven" in blob
    assert "advertis" in blob.lower()
    assert "logistics" in blob.lower()
    assert "nuance" in blob.lower() or "override" in blob.lower() or "capital-light" in blob.lower()
    assert "Made by Ami Sata" in blob


def test_method_page_loads_and_credits_sources():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=90)
    at.run()
    assert not at.exception
    try:
        at.switch_page("Data and method")
    except Exception:
        at.switch_page("app_pages/method_page.py")
    at.run()
    assert not at.exception, f"Method page raised: {at.exception}"
    assert "Data and method" in _titles(at)
    text = _blob(at)
    assert "Made by Ami Sata" in text or "Made by Ami Sata" in _captions(at)
    assert "JD" in text
    assert "20-F" in text
    assert "Best Buy" in text
    assert "Zalando" in text
    assert "Jiang" in text or "mid-tail" in text.lower() or "Mid Tail" in text
    assert "Olist" in text  # mentioned as dropped
    assert "no longer used" in text.lower() or "dropped" in text.lower() or "drops" in text.lower()
    assert "Joybuy" not in text
    assert "家用电器" in text
    assert "美妆护肤" in text
    assert "服饰内衣" in text
    assert "母婴" in text
    assert "电脑" in text
    assert "advertis" in text.lower() or "marketing" in text.lower()
    assert "107" in text
    assert "GMV" in text or "gmv" in text.lower()
    assert "9.1%" in text or "9.1" in text


def test_no_forbidden_retailer_names_in_source():
    banned = ("joybuy", "onbuy", "walmart", "jdw-rule")
    # jdw-rule.jd.hk is the official fee URL and MUST appear; drop that ban.
    banned = ("joybuy", "onbuy", "walmart")
    skip = {".pyc", "__pycache__", ".gz", ".pdf"}
    hits = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(s in path.name or s in str(path) for s in skip):
            continue
        if ".git" in path.parts or "node_modules" in path.parts or "tests" in path.parts:
            continue
        if path.suffix.lower() in {".png", ".jpg", ".ico", ".woff", ".woff2"}:
            continue
        try:
            text = path.read_text(errors="replace").lower()
        except Exception:
            continue
        for word in banned:
            if word in text:
                hits.append(f"{path.relative_to(ROOT)}: {word}")
    assert hits == [], f"Forbidden names in source: {hits}"
