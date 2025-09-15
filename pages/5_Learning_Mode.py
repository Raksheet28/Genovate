# pages/5_Learning_Mode.py
import streamlit as st
from genovate_backend import learning_mode

st.set_page_config(page_title="Genovate • Learning", page_icon="📘", layout="wide")

# Sidebar nav
st.sidebar.page_link("pages/1_Home.py", label="🏠 Home")
st.sidebar.page_link("pages/2_Simulation.py", label="🎯 Simulation")
st.sidebar.page_link("pages/3_Gene_Detection.py", label="🧪 Gene Detection")
st.sidebar.page_link("pages/4_Sequence_Viewer.py", label="🧬 Sequence Viewer")
st.sidebar.page_link("pages/5_Learning_Mode.py", label="📘 Learning Mode")

st.title("📘 Learning Mode")
with st.expander("🔬 CRISPR Basics", expanded=True):
    st.write(learning_mode["CRISPR Basics"])

c3, c4 = st.columns(2)
with c3:
    with st.expander("⚡ Electroporation", expanded=True):
        st.write(learning_mode["Electroporation"])
with c4:
    with st.expander("🧪 Lipid Nanoparticles (LNPs)", expanded=True):
        st.write(learning_mode["Lipid Nanoparticles (LNPs)"])

with st.expander("🌐 External Resources", expanded=True):
    for label, url in learning_mode["External Resources"].items():
        st.markdown(f"- [{label}]({url})")
