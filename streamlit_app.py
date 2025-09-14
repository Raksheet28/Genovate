# streamlit_app.py  → Home / Landing page
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Genovate — CRISPR Delivery & Gene Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Minimal, modern styling ----------
st.markdown("""
<style>
/* Container width */
.block-container {padding-top:1.5rem; max-width: 1200px;}
/* Gradient headline */
.hero-title {
  font-size: 3.0rem; line-height:1.1; font-weight: 800; margin: 0 0 .25rem 0;
  background: linear-gradient(90deg,#7dd3fc 0%, #22d3ee 35%, #34d399 70%, #a3e635 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
/* Subhead */
.hero-sub {font-size:1.1rem; color:#94a3b8; margin-top:.2rem;}
/* Pretty cards */
.card {
  border:1px solid #1f2937; background:rgba(2,6,23,.55);
  padding:1.0rem 1.1rem; border-radius:14px;
}
.card h4 {margin:0 0 .25rem 0}
.kicker {letter-spacing:.14em; font-size:.78rem; text-transform:uppercase; color:#a3e3ff;}
.badge {display:inline-block; padding:.25rem .55rem; border-radius:999px; font-size:.75rem; border:1px solid #213247;}
.cta {border:1px solid #1f2937; background:linear-gradient(180deg,rgba(2,6,23,.55),rgba(2,6,23,.35));
      padding:1rem; border-radius:14px;}
/* Buttons look consistent */
.stButton>button, .stPageLink>button, .stDownloadButton>button {
  border-radius:10px; padding:.6rem .9rem; font-weight:600;
}
.footer {color:#64748b; font-size:.85rem;}
</style>
""", unsafe_allow_html=True)

# ---------- Top nav (links must match files in pages/) ----------
st.sidebar.markdown("### Navigate")
st.sidebar.page_link("pages/2_Simulation.py", label="🎯 Simulation")
st.sidebar.page_link("pages/3_Gene_Detection.py", label="🧪 Gene Detection")
st.sidebar.page_link("pages/4_Sequence_Viewer.py", label="🧫 Sequence Viewer")  # ✅ matches your file
st.sidebar.page_link("pages/5_Learning_Mode.py", label="📘 Learning Mode")

# ---------- HERO ----------
st.markdown('<div class="kicker">GENE EDITING DECISION SUPPORT</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Genovate</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">'
    'A sleek, research-grade assistant for CRISPR delivery decisions and gene insights. '
    'Run simulations, auto-detect genes from sequence, visualize PAMs, and export a clean PDF report.'
    '</div>',
    unsafe_allow_html=True,
)
st.write("")

cta1, cta2, cta3 = st.columns([1.1, 1.1, 1])
with cta1:
    st.page_link("pages/2_Simulation.py", label="🚀 Open Simulation", icon="🧪")
with cta2:
    st.page_link("pages/3_Gene_Detection.py", label="🧬 Auto-Detect Gene", icon="🧬")
with cta3:
    st.page_link("pages/4_Sequence_Viewer.py", label="🧫 Sequence Viewer", icon="🧫")

st.write("")

# ---------- Value props ----------
st.markdown("#### Why Genovate")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        """
        <div class="card">
          <h4>Delivery Method Picks</h4>
          <p>Compare LNP vs Electroporation with either model or weighted heuristic.
          See impact on efficiency, off-target risk, and viability.</p>
          <span class="badge">Simulation</span>
        </div>
        """, unsafe_allow_html=True)
with col2:
    st.markdown(
        """
        <div class="card">
          <h4>Sequence-Aware Tools</h4>
          <p>Paste DNA to highlight SpCas9 PAMs (NGG) or use BLAST-based gene detection
          tailored for human hits.</p>
          <span class="badge">Genomics</span>
        </div>
        """, unsafe_allow_html=True)
with col3:
    st.markdown(
        """
        <div class="card">
          <h4>One-click Reports</h4>
          <p>Export beautiful PDFs with radar charts and your chosen parameters.
          Unicode-safe output using TrueType fonts.</p>
          <span class="badge">Reporting</span>
        </div>
        """, unsafe_allow_html=True)

st.write("")

# ---------- How to use ----------
st.markdown("#### How to use Genovate")
s1, s2 = st.columns([1.2, 1])
with s1:
    st.markdown(
        """
        1. **Simulation** → pick the organ & mutation, set clinical parameters, and choose **model** or **advanced heuristic**.  
           Download the **PDF report** in the results section.  
        2. **Gene Detection** → paste a ≥120 bp DNA fragment to BLAST and get likely human gene hits.  
        3. **Sequence Viewer** → enter an NCBI accession and highlight **NGG** PAM sites.  
        4. **Learning Mode** → a lightweight CRISPR primer for quick refreshers and references.
        """
    )
with s2:
    st.markdown(
        """
        <div class="cta">
          <strong>Pro tip</strong><br/>
          If you enable <em>Advanced controls</em> inside Simulation, you can:
          <ul>
            <li>Weight efficiency / off-target / viability</li>
            <li>Blend baseline profiles with your inputs</li>
            <li>Compare class probabilities</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

# ---------- Why I built it (short, friendly) ----------
st.markdown("#### Why I built Genovate")
st.markdown(
    """
    I built Genovate to turn scattered CRISPR decision notes into a **usable, visual tool**.
    Too often, delivery discussions live in slides and email threads. Genovate lets you
    capture the trade-offs, share a transparent snapshot, and iterate quickly.

    **Near-term goals:** refine organ-specific profiles, support additional nucleases, and
    add better uncertainty visuals.  
    **Long-term:** plug into curated datasets and evolve from heuristics to validated,
    interpretable models.
    """
)

st.divider()

# ---------- Quick nav again ----------
c1, c2, c3, c4 = st.columns(4)
with c1: st.page_link("pages/2_Simulation.py", label="🎯 Simulation")
with c2: st.page_link("pages/3_Gene_Detection.py", label="🧪 Gene Detection")
with c3: st.page_link("pages/4_Sequence_Viewer.py", label="🧫 Sequence Viewer")
with c4: st.page_link("pages/5_Learning_Mode.py", label="📘 Learning Mode")

st.write("")
st.markdown(
    f"<div class='footer'>© {datetime.now().year} Genovate — Research prototype (not for clinical use)</div>",
    unsafe_allow_html=True,
)
