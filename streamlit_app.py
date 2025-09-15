# streamlit_app.py
import streamlit as st
import os

st.set_page_config(
    page_title="Genovate • CRISPR Delivery Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ====== THEME (sleek, neon lightsaber accents) ======
st.markdown("""
<style>
:root {
  --bg:#0f0f14;
  --panel:#14141d;
  --muted:#9aa0a6;
  --accent:#8a5cf6;      /* neon purple */
  --accent2:#4EE59E;     /* neon green */
  --card:#171725;
  --border: #26263a;
}
html, body, [data-testid="stAppViewContainer"] {
  background: radial-gradient(1200px 800px at 15% -10%, rgba(138,92,246,0.12), transparent 60%),
              radial-gradient(1200px 800px at 115% 10%, rgba(78,229,158,0.12), transparent 60%),
              var(--bg)!important;
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
.block-container { padding-top: 1.5rem; }
h1,h2,h3,h4 { color: #e8e8ff; }
p, li, label, span, .stCaption, .stMarkdown, .stText, .st-emotion-cache { color: #d6d7e0; }

.hero {
  padding: 2rem 2rem 1.5rem 2rem;
  border-radius: 16px;
  background:
    linear-gradient(135deg, rgba(138,92,246,0.08), rgba(78,229,158,0.08));
  border: 1px solid var(--border);
  box-shadow: 0 0 40px rgba(138,92,246,0.08), 0 0 60px rgba(78,229,158,0.06);
}
.hero h1 {
  font-size: 2.2rem;
  line-height: 1.2;
  margin: 0 0 0.4rem 0;
}
.sub { color: var(--muted); margin: 0.2rem 0 0.8rem 0; }

.badge {
  display:inline-block;
  padding: 0.28rem 0.55rem;
  border-radius: 999px;
  font-weight: 600;
  letter-spacing: 0.3px;
  font-size: 0.78rem;
  background: linear-gradient(90deg, rgba(138,92,246,0.18), rgba(78,229,158,0.18));
  border: 1px solid var(--border);
  color: #e8e8ff;
}

.tile {
  padding: 1.1rem 1.1rem 0.9rem 1.1rem;
  border-radius: 14px;
  background: var(--card);
  border: 1px solid var(--border);
  transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
}
.tile:hover {
  transform: translateY(-2px);
  border-color: rgba(138,92,246,0.5);
  box-shadow: 0 6px 22px rgba(138,92,246,0.12), inset 0 0 0 1px rgba(78,229,158,0.10);
}
.tile h3 { margin: 0.1rem 0 0.35rem 0; font-size: 1.05rem; color:#f0efff; }
.tile p { margin: 0 0 .7rem 0; font-size: 0.94rem; color:#cdd0dc; }

.cta-row a button {
  width: 100%;
  border-radius: 10px !important;
  border: 1px solid var(--border) !important;
  background: linear-gradient(90deg, rgba(138,92,246,0.22), rgba(78,229,158,0.22)) !important;
  color: #fff !important;
}

.sidebar-title {
  font-weight: 700; color: #e8e8ff; margin-bottom: .4rem;
}
.sidebar-sub { color: var(--muted); margin-bottom: .6rem; }
</style>
""", unsafe_allow_html=True)

# ====== SIDEBAR NAV (use ONLY page_link; do not use switch_page) ======
st.sidebar.markdown('<div class="sidebar-title">Genovate</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-sub">Navigate</div>', unsafe_allow_html=True)
st.sidebar.page_link("streamlit_app.py", label="🏠 Home")
st.sidebar.page_link("pages/2_Simulation.py", label="🎯 Simulation")
st.sidebar.page_link("pages/3_Gene_Detection.py", label="🧪 Gene Detection")
st.sidebar.page_link("pages/4_Sequence_Viewer.py", label="🧬 Sequence Viewer")
st.sidebar.page_link("pages/5_Learning_Mode.py", label="📘 Learning Mode")

# ====== HERO / LANDING ======
st.markdown("""
<div class="hero">
  <span class="badge">Precision CRISPR • Modern tooling</span>
  <h1>Genovate</h1>
  <p class="sub">
    A sleek workbench for CRISPR delivery simulation, gene detection, and sequence exploration —
    built to help scientists and students move faster with clarity and confidence.
  </p>
</div>
""", unsafe_allow_html=True)

# ====== VALUE PROPS & QUICK NAV ======
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
    <div class="tile">
      <h3>🎯 Simulation</h3>
      <p>Compare LNP vs Electroporation. Try advanced weighted heuristics, blend with your inputs, and export a polished PDF.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_Simulation.py", label="🚀 Open Simulation", icon="🧪")

with col2:
    st.markdown("""
    <div class="tile">
      <h3>🧪 Gene Detection</h3>
      <p>Paste a DNA snippet, BLAST against *H. sapiens*-biased db, and preview top matches with identity %.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/3_Gene_Detection.py", label="🔎 Detect Gene", icon="🧬")

with col3:
    st.markdown("""
    <div class="tile">
      <h3>🧬 Sequence Viewer</h3>
      <p>Fetch accessions, render the first N bases, auto-highlight PAMs (NGG by default), and inspect context.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/4_Sequence_Viewer.py", label="👀 Open Viewer", icon="📄")

st.markdown("")

# ====== STORY / HOW-TO ======
l, r = st.columns([1.1, 1], gap="large")
with l:
    st.subheader("What is Genovate?")
    st.write(
        "Genovate is a compact, opinionated toolkit for **CRISPR delivery decisions** and **lightweight gene analysis**. "
        "Use it to simulate delivery tradeoffs (efficiency, off-target risk, viability), quickly surface putative gene matches, "
        "and visualize sequences with PAM highlights — then export clean PDFs for lab notes or stakeholder updates."
    )
    st.markdown("**How to use it**")
    st.markdown("- Head to **Simulation** to choose an organ & mutation, tweak parameters, and get a recommended delivery method with confidence.\n"
                "- Try **Advanced Controls** to blend baselines with your inputs or switch to a weighted heuristic.\n"
                "- Use **Gene Detection** to BLAST a fragment and skim the top hits.\n"
                "- Explore **Sequence Viewer** for quick context and PAM motifs.")
with r:
    st.subheader("Why I built it")
    st.write(
        "I created Genovate to make early-stage CRISPR decisions **simpler, faster, and clearer**. "
        "I wanted a tool that felt modern but stayed honest about uncertainty — something that helps me "
        "reason about delivery choices without drowning in boilerplate. Next up: richer model priors, better organ-specific LNP profiles, "
        "and exportable notebooks for reproducibility."
    )
    st.markdown("**Future goals**")
    st.markdown("- Expand training data and add more delivery vectors.\n"
                "- Organ/mutation-conditioned profiles and uncertainty summaries.\n"
                "- Notebook exports and versioned reports for auditability.")

st.markdown("---")
st.caption("Built with ❤️ for researchers & learners. • © Genovate")
