# pages/1_Home.py
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Genovate — CRISPR Delivery & Gene Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Sidebar navigation ----------
st.sidebar.markdown("### Navigate")
st.sidebar.page_link("pages/2_Simulation.py", label="🎯 Simulation")
st.sidebar.page_link("pages/3_Gene_Detection.py", label="🧪 Gene Detection")
st.sidebar.page_link("pages/4_Sequence_Viewer.py", label="🧫 Sequence Viewer")  # ✅ fixed
st.sidebar.page_link("pages/5_Learning_Mode.py", label="📘 Learning Mode")

# ---------- Hero section ----------
st.title("🧬 Genovate")
st.caption("Landing page • CRISPR Delivery & Gene Analysis Platform")

st.markdown(
    """
Welcome to **Genovate**!  
This platform helps you simulate CRISPR delivery outcomes, detect genes from DNA sequences, 
visualize PAM sites, and export professional reports.  

Use the sidebar or buttons below to get started.
"""
)

# ---------- Quick navigation cards ----------
c1, c2, c3, c4 = st.columns(4)
with c1: st.page_link("pages/2_Simulation.py", label="🎯 Simulation")
with c2: st.page_link("pages/3_Gene_Detection.py", label="🧪 Gene Detection")
with c3: st.page_link("pages/4_Sequence_Viewer.py", label="🧫 Sequence Viewer")  # ✅ fixed
with c4: st.page_link("pages/5_Learning_Mode.py", label="📘 Learning Mode")

st.markdown("---")
st.caption(f"© {datetime.now().year} Genovate — Research prototype (not for clinical use)")
