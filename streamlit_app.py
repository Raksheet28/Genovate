# streamlit_app.py  → acts as the Home page
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Genovate — CRISPR Delivery & Gene Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Sidebar: built-in pages nav is already shown by Streamlit ----------
with st.sidebar:
    st.markdown("### Navigate")
    # Try to render explicit page links (works on most hosts)
    try:
        st.page_link("pages/2_Simulation.py",      label="🎯 Simulation")
        st.page_link("pages/3_Gene_Detection.py",  label="🧪 Gene Detection")
        st.page_link("pages/4_Sequence_Viewer.py", label="🧫 Sequence Viewer")
        st.page_link("pages/5_Learning_Mode.py",   label="📘 Learning Mode")
    except Exception:
        st.info("Use the built-in page list below to navigate.")

# ---------- Styles ----------
st.markdown(
    """
    <style>
      .hero {
        padding: 2.4rem 2rem;
        border-radius: 18px;
        background: radial-gradient(1200px 600px at 5% 10%, rgba(67,97,238,.14), transparent 60%),
                    radial-gradient(1000px 500px at 95% -10%, rgba(67,97,238,.12), transparent 65%),
                    linear-gradient(180deg, #0b0f1a 0%, #0a0e19 100%);
        border: 1px solid rgba(255,255,255,0.06);
      }
      .title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: .3px;
        background: linear-gradient(90deg, #E2E8F0, #A5B4FC 60%, #93C5FD);
        -webkit-background-clip: text; background-clip: text; color: transparent;
        margin-bottom: .25rem;
      }
      .subtitle { color: #c8d0e0; font-size: 1.05rem; margin-bottom: 0.2rem; }
      .tag { display:inline-block; padding:.2rem .6rem; border-radius: 999px;
             border:1px solid rgba(255,255,255,.15); color:#9BB6FF; font-weight:600; font-size:.78rem;
             background: rgba(147,197,253,.06); margin-right:.4rem; }
      .card {
        padding: 1.0rem 1.0rem; border-radius: 14px;
        background: #0e1422; border: 1px solid rgba(255,255,255,0.06);
      }
      .card h4 { margin: 0 0 .4rem 0; }
      .cta { border-radius: 12px; padding: .85rem 1rem; width: 100%;
             border: 1px solid rgba(255,255,255,.12); background: #11203a; color: #dfe7ff; }
      .cta:hover { background:#152643; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Hero ----------
st.markdown(
    """
    <div class="hero">
      <div class="title">Genovate</div>
      <div class="subtitle">Modern tools for CRISPR delivery simulation, gene detection, and sequence insight — with exportable, professional-grade reports.</div>
      <div class="subtitle" style="opacity:.9;">Built for researchers, clinicians, and students exploring translational genome editing.</div>
      <div style="margin-top:.8rem;">
        <span class="tag">Simulation</span>
        <span class="tag">Gene Detection</span>
        <span class="tag">Sequence Viewer</span>
        <span class="tag">PAM Highlighting</span>
        <span class="tag">PDF Export</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# ---------- CTAs (with safe fallback) ----------
c1, c2, c3, c4 = st.columns(4)
def _cta_fallback(label):
    st.button(label, disabled=True, help="Use the sidebar pages list to open this.")

try:
    with c1: st.page_link("pages/2_Simulation.py",      label="🚀 Open Simulation")
    with c2: st.page_link("pages/3_Gene_Detection.py",  label="🧪 Run Gene Detection (BLAST)")
    with c3: st.page_link("pages/4_Sequence_Viewer.py", label="🧫 Sequence Viewer")
    with c4: st.page_link("pages/5_Learning_Mode.py",   label="📘 Learning Mode")
except Exception:
    with c1: _cta_fallback("🚀 Open Simulation")
    with c2: _cta_fallback("🧪 Run Gene Detection (BLAST)")
    with c3: _cta_fallback("🧫 Sequence Viewer")
    with c4: _cta_fallback("📘 Learning Mode")
    st.info("If buttons are disabled, use the sidebar pages list to navigate.")

st.write("")
a, b = st.columns([1.3, 1])
with a:
    st.markdown(
        """
        ### What is Genovate?
        Genovate helps you:
        - **Simulate** CRISPR delivery choices (e.g., LNP vs electroporation) with confidence estimates  
        - **Detect** likely genes from a pasted DNA fragment (fast BLAST wrapper)  
        - **Inspect** sequences with automatic **NGG** PAM highlighting  
        - **Export** clean, **Unicode-safe PDFs** for lab notes and reviews
        """)
with b:
    st.markdown(
        """
        ### How to use it
        1. Open **Simulation** and enter organ, gene, and parameters  
        2. Review the **radar chart** and confidence  
        3. Click **Download PDF** — it’s robust to long text & Unicode  
        4. Explore **Gene Detection** or **Sequence Viewer** as needed
        """)

st.markdown("---")
st.markdown(
    """
    #### Why I built this
    I created Genovate to make **CRISPR decision-support** fast, transparent, and shareable.  
    My goal is to turn exploratory genome editing work into **clear, reproducible artifacts** you can discuss with your team.
    """)
st.caption(f"© {datetime.now().year} Genovate — Research prototype (not for clinical use)")
