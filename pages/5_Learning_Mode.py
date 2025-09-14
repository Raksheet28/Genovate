import streamlit as st
from genovate_backend import learning_mode

st.set_page_config(page_title="Genovate • Learning Mode", page_icon="📘", layout="wide")
st.page_link("streamlit_app.py", label="🏠 Home")

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
