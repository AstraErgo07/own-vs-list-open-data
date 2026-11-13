"""Public entry point: 100-product 1P/3P decision framework.

Legacy analysis files are retained in the repository for audit, but are not
exposed in the Streamlit navigation.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import streamlit as st
st.set_page_config(
    page_title="1P vs 3P | Marketplace Decision Framework",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.navigation([
    st.Page("app_pages/anonymous_100_product_framework.py",
            title="1P vs 3P Decision Framework",default=True)
]).run()
