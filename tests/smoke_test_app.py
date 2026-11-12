"""Streamlit AppTest smoke: the app loads, shows both scenarios, and has no exceptions."""
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
    assert "Joybuy" in blob
    assert "Benchmark: Amazon UK" in blob
    assert "stand-in" in blob.lower()
    assert "Entrant" in blob or "entrant" in blob
    assert "Established" in blob or "established" in blob
    metric_labels = [m.label for m in at.metric]
    assert "Bring in-house" in metric_labels
    assert "Test as 3P first" in metric_labels
    assert "Keep 3P" in metric_labels
    assert any("sub-categor" in m.lower() for m in metric_labels)
    assert any("modelled sales" in m.lower() for m in metric_labels)
    # Mid-band headline: 20 sub-categories on each side. Do not hard-code
    # a recommendation split, because entrant assumptions are reviewable.
    expander_labels = [e.label for e in at.expander]
    assert any("open question" in x.lower() or "reviewer" in x.lower() or "haircut" in x.lower()
               for x in expander_labels)
    assert "advertis" in blob.lower()
    assert "warehouse" in blob.lower() or "Milton Keynes" in blob
    assert "Currys" in blob or "18.3" in blob
    assert "61%" in blob or "61" in blob
    assert "Olist" not in blob  # dropped, not on the main page
    assert "breakeven" in blob.lower() or "Break-even" in blob or "Breakeven" in blob
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
    assert "Joybuy" in text
    assert "has not published" in text.lower() or "not published" in text.lower()
    assert "Amazon UK" in text or "sell.amazon.co.uk" in text
    assert "Currys" in text
    assert "18.3" in text
    assert "THG" in text
    assert "39.3" in text
    assert "Zalando" in text
    assert "Jiang" in text or "mid-tail" in text.lower()
    assert "VAT" in text
    assert "61%" in text or "61" in text
    assert "Olist" in text  # mentioned as dropped
    assert "no longer used" in text.lower() or "dropped" in text.lower() or "drops" in text.lower()
    assert "Assumption" in text
    assert "open question" in text.lower() or "Open question" in text
    assert "GMV" in text or "gmv" in text.lower()


def test_joybuy_is_the_subject_and_old_bans_do_not_apply():
    """v3.0 is about Joybuy; the old source-ban on that name is retired."""
    # OnBuy and Walmart still should not appear as if they were this model.
    banned = ("onbuy", "walmart")
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
    assert hits == [], f"Unexpected retailer names in source: {hits}"
    # And Joybuy must appear, because it is the subject.
    found = False
    for path in (ROOT / "own_vs_list").rglob("*.py"):
        if "joybuy" in path.read_text(errors="replace").lower():
            found = True
            break
    assert found, "expected Joybuy to appear in the model source"
