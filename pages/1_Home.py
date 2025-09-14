# pages/1_Home.py
import streamlit as st

st.set_page_config(page_title="Genovate • Home", page_icon="🧬", layout="wide")

# --- Hero ---
st.markdown("""
<style>
.hero {
  padding: 2.2rem 2rem; border-radius: 16px;
  background: radial-gradient(1200px 400px at 10% -10%, #0ea5e9 0%, transparent 70%),
              radial-gradient(1400px 500px at 100% 10%, #22d3ee 0%, transparent 60%),
              linear-gradient(180deg, #0b1020 0%, #0b1020 100%);
  color: #f8fafc; border: 1px solid rgba(255,255,255,.08);
}
.cta > div > button {width:100%;}
.kpi {background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.08);
      padding: 0.9rem 1rem; border-radius: 12px;}
.small {opacity:.8; font-size:.9rem}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1 style="margin-bottom:.2rem">Genovate</h1>
  <p class="small">Decision support for CRISPR delivery & sequence exploration</p>
</div>
""", unsafe_allow_html=True)

st.write("")  # spacer

# --- Quick links ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.page_link("pages/2_Simulation.py", label="🚀 Open Simulation", icon="🧪")
with c2:
    st.page_link("pages/3_Gene_Detection.py", label="🔍 Gene Detection (BLAST)", icon="🧬")
with c3:
    st.page_link("pages/4_Sequence_View.py", label="🧫 Sequence Viewer", icon="🧫")
with c4:
    st.page_link("pages/5_Learning_Mode.py", label="📘 Learning Mode", icon="📘")

st.write("")
st.subheader("What is Genovate?")
st.write("""
Genovate helps you **compare CRISPR delivery strategies** (LNP vs. electroporation),
inspect **genomic sequences with PAM highlights**, and **auto-detect genes** from DNA
fragments using BLAST. It’s designed for researchers and students who want fast,
transparent simulations with exportable reports.
""")

st.subheader("How to use it")
st.markdown("""
1. **Simulation** – enter your organ, mutation, and clinical parameters.  
   Toggle **Advanced Controls** to use a weighted heuristic and blend baselines with your inputs.  
   Export a **PDF report** with your results and radar chart.
2. **Gene Detection** – paste ≥120 bp DNA; we BLAST (biased to human) and show top matches.
3. **Sequence Viewer** – fetch a transcript by accession; PAM sites (**NGG**) are highlighted.
4. **Learning Mode** – concise primers and links to credible resources.
""")

st.subheader("Why I created Genovate")
st.write("""
I built Genovate to make **early CRISPR delivery decisions** less guessy and more reproducible.
After wrestling with scattered spreadsheets and one-off notebooks, I wanted a **clean, interactive**
tool that combines simulation, visualization, and simple reporting.  
**Future goals:** organ-specific priors, additional delivery modalities, better on-/off-target
models, and collaboration features.
""")
