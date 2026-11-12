"""Streamlit AppTest smoke: the app loads, shows counts, and has no exceptions."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# AppTest needs to start from the app directory so st.Page relative paths resolve.
pytest.importorskip("streamlit")


def _captions(at) -> str:
    return " ".join(str(c.value) for c in at.caption)


def _titles(at) -> str:
    return " ".join(str(t.value) for t in at.title)


def test_main_page_loads_without_exception():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=90)
    at.run()
    assert not at.exception, f"App raised: {at.exception}"
    blob = _titles(at) + " " + _captions(at)
    assert "Own stock vs marketplace listing" in _titles(at)
    assert "Made by Ami Sata" in blob
    # Headline metrics exist and include the default counts.
    assert len(at.metric) >= 4
    metric_labels = [m.label for m in at.metric]
    assert "Bring in-house" in metric_labels
    assert "Test as 3P first" in metric_labels
    assert "Keep 3P" in metric_labels
    metric_values = {m.label: str(m.value) for m in at.metric}
    assert metric_values["Bring in-house"] == "2,604"
    assert metric_values["Test as 3P first"] == "584"
    assert metric_values["Keep 3P"] == "921"
    # Expanders we rely on.
    expander_labels = [e.label for e in at.expander]
    assert any("cannot tell us" in x.lower() or "can't tell us" in x.lower() or "gaps" in x.lower() for x in expander_labels)
    assert any("risk adjustment" in x.lower() or "demand swing" in x.lower() for x in expander_labels)
    assert any("worked" in x.lower() or "recommendation" in x.lower() or "sample shows" in x.lower() for x in expander_labels)
    assert any("published figure" in x.lower() or "published company" in x.lower() or "filing" in x.lower() for x in expander_labels)
    # Fee disclaimer is present.
    all_text = blob + " " + " ".join(str(getattr(m, "value", m)) for m in at.markdown)
    assert "Amazon UK" in all_text
    # JD is named as the source of published 20-F company figures.
    assert "JD" in all_text
    assert "Joybuy" not in all_text
    assert "OnBuy" not in all_text
    assert "Walmart" not in all_text


def test_method_page_loads_and_credits_licences():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=90)
    at.run()
    assert not at.exception
    # Switch to the method page. Streamlit accepts the file path or title.
    try:
        at.switch_page("Data and method")
    except Exception:
        at.switch_page("app_pages/method_page.py")
    at.run()
    assert not at.exception, f"Method page raised: {at.exception}"
    assert "Data and method" in _titles(at)
    text = _titles(at) + " " + _captions(at) + " " + " ".join(str(m.value) for m in at.markdown)
    assert "CC BY-NC-SA" in text or "NonCommercial" in text
    assert "Olist" in text
    assert "Amazon UK" in text
    assert "European Central Bank" in text or "ECB" in text
    assert "Made by Ami Sata" in text or "Made by Ami Sata" in _captions(at)
    assert "JD" in text
    assert "20-F" in text
    assert "Best Buy" in text
    assert "gross margin" in text.lower() or "22.5%" in text
    assert "Joybuy" not in text


def test_no_forbidden_retailer_names_in_source():
    banned = ("joybuy", "onbuy", "walmart", "jdw-rule")
    # "the range" is too generic to ban as a substring of ordinary English.
    skip = {".pyc", "__pycache__", ".gz", ".pdf"}
    hits = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(s in path.name or s in str(path) for s in skip):
            continue
        if any(part in path.parts for part in (".git", ".venv", "venv", "__pycache__", "tests")):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except (OSError, UnicodeError):
            continue
        for word in banned:
            if word in text:
                hits.append(f"{path.relative_to(ROOT)}: {word}")
    assert hits == [], f"Forbidden retailer names in source: {hits}"
