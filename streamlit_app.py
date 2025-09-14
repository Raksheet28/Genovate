# streamlit_app.py
import os
import streamlit as st

st.set_page_config(
    page_title="Genovate — CRISPR Delivery & Gene Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

HOME_PATH = "pages/1_Home.py"

# Robust redirect to the real Home page.
if os.path.exists(HOME_PATH):
    try:
        st.switch_page(HOME_PATH)
    except Exception:
        # Fallback if switch_page isn’t available in this environment
        st.title("Genovate")
        st.caption("If you see this, click **Home** in the sidebar.")
        st.write("Pages were detected, but automatic redirect isn't available here.")
else:
    # If the Home page file is missing, show a helpful error.
    st.error("`pages/1_Home.py` not found. Please ensure your `pages/` folder contains the Home page.")
