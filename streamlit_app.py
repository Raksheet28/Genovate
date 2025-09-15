# pages/1_Home.py
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Genovate — CRISPR Delivery & Gene Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# Neon "lightsaber" theme CSS
# ---------------------------
st.markdown(
    """
    <style>
      :root{
        --bg:#0a0c14;
        --panel:#0f1220;
        --glass:rgba(255,255,255,.06);
        --ink:#eef1ff;
        --muted:#b8c1ff;
        --edge:rgba(255,255,255,.12);
        --laser-purple:#cdb4ff;
        --laser-green:#b6ffc0;
        --glow-purple:0 0 32px rgba(205,180,255,.55), 0 0 68px rgba(205,180,255,.24);
        --glow-green:0 0 32px rgba(182,255,192,.55), 0 0 68px rgba(182,255,192,.22);
      }

      .stApp{
        background:
          radial-gradient(1200px 700px at -10% -10%, rgba(205,180,255,.12), transparent 60%),
          radial-gradient(1000px 700px at 110% 10%, rgba(182,255,192,.10), transparent 60%),
          var(--bg)!important;
      }

      .hero{
        position:relative; overflow:hidden;
        padding:2.6rem 2.2rem;
        border-radius:22px;
        border:1px solid var(--edge);
        background:linear-gradient(180deg, rgba(18,20,36,.85), rgba(12,16,30,.9));
      }
      .hero:before, .hero:after{
        content:"";
        position:absolute; inset:auto auto -40% -20%;
        width:580px; height:580px; border-radius:50%;
        background:radial-gradient(closest-side, rgba(205,180,255,.22), transparent 60%);
        filter:blur(18px);
      }
      .hero:after{
        inset:-35% -15% auto auto;
        background:radial-gradient(closest-side, rgba(182,255,192,.20), transparent 60%);
      }

      .brand{
        font-weight:900; letter-spacing:.3px;
        font-size:2.8rem; line-height:1.05; margin:0 0 .5rem 0;
        background:linear-gradient(90deg, var(--laser-purple), #e6fffb, var(--laser-green));
        -webkit-background-clip:text; background-clip:text; color:transparent;
        text-shadow: 0 0 22px rgba(205,180,255,.25);
      }
      .tagline{ color:var(--muted); font-size:1.08rem; margin:.15rem 0; }

      .chip{
        display:inline-block; margin:.25rem .4rem .25rem 0;
        padding:.34rem .7rem; border-radius:999px;
        border:1px solid var(--edge); color:#e8edff;
        background:rgba(255,255,255,.04); font-weight:700; font-size:.78rem;
      }

      .panel{
        padding:1.2rem 1.1rem; border-radius:16px;
        background:linear-gradient(180deg, rgba(18,22,40,.8), rgba(15,18,34,.9));
        border:1px solid var(--edge);
      }
      .panel h4{ color:var(--ink); margin:.1rem 0 .5rem 0; }
      .panel p{ color:#c9d2ff; margin:0; font-size:.98rem; }

      .cta{
        width:100%; padding:.95rem 1rem; border-radius:14px; border:0;
        font-weight:900; letter-spacing:.2px; cursor:pointer;
        color:#0c1224; background:linear-gradient(90deg, var(--laser-purple), var(--laser-green));
        box-shadow: var(--glow-purple), var(--glow-green);
      }
      .cta:hover{ filter:brightness(1.06); }
      .cta.secondary{
        color:#e8f0ff; background:rgba(255,255,255,.06);
        border:1px solid var(--edge); box-shadow:none;
      }

      .kpi{
        padding:.8rem 1rem; border-radius:12px; border:1px solid var(--edge);
        background:rgba(255,255,255,.03); color:#e3eaff; font-weight:800;
      }
      .dim{ color:#a9b4ff; font-weight:600; }

      .block-container{ padding-top:.6rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------
# Small helper: safe page switching
# --------------------------------
def go(page_py: str) -> None:
    """
    Try st.switch_page('pages/XYZ.py'). If unavailable, show a hint.
    """
    try:
        st.switch_page(f"pages/{page_py}")
    except Exception:
        st.warning("Navigation API not available here. Use the **built-in pages menu** (top-left) to switch pages.")

# ---------------------------
# Sidebar (explicit navigation)
# ---------------------------
with st.sidebar:
    st.markdown("### ⚡ Quick Nav")
    if st.button("🎯 Simulation", use_container_width=True):
        go("2_Simulation.py")
    if st.button("🧪 Gene Detection", use_container_width=True):
        go("3_Gene_Detection.py")
    if st.button("🧫 Sequence Viewer", use_container_width=True):
        go("4_Sequence_Viewer.py")
    if st.button("📘 Learning Mode", use_container_width=True):
        go("5_Learning_Mode.py")
    st.markdown("---")
    st.caption("If these buttons do nothing, click the default **Pages** list in the Streamlit sidebar header.")

# ---------------------------
# HERO
# ---------------------------
st.markdown(
    """
    <div class="hero">
      <div class="brand">Genovate</div>
      <div class="tagline">CRISPR delivery decision-support • Fast gene detection • Sequence insight • One-click PDFs</div>
      <div class="tagline">Built for researchers, clinicians, and students who need answers fast — and slides even faster.</div>
      <div style="margin-top:.9rem;">
        <span class="chip">LNP vs Electroporation</span>
        <span class="chip">Confidence Scoring</span>
        <span class="chip">BLAST Summaries</span>
        <span class="chip">PAM Highlighting</span>
        <span class="chip">Unicode-Safe PDF</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Primary CTAs
# ---------------------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🚀 Open Simulation", key="cta_sim", use_container_width=True):
        go("2_Simulation.py")
with c2:
    if st.button("🧪 Run Gene Detection", key="cta_detect", use_container_width=True):
        go("3_Gene_Detection.py")
with c3:
    if st.button("🧫 Sequence Viewer", key="cta_seq", use_container_width=True):
        go("4_Sequence_Viewer.py")
with c4:
    if st.button("📘 Learning Mode", key="cta_learn", use_container_width=True):
        go("5_Learning_Mode.py")

st.write("")

# ---------------------------
# Value props (cards)
# ---------------------------
p1, p2, p3 = st.columns(3)
with p1:
    st.markdown(
        """
        <div class="panel">
          <h4>Transparent Decisions</h4>
          <p>Compare the learned model against a weighted heuristic you can tune. See why a method wins and export the reasoning.</p>
        </div>
        """, unsafe_allow_html=True)
with p2:
    st.markdown(
        """
        <div class="panel">
          <h4>BLAST, Simplified</h4>
          <p>Paste ≥120 bp, get top hits with identity summaries. Triage fast, then deep-dive in your preferred tools.</p>
        </div>
        """, unsafe_allow_html=True)
with p3:
    st.markdown(
        """
        <div class="panel">
          <h4>Sequence Insight</h4>
          <p>Highlight NGG PAMs instantly on GenBank accessions. Copy snippets for downstream CRISPR design.</p>
        </div>
        """, unsafe_allow_html=True)

st.write("")

# ---------------------------
# Mini KPIs
# ---------------------------
k1, k2, k3 = st.columns(3)
with k1:
    st.markdown('<div class="kpi">⏱️  <span class="dim">Report time</span>: ~2–3 min</div>', unsafe_allow_html=True)
with k2:
    st.markdown('<div class="kpi">📄  <span class="dim">PDF</span>: DejaVu Sans (Unicode)</div>', unsafe_allow_html=True)
with k3:
    st.markdown('<div class="kpi">🧪  <span class="dim">Use cases</span>: Teaching, prototyping</div>', unsafe_allow_html=True)

st.markdown("---")

# ---------------------------
# Story & How-to
# ---------------------------
col_a, col_b = st.columns([1.2, 1])
with col_a:
    st.subheader("Why I built Genovate")
    st.markdown(
        """
        I wanted a **fast, transparent, and clean** way to make CRISPR delivery choices and share them.
        Lab decisions often live in scattered notes; Genovate brings them into one place with a **one-click PDF**.
        Roadmap: organ-specific priors, richer delivery models, and pluggable on/off-target scorers.
        """
    )
with col_b:
    st.subheader("How to use it")
    st.markdown(
        """
        **Simulation** → set organ & mutation → adjust parameters/weights → compare radar chart & confidence → **Download PDF**.  
        **Gene Detection** → paste sequence → scan hit table → copy accessions for follow-up.  
        **Sequence Viewer** → fetch accession → inspect NGG highlights for design.
        """
    )

st.markdown("---")
st.caption(f"© {datetime.now().year} Genovate — Research prototype (not for clinical use)")
