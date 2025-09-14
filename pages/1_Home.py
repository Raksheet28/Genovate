# pages/1_Home.py
import streamlit as st
from datetime import datetime

# IMPORTANT: Do NOT call st.set_page_config here (only in the main file)

# ---- Sidebar quick nav (works inside a page) ----
with st.sidebar:
    st.markdown("### Navigate")
    st.page_link("pages/2_Simulation.py",      label="🎯 Simulation")
    st.page_link("pages/3_Gene_Detection.py",  label="🧪 Gene Detection")
    st.page_link("pages/4_Sequence_Viewer.py", label="🧫 Sequence Viewer")  # <-- matches your filename
    st.page_link("pages/5_Learning_Mode.py",   label="📘 Learning Mode")

# ---- Hero / Landing ----
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
c1, c2, c3, c4 = st.columns(4)
with c1: st.page_link("pages/2_Simulation.py",      label="🚀 Open Simulation")
with c2: st.page_link("pages/3_Gene_Detection.py",  label="🧪 Run Gene Detection (BLAST)")
with c3: st.page_link("pages/4_Sequence_Viewer.py", label="🧫 Sequence Viewer")  # <-- matches filename
with c4: st.page_link("pages/5_Learning_Mode.py",   label="📘 Learning Mode")

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
