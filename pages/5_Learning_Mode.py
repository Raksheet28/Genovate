# pages/5_Learning_Mode.py
# Sleek, modern Learning Mode with neon aesthetic + richer content

import streamlit as st
import pandas as pd
from genovate_backend import learning_mode

st.set_page_config(page_title="Genovate • Learning", page_icon="📘", layout="wide")

# ---------- Light CSS polish (matches landing vibe) ----------
st.markdown("""
<style>
.stApp {
  background:
    radial-gradient(900px 600px at 12% 10%, #b388ff22 0%, transparent 55%),
    radial-gradient(900px 600px at 88% 8%, #7ef9c222 0%, transparent 50%),
    linear-gradient(180deg, #0a0f15 0%, #0b0f14 100%);
  color:#e8eaf0;
}
h1,h2,h3 { color:#eef0ff; letter-spacing:.2px; }
a { color:#cbb7ff; text-decoration:none; } a:hover { text-decoration:underline; }

.card {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 14px;
  padding: 1.0rem 1.1rem;
  box-shadow: 0 10px 28px rgba(0,0,0,.35);
}

.badge {
  display:inline-block; padding:.15rem .55rem; border-radius:999px;
  border:1px solid rgba(255,255,255,.15); background:rgba(255,255,255,.05);
  font-size:.78rem; color:#dfe3ea; margin-right:.35rem;
}

.kpi {
  background: linear-gradient(90deg, #6e56cf, #58ffc1);
  color:#0b1722; font-weight:800; border-radius:12px; padding:.55rem .9rem;
  display:inline-block; box-shadow:0 0 18px #6e56cf66, inset 0 0 10px #b8a9ff55;
}

.hr { border-top:1px solid #243246; margin: .9rem 0 1.1rem 0; }
.small { color:#9aa6b2; font-size:.92rem; }
</style>
""", unsafe_allow_html=True)

# ---------- Title / intro ----------
st.title("📘 Learning Mode")
st.caption("A quick, practical primer on CRISPR delivery and analysis — tuned for Genovate workflows.")

# ---------- Top hero cards ----------
c1, c2, c3 = st.columns(3)
with c1:
  st.markdown('<div class="card"><div class="kpi">CRISPR 101</div><div class="hr"></div>'
              '<span class="small">Cas nuclease + guide RNA cut; cell repairs → edit. '
              'Targeting hinges on PAM & guide specificity.</span></div>', unsafe_allow_html=True)
with c2:
  st.markdown('<div class="card"><div class="kpi">Delivery Matters</div><div class="hr"></div>'
              '<span class="small">LNPs favor in-vivo liver/kidney; electroporation shines ex-vivo. '
              'Viability, scale, and off-target profiles differ.</span></div>', unsafe_allow_html=True)
with c3:
  st.markdown('<div class="card"><div class="kpi">Design Loop</div><div class="hr"></div>'
              '<span class="small">Select target → check PAMs → simulate delivery trade-offs → validate candidates externally.</span></div>', unsafe_allow_html=True)

st.markdown("")

# ---------- Tabs ----------
tab_basics, tab_delivery, tab_checklist, tab_glossary, tab_links, tab_mutations = st.tabs(
    ["🔬 CRISPR Basics", "🚚 Delivery Methods", "🛠️ Design Checklist", "📖 Glossary", "🌐 Resources", "🧬 Mutation Stats"]
)

# --- Basics ---
with tab_basics:
    st.markdown("### Core concepts")
    st.write(learning_mode["CRISPR Basics"])

    st.markdown("#### PAM patterns you’ll see in Genovate")
    st.markdown(
        "- **SpCas9:** `NGG` (canonical), supports some NAG\n"
        "- **SaCas9:** `NNGRRT`\n"
        "- **Cas12a (Cpf1):** `TTTV` (T = thymine, V = A/C/G)\n"
        "_Tip: the Sequence Viewer highlights NGG by default._"
    )

    st.info(
        "Model predictions in Genovate are decision-support only. Always validate guides with external tools "
        "and experimental controls."
    )

# --- Delivery Methods ---
with tab_delivery:
    st.markdown("### LNP vs Electroporation — quick comparison")

    df = pd.DataFrame([
        ["Lipid Nanoparticles (LNPs)",
         "In vivo delivery; liver first, kidney/other organs improving",
         "High (mRNA/protein); gentle on cells",
         "Generally lower than electro (cargo dependent)",
         "Scales well; manufacturing is the work",
         "Transient expression; payload size constraints"],
        ["Electroporation",
         "Ex vivo cells (T cells, HSCs, etc.)",
         "Very high delivery of RNP/DNA; tunable pulses",
         "Higher off-target if long exposure or DNA templates",
         "Great for small batches; cell-type optimization needed",
         "Can reduce viability; requires instrumentation"],
    ], columns=["Method","Typical Use","On-target Efficiency","Off-target Risk","Scalability","Notes"])

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("#### In Genovate")
    st.markdown(
        "- **Simulation tab** lets you compare methods with your clinical parameters.\n"
        "- **Advanced Controls** → blend heuristic weights (efficiency/viability/off-target) to reflect priorities.\n"
        "- Export a **PDF** with radar chart + inputs for quick sharing."
    )

# --- Design Checklist ---
with tab_checklist:
    st.markdown("### Practical guide design checklist")
    st.markdown(
        """
1. **Pick a PAM-rich window** near your edit site (e.g., NGG for SpCas9).
2. **Avoid long homopolymers** in the guide; aim for balanced GC (≈40–60%).
3. **Scan both strands**; sometimes the opposite strand yields better PAM/seed context.
4. **Minimize off-targets** (mismatches in seed region matter most).
5. **Choose delivery** based on context:
   - *In vivo proof-of-concept:* start with **LNP** (mRNA/protein cargo).
   - *Cell therapy/ex-vivo edits:* start with **Electroporation** (RNPs).
6. **Plan controls** (no-sgRNA, non-targeting sgRNA, safe harbor control).
7. **Document** with Genovate’s PDF export; then validate in external tools (CHOPCHOP/CRISPOR) and wet-lab.
        """
    )
    st.warning("Ethical/clinical note: ensure approvals and biosafety training before experimental work.")

# --- Glossary ---
with tab_glossary:
    st.markdown("### Quick glossary")
    gloss = pd.DataFrame([
        ["PAM", "Protospacer Adjacent Motif; short sequence required for nuclease binding (e.g., NGG)."],
        ["Seed region", "Guide bases proximal to PAM; mismatches here reduce activity most."],
        ["RNP", "Cas protein pre-complexed with guide RNA; fast and transient editing."],
        ["HDR/NHEJ", "Repair pathways; HDR for precise edits with templates, NHEJ for indels."],
        ["LNP", "Lipid nanoparticle—vesicles that deliver nucleic acids/proteins in vivo."],
    ], columns=["Term","Meaning"])
    st.table(gloss)

# --- Resources ---
with tab_links:
    st.markdown("### Curated reading")
    st.markdown(
        "- [Broad CRISPR Overview](https://www.broadinstitute.org/what-broad/areas-focus/project-spotlight/crispr)\n"
        "- [Nature CRISPR Guide](https://www.nature.com/subjects/crispr-cas9)\n"
        "- [NCBI Bookshelf: Genome Editing](https://www.ncbi.nlm.nih.gov/books/)"
    )

# --- Mutation Stats ---
with tab_mutations:
    st.markdown("### Genetic Mutation Prevalence")

    mut_df = pd.DataFrame([
        ["BRCA1 (Breast Cancer Risk)", "0.25%", "Rare", "1 in 400"],
        ["CFTR ΔF508 (Cystic Fibrosis)", "4%", "Carrier common", "1 in 25 (Caucasian ancestry)"],
        ["Sickle Cell (HbS)", "8–10%", "Moderately common", "1 in 12 (African ancestry)"],
        ["Huntington’s (HTT expansion)", "0.005%", "Ultra-rare", "1 in 20,000"],
        ["APOE4 (Alzheimer’s risk allele)", "15–20%", "Common", "1 in 5"],
    ], columns=["Mutation","% of Population","Rarity","Approx Probability"])

    st.dataframe(mut_df, use_container_width=True, hide_index=True)

    st.info("Note: Prevalence varies by ancestry and population. Data shown is approximate for educational use.")

# ---------- Footer ----------
st.markdown("---")
st.caption("Developed by Raksheet Gummakonda • Genovate")
