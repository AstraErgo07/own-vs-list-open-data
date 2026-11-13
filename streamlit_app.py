"""Streamlit entry point: anonymised 1P/3P framework (development branch)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))

import streamlit as st

st.set_page_config(page_title="1P vs 3P | Marketplace Decision Framework",layout="wide")
from common.nav import footer

nav=st.navigation({
    "Decision Framework":[st.Page("app_pages/anonymous_100_product_framework.py",title="100-product comparison",url_path="100-product-framework",default=True)],
    "Original analysis":[st.Page("app_pages/own_vs_list_page.py",title="Legacy Own vs List",url_path="legacy-own-vs-list")],
    "About":[st.Page("app_pages/method_page.py",title="Method and changes",url_path="method-and-changes")],
})
nav.run()
footer()
