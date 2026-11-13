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
    # First-screen headline: A vs B 1P share of sub-categories and of modelled sales.
    assert any("sub-categor" in m.lower() and "1p" in m.lower() and m.startswith("A") for m in metric_labels)
    assert any("modelled sales" in m.lower() and "1p" in m.lower() and m.startswith("A") for m in metric_labels)
    assert any("sub-categor" in m.lower() and "1p" in m.lower() and m.startswith("B") for m in metric_labels)
    assert any("modelled sales" in m.lower() and "1p" in m.lower() and m.startswith("B") for m in metric_labels)
    # Counts still appear (caption and the later maturity metrics). Do not
    # hard-code a recommendation split, because entrant assumptions are reviewable.
    assert "Bring in-house" in blob or "Bring in-house" in metric_labels
    assert "Test as 3P first" in blob or "Test as 3P first" in metric_labels
    assert "Keep 3P" in blob or "Keep 3P" in metric_labels
    expander_labels = [e.label for e in at.expander]
    assert any("how it decides" in x.lower() for x in expander_labels)
    assert "illustrative" in blob.lower()
    assert "Joybuy-inspired" in blob or "Joybuy-inspired" in blob.replace("‑", "-")
    assert "advertis" in blob.lower()
    assert "warehouse" in blob.lower() or "Milton Keynes" in blob
    assert "Currys" in blob or "18.3" in blob
    assert "Olist" not in blob  # dropped, not on the main page
    assert "breakeven" in blob.lower() or "Break-even" in blob or "Breakeven" in blob
    assert "Made by Ami Sata" in blob
    # v3.2 surface: both verdicts, seller coverage, sunk cost, version.
    assert "v3.2" in blob or "v3.2" in _titles(at) or "v3.2" in _captions(at)
    assert "unit" in blob.lower() and "strategic" in blob.lower()
    assert "seller coverage" in blob.lower() or "Seller coverage" in blob
    assert "sunk" in blob.lower() or "variable" in blob.lower()
    assert "Do not range" in blob or "not ranged" in blob.lower() or "Do not range" in metric_labels
    # Version history and the JD China 78.2% note belong on Method and changes,
    # not as the opening of the main page.
    assert "principled fix" not in blob.lower()
    # If 78.2% still appears later (findings), it must not be Joybuy's mix.
    if "78.2" in blob or "78%" in blob:
        assert "parent" in blob.lower() or "JD China" in blob or "not Joybuy" in blob
    assert "land-grab" in blob.lower() or "strategic" in blob.lower()


def test_method_page_loads_and_credits_sources():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=90)
    at.run()
    assert not at.exception
    try:
        at.switch_page("Method and changes")
    except Exception:
        at.switch_page("app_pages/method_page.py")
    at.run()
    assert not at.exception, f"Method page raised: {at.exception}"
    assert "Method and changes" in _titles(at)
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
    assert "seller coverage" in text.lower() or "Seller coverage" in text or "coverage" in text.lower()
    assert "variable" in text.lower() or "sunk" in text.lower()
    assert "v3.2" in text or "v3.2" in _captions(at) or "v3.1" in text
    # Version history and the stress-test summary live here, not on the first screen.
    assert "principled fix" in text.lower()
    assert "78.2" in text
    assert "parent" in text.lower() or "JD China" in text or "not Joybuy" in text
    assert "stress" in text.lower()
    assert "not used as a target" in text.lower() or "not a target" in text.lower()


def test_joybuy_is_the_subject_and_old_bans_do_not_apply():
    """v3.2 still cites Joybuy where a published figure is used; the old source-ban on that name is retired."""
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
