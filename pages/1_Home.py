# pages/1_Home.py
import streamlit as st

st.set_page_config(page_title="Genovate • Home", page_icon="🧬", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 1.5rem;}
.hero {
  background: radial-gradient(1200px 600px at 10% -10%, rgba(46,134,222,0.25), transparent 60%),
              radial-gradient(1000px 600px at 90% 0%, rgba(16,185,129,0.20), transparent 60%),
              linear-gradient(180deg, rgba(20,22,26,0.04), rgba(20,22,26,0.02));
  border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 2.4rem 2rem;
}
.card {
  background: rgba(255,255,255,0.55); backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
  border: 1px solid rgba(0,0,0,0.06); border-radius: 14px; padding: 1.1rem 1.0rem;
}
@media (prefers-color-scheme: dark){
  .card { background: rgba(17,17,17,0.35); border-color: rgba(255,255,255,0.08); }
  .hero { border-color: rgba(255,255,255,0.08); }
}
.h2 { font-weight: 800; letter-spacing: -0.02em; margin: 0.2rem 0 0.6rem 0; }
.pill { display:inline-block; padding: 0.25rem 0.6rem; border-radius: 999px;
        border: 1px solid rgba(0,0,0,0.08); font-size: 0.85rem; font-weight: 600;}
@media (prefers-color-scheme: dark){ .pill{ border-color: rgba(255,255,255,0.12);} }
.stButton>button { border-radius: 10px; padding: 0.6rem 1rem; font-weight: 700;
  background: linear-gradient(135deg, #2e86de, #1abc9c); border: none; }
.stButton>button:hover { filter: brightness(1.03); transform: translateY(-1px); }
.link-btn { display:inline-block; padding: 0.55rem 0.9rem; border-radius: 10px;
  border: 1px solid rgba(0,0,0,0.08); text-decoration: none; font-weight: 700; }
@media (prefers-color-scheme: dark){ .link-btn{ border-color: rgba(255,255,255,0.12);} }
.muted { color: #6b7280; font-size: 0.92rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div style="text-align:center;">
    <div class="pill">Research Companion • CRISPR Delivery • Genomic Tools</div>
    <h1 style="font-size:3.0rem; margin: 0.5rem 0 0.2rem 0;">🧬 Genovate</h1>
    <p style="font-size:1.15rem; margin:0; opacity:0.9">
      Predict, compare, and communicate CRISPR delivery strategies with clarity and confidence.
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

st.write("")
st.markdown('<h2 class="h2">What you can do</h2>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""<div class="card"><h3>🎯 Delivery Prediction</h3>
    <p class="muted">Compare LNP vs Electroporation using efficiency, off-target risk, and viability.
    Switch to a weighted heuristic to reflect your priorities.</p></div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="card"><h3>🧪 Gene & Sequence Tools</h3>
    <p class="muted">Paste DNA to auto-detect genes (BLAST), or visualize sequences with PAM
    motif highlighting. Explore common transcripts instantly.</p></div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="card"><h3>📄 One-click Reports</h3>
    <p class="muted">Export a clean PDF summary with radar charts and context notes—perfect for lab
    meetings, proposals, and documentation.</p></div>""", unsafe_allow_html=True)

st.write("")
st.markdown('<h2 class="h2">How it works</h2>', unsafe_allow_html=True)
s1, s2, s3, s4 = st.columns(4)
for step, title, desc in [
    ("Step 1", "Set up a case", "Choose an organ & mutation, then tune clinical parameters."),
    ("Step 2", "Run prediction", "Use the model or a weighted heuristic to get a recommended method."),
    ("Step 3", "Compare profiles", "View radar charts for efficiency, off-target risk, and viability."),
    ("Step 4", "Export PDF", "Download a polished report to share with your team."),
]:
    with (s1 if step=="Step 1" else s2 if step=="Step 2" else s3 if step=="Step 3" else s4):
        st.markdown(f"""<div class="card"><div class="pill">{step}</div>
        <h4>{title}</h4><p class="muted">{desc}</p></div>""", unsafe_allow_html=True)

st.write("")
st.markdown('<h2 class="h2">Why I built Genovate</h2>', unsafe_allow_html=True)
st.markdown("""<div class="card">
<p class="muted" style="margin-bottom:0.6rem;">
Genovate began as a personal mission after watching a close family member live with
Polycystic Kidney Disease (PKD). That experience pushed me to explore how software can
accelerate insight and communication around gene-editing decisions.</p>
<p class="muted" style="margin-bottom:0.6rem;">
My goal: make complex CRISPR choices intuitive—so researchers, students, and clinicians can
explore delivery options, understand trade-offs, and present decisions clearly.</p>
<p class="muted">
Next up: richer organ- and mutation-specific priors, more delivery modes, and data-backed
parameter estimation—moving Genovate from “research companion” toward a
robust, evidence-aware platform.</p></div>""", unsafe_allow_html=True)

st.write("")
st.markdown('<h2 class="h2">Jump in</h2>', unsafe_allow_html=True)
cta1, cta2, cta3 = st.columns([1.2,1,1])
with cta1:
    st.page_link("pages/2_Simulation.py", label="🚀 Open Simulation", icon="🎯")
with cta2:
    st.page_link("pages/3_Gene_Detection.py", label="🧬 Gene Detection", icon="🧪")
with cta3:
    st.page_link("pages/4_Sequence_Viewer.py", label="🧫 Sequence Viewer", icon="🧫")

st.write("")
st.markdown("""
<div style="text-align:center; opacity:0.85; margin-top:0.6rem;">
  <span class="muted">Questions or ideas?</span>
  &nbsp;
  <a class="link-btn" href="mailto:support@genovate.app">Email support@genovate.app</a>
</div>
""", unsafe_allow_html=True)
