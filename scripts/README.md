# Scripts

`build_overview_pdf.py` builds the peer-review PDF overview
(`/workspace/joybuy_own_vs_list_overview.pdf` and
`docs/joybuy_own_vs_list_overview.pdf`).

It needs reportlab and matplotlib in addition to the app’s
`requirements.txt`:

```bash
pip install reportlab matplotlib
PYTHONPATH=.. python scripts/build_overview_pdf.py
```

The PDF is a companion for sharing with reviewers. The interactive
model is the Streamlit app.
