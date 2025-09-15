# pages/1_Home.py
import streamlit as st

st.set_page_config(page_title="Genovate • Home", page_icon="🏠", layout="wide")

st.markdown("""
<style>
.hero-mini {padding: 1.3rem 1.6rem; border-radius:12px; border:1px solid #26263a;
background: linear-gradient(135deg, rgba(138,92,246,0.10), rgba(78,229,158,0.10));}
h2 { color:#e8e8ff; }
p, li, span { color:#d6d7e0; }
.tile { padding:1rem; border-radius:12px; background:#171725; border:1px solid #26263a; }
.tile h3 { margin:0 0 .35rem 0; color:#f0efff; }
.tile p { margin:0; color:#cdd0dc; }
</style>
""", unsafe_allow_html=True)

st.sidebar.page_link("streamlit_app.py", label="🏠 Home")
st.sidebar.page_link("pages/2_Simulation.py", label="🎯 Simulation")
st.sidebar.page_link("pages/3_Gene_Detection.py", label="🧪 Gene Detection")
st.sidebar.page_link("pages/4_Sequence_Viewer.py", label="🧬 Sequence Viewer")
st.sidebar.page_link("pages/5_Learning_Mode.py", label="📘 Learning Mode")

st.markdown('<div class="hero-mini"><h2>Welcome back to Genovate</h2><p>Pick a workspace below.</p></div>', unsafe_allow_html=True)
st.write("")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="tile"><h3>🎯 Simulation</h3><p>Delivery tradeoffs & PDF export.</p></div>', unsafe_allow_html=True)
    st.page_link("pages/2_Simulation.py", label="Open Simulation", icon="🧪")
with c2:
    st.markdown('<div class="tile"><h3>🧪 Gene Detection</h3><p>Quick BLAST with identity %.</p></div>', unsafe_allow_html=True)
    st.page_link("pages/3_Gene_Detection.py", label="Detect Gene", icon="🧬")
with c3:
    st.markdown('<div class="tile"><h3>🧬 Sequence Viewer</h3><p>View accessions & PAMs.</p></div>', unsafe_allow_html=True)
    st.page_link("pages/4_Sequence_Viewer.py", label="Open Viewer", icon="📄")
