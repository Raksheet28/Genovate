# pages/1_Home.py
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Genovate — CRISPR Delivery & Gene Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styles (sleek, modern, startup aesthetic) ----------
st.markdown(
    """
    <style>
      :root {
        --bg: #0a0f1f;
        --card: #0f1426;
        --ink: #e6ecff;
        --muted: #aab6d6;
        --edge: rgba(255,255,255,.08);
        --primary: #6aa5ff;
        --accent: #8b7dff;
        --glow: 0 0 40px rgba(106,165,255,.35), 0 0 80px rgba(139,125,255,.18);
      }
      .stApp { background: radial-gradient(1200px 600px at -10% -10%, rgba(139,125,255,.08), transparent 60%),
                             radial-gradient(1000px 700px at 110% 10%, rgba(106,165,255,.10), transparent 60%),
                             var(--bg) !important; }

      .hero {
        position: relative;
        margin: 0 0 1rem 0;
        padding: 2.6rem 2.2rem;
        border-radius: 20px;
        border: 1px solid var(--edge);
        background: linear-gradient(180deg, rgba(16,23,45,.7), rgba(13,18,34,.8));
        box-shadow: var(--glow);
        overflow: hidden;
      }
      .hero:after {
        content: "";
        position: absolute;
        inset: -40% -40% auto auto;
        width: 480px; height: 480px;
        background: radial-gradient(closest-side, rgba(106,165,255,.25), transparent);
        filter: blur(30px);
        opacity: .7;
      }
      .title {
        font-size: 2.6rem; line-height: 1.1; font-weight: 900;
        letter-spacing: .2px;
        background: linear-gradient(90deg, #e6ecff, #b6c4ff 45%, #9ad0ff 85%);
        -webkit-background-clip: text; background-clip: text; color: transparent;
        margin: 0 0 .5rem 0;
      }
      .subtitle { color: var(--muted); font-size: 1.06rem; margin: 0.1rem 0; }
      .chip { display:inline-block; padding:.28rem .6rem; border-radius: 999px;
              border:1px solid var(--edge); color:#cfe0ff; background: rgba(130,160,255,.08);
              font-weight: 600; font-size:.78rem; margin:.25rem .35rem .25rem 0; }

      .card {
        padding: 1.1rem 1.0rem;
        border-radius: 16px;
        background: linear-gradient(180deg, rgba(18,24,46,.8), rgba(15,20,38,.9));
        border: 1px solid var(--edge);
      }
      .card h4 { color: var(--ink); margin: .1rem 0 .4rem 0; }
      .card p  { color: var(--muted); margin: 0; font-size: .98rem; }

      .kpi {
        display:flex; align-items:center; gap:.6rem;
        padding:.75rem .9rem; border-radius: 12px;
        border:1px solid var(--edge); background: rgba(255,255,255,.02);
        color:#cfe0ff; font-weight:700;
      }
      .kpi .dim { color: var(--muted); font-weight:600; }

      .cta {
        display:block; width:100%; text-align:center; cursor:pointer;
        padding: .9rem 1rem; border-radius: 14px; font-weight: 800;
        letter-spacing:.2px; color:#0b1224;
        background: linear-gradient(90deg, #9ad0ff, #b8b0ff);
        border: 0; box-shadow: var(--glow);
      }
      .cta:hover { filter: brightness(1.05); }
      .cta.secondary {
        color:#dfe7ff; background: #152a4a; border:1px solid var(--edge);
        box-shadow: none;
      }
      .muted { color: var(--muted); }

      /* tighten top padding */
      .block-container { padding-top: 0.6rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar Quick Nav (with safe fallback) ----------
with st.sidebar:
    st.markdown("#### Navigate")
    try:
        st.page_link("pages/2_Simulation.py",      label="🎯 Simulation")
        st.page_link("pages/3_Gene_Detection.py",  label="🧪 Gene Detection")
        st.page_link("pages/4_Sequence_Viewer.py", label="🧫 Sequence Viewer")
        st.page_link("pages/5_Learning_Mode.py",   label="📘 Learning Mode")
    except Exception:
        st.info("Use the built-in page list below to navigate.")

# ---------- HERO ----------
st.markdown(
    """
    <div class="hero">
      <div class="title">Genovate</div>
      <div class="subtitle">Decision-support for CRISPR delivery and sequence insight — built for researchers, clinicians, and students.</div>
      <div class="subtitle">Simulate delivery methods, detect likely genes from DNA fragments, highlight PAM sites, and export clean, Unicode-safe PDFs.</div>
      <div style="margin-top:.9rem;">
        <span class="chip">LNP vs Electroporation</span>
        <span class="chip">Confidence Scoring</span>
        <span class="chip">BLAST Fast-Wrap</span>
        <span class="chip">PAM Highlighting</span>
        <span class="chip">PDF Reports</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- CTA Buttons (link to other pages) ----------
c1, c2, c3, c4 = st.columns(4)
def _fallback(label):
    st.button(label, disabled=True, help="Use the sidebar page list to open this.")

try:
    with c1: st.page_link("pages/2_Simulation.py",      label="🚀 Open Simulation")
    with c2: st.page_link("pages/3_Gene_Detection.py",  label="🧪 Run Gene Detection")
    with c3: st.page_link("pages/4_Sequence_Viewer.py", label="🧫 Sequence Viewer")
    with c4: st.page_link("pages/5_Learning_Mode.py",   label="📘 Learning Mode")
except Exception:
    with c1: _fallback("🚀 Open Simulation")
    with c2: _fallback("🧪 Run Gene Detection")
    with c3: _fallback("🧫 Sequence Viewer")
    with c4: _fallback("📘 Learning Mode")
    st.info("If buttons are disabled, use the sidebar pages list to navigate.")

st.write("")

# ---------- Value Props ----------
v1, v2, v3 = st.columns([1,1,1])
with v1:
    st.markdown(
        """
        <div class="card">
          <h4>Model + Heuristic Blend</h4>
          <p>Compare a learned model vs a transparent weighted heuristic. Tune weights, see confidence, and export the rationale.</p>
        </div>
        """, unsafe_allow_html=True)
with v2:
    st.markdown(
        """
        <div class="card">
          <h4>Fast Gene Detection</h4>
          <p>Paste a DNA fragment (≥120 bp). We fast-wrap BLAST, summarize hits, and present a neat table for downstream validation.</p>
        </div>
        """, unsafe_allow_html=True)
with v3:
    st.markdown(
        """
        <div class="card">
          <h4>Sequence Insight</h4>
          <p>View accessions, highlight NGG PAMs, and copy sequences. Perfect for rapid CRISPR design and documentation.</p>
        </div>
        """, unsafe_allow_html=True)

st.write("")

# ---------- Mini KPIs ----------
k1, k2, k3 = st.columns([1,1,1])
with k1:
    st.markdown('<div class="kpi">🚀 <span>Minutes to usable report</span> <span class="dim">≈ 2–3</span></div>', unsafe_allow_html=True)
with k2:
    st.markdown('<div class="kpi">📄 <span>Unicode-safe PDF</span> <span class="dim">DejaVu Sans</span></div>', unsafe_allow_html=True)
with k3:
    st.markdown('<div class="kpi">🧪 <span>Use cases</span> <span class="dim">Teaching, lab notes, prototyping</span></div>', unsafe_allow_html=True)

st.write("")
st.markdown("---")

# ---------- Story & How-To ----------
a, b = st.columns([1.2, 1])
with a:
    st.subheader("Why I built Genovate")
    st.markdown(
        """
        I wanted a tool that made **CRISPR decision-support** fast, transparent, and shareable.  
        In many labs, we iterate on delivery choices and sequence checks across scattered notebooks and screenshots.  
        Genovate pulls that workflow into a single place — with clean visuals and a **one-click, reproducible PDF**.
        """
    )
    st.caption("Roadmap: richer delivery models, organ-specific priors, and pluggable on-/off-target scorers.")
with b:
    st.subheader("How to use it")
    st.markdown(
        """
        **Simulation** → choose organ & mutation → set parameters → compare radar chart & confidence → **Download PDF**.  
        **Gene Detection** → paste DNA (≥120 bp) → scan results table → copy accession for follow-up.  
        **Sequence Viewer** → fetch an accession → inspect & copy highlighted regions.
        """
    )

st.write("")
st.markdown("---")

# ---------- Bottom CTA ----------
c_left, c_right = st.columns([1.2, 1])
with c_left:
    st.markdown("### Ready to start?")
    st.markdown(
        "Spin up a simulation, detect genes from a fragment, or jump into the sequence viewer. "
        "Everything exports cleanly and is designed to be **presentation-ready**."
    )
with c_right:
    try:
        st.page_link("pages/2_Simulation.py", label="✨ Start with Simulation", icon="🧪")
    except Exception:
        st.button("✨ Start with Simulation", disabled=True)

st.caption(f"© {datetime.now().year} Genovate — Research prototype (not for clinical use)")
