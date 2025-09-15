# streamlit_app.py
import os
import streamlit as st

# ---------- Page config ----------
st.set_page_config(
    page_title="Genovate • Landing",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Global CSS ----------
st.markdown("""
<style>
/* App background gradient */
.stApp {
  background: radial-gradient(1200px 800px at 20% 10%, #b388ff22 0%, transparent 50%),
              radial-gradient(1000px 600px at 80% 0%, #7ef9c222 0%, transparent 45%),
              linear-gradient(180deg, #0b0f14 0%, #0b0f14 100%);
  color: #e8eaf0;
}

/* Headings + accents */
h1, h2, h3 { color: #eaeaff; letter-spacing: 0.2px; }
a { color: #cbb7ff; text-decoration: none; }
a:hover { text-decoration: underline; }

/* Cards */
.card {
  background: #101621;
  border: 1px solid #1e2a3a;
  border-radius: 14px;
  padding: 1.2rem 1.3rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}
.hero {
  background: linear-gradient(135deg, #1b2433 0%, #141c29 100%);
  border: 1px solid #243246;
  border-radius: 16px;
  padding: 1.6rem 1.6rem;
}

/* Buttons */
.stButton>button, .stDownloadButton>button {
  background: #6e56cf; /* light purple saber */
  color: white;
  border: none;
  border-radius: 10px;
  padding: 0.6rem 1rem;
  font-weight: 600;
  transition: transform .05s ease-in-out, box-shadow .1s ease;
  box-shadow: 0 0 20px #6e56cf55, inset 0 0 10px #8f7bf5aa;
}
.stButton>button:hover, .stDownloadButton>button:hover {
  transform: translateY(-1px);
  box-shadow: 0 0 26px #6e56cf88, inset 0 0 10px #b8a9ff88;
}

/* Sidebar */
.sidebar-title { font-weight: 700; font-size: 1.0rem; padding-top: .4rem; }
.sidebar-sub { color: #95a1b5; margin-top: .5rem; font-size: .85rem; }
.sidebar-sep { border-top: 1px solid #233148; margin: .6rem 0 .2rem 0; }
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar Nav (no self-link on Home) ----------
st.sidebar.markdown('<div class="sidebar-title">Genovate</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-sub">Navigate</div>', unsafe_allow_html=True)
st.sidebar.markdown("🏠 **Home**")  # label only; main script can't be linked
st.sidebar.page_link("pages/2_Simulation.py", label="🎯 Simulation")
st.sidebar.page_link("pages/3_Gene_Detection.py", label="🧪 Gene Detection")
st.sidebar.page_link("pages/4_Sequence_Viewer.py", label="🧬 Sequence Viewer")
st.sidebar.page_link("pages/5_Learning_Mode.py", label="📘 Learning Mode")
st.sidebar.markdown('<div class="sidebar-sep"></div>', unsafe_allow_html=True)
st.sidebar.caption("Research prototype — not for clinical use.")

# ---------- Hero Section ----------
st.markdown("### ")
col_hero_left, col_hero_right = st.columns([1.25, 1])
with col_hero_left:
    st.markdown("""
    <div class="hero">
      <h1>Genovate</h1>
      <h3 style="margin-top:-8px; color:#cbb7ff;">CRISPR delivery simulation & genomic viewers</h3>
      <p style="color:#b7c2d5; line-height:1.5;">
        Genovate helps you rapidly explore delivery choices (LNP vs Electroporation), visualize PAM sites,
        and detect candidate genes from DNA. Blend heuristic weights with model outputs and export
        polished PDFs for collaboration.
      </p>
      <div style="display:flex; gap:12px; flex-wrap:wrap;">
        """, unsafe_allow_html=True)
    st.page_link("pages/2_Simulation.py", label="🚀 Open Simulation")
    st.page_link("pages/3_Gene_Detection.py", label="🧪 Gene Detection")
    st.page_link("pages/4_Sequence_Viewer.py", label="🧬 Sequence Viewer")
    st.page_link("pages/5_Learning_Mode.py", label="📘 Learning Mode")
    st.markdown("</div></div>", unsafe_allow_html=True)

with col_hero_right:
    st.markdown("""
    <div class="card">
      <h3 style="margin-top:.2rem;">How to use Genovate</h3>
      <ul style="color:#c2cad8;">
        <li><b>Simulation:</b> Set organ & gene, adjust clinical parameters, toggle <i>Advanced Controls</i>
            to blend heuristics, then export a PDF report.</li>
        <li><b>Gene Detection:</b> Paste a DNA fragment (≥120bp) to get top BLAST matches.</li>
        <li><b>Sequence Viewer:</b> Fetch a transcript by accession and highlight PAM motifs.</li>
      </ul>
      <h3>Why I built it</h3>
      <p style="color:#b7c2d5;">
        I wanted a fast, clean sandbox to iterate on CRISPR delivery choices and communicate results with
        collaborators. This is a living project—next up: organ-aware priors, new nucleases, and richer reports.
      </p>
    </div>
    """, unsafe_allow_html=True)

# ---------- Feature Cards ----------
st.markdown("### ")
f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("""
    <div class="card">
      <h4>Delivery Tradeoffs</h4>
      <p style="color:#b7c2d5;">Model vs weighted heuristic with blend controls to tune efficiency, off-target risk, and viability.</p>
    </div>""", unsafe_allow_html=True)
with f2:
    st.markdown("""
    <div class="card">
      <h4>Polished Exports</h4>
      <p style="color:#b7c2d5;">One-click PDF including radar comparisons and decision rationale.</p>
    </div>""", unsafe_allow_html=True)
with f3:
    st.markdown("""
    <div class="card">
      <h4>Genomic Utilities</h4>
      <p style="color:#b7c2d5;">Quick PAM highlighting and BLAST-based gene hints for exploratory work.</p>
    </div>""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Developed by Raksheet Gummakonda • Genovate")
