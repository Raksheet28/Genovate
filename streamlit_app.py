# streamlit_app.py — Modern Landing (buttons, neon aesthetic, more info)
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
/* App background gradient (soft neon vibe) */
.stApp {
  background:
    radial-gradient(1000px 700px at 15% 8%, #b388ff22 0%, transparent 55%),
    radial-gradient(900px 600px at 85% 5%, #7ef9c222 0%, transparent 50%),
    linear-gradient(180deg, #0a0f15 0%, #0b0f14 100%);
  color: #e8eaf0;
}

/* Headings + links */
h1, h2, h3 { color: #eef0ff; letter-spacing: .2px; }
a { color: #cbb7ff; text-decoration: none; }
a:hover { text-decoration: underline; }

/* Hero card */
.hero {
  background: linear-gradient(135deg, #1b2433 0%, #141c29 100%);
  border: 1px solid #243246;
  border-radius: 18px;
  padding: 1.6rem 1.6rem;
  box-shadow: 0 14px 38px rgba(0,0,0,.35);
}

/* Generic glass card */
.card {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 16px;
  padding: 1.2rem 1.3rem;
  box-shadow: 0 10px 30px rgba(0,0,0,.35);
}

/* Gradient 'button' look */
.stButton>button {
  background: linear-gradient(90deg, #6e56cf, #58ffc1);
  color:#0b1722 !important;
  border: 0;
  border-radius: 12px !important;
  padding: .7rem 1.3rem !important;
  font-weight: 800 !important;
  font-size: 1rem !important;
  box-shadow: 0 0 18px #6e56cf66, inset 0 0 10px #b8a9ff66;
  transition: transform .06s ease-in-out, box-shadow .12s ease;
}
.stButton>button:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 28px #6e56cf99, inset 0 0 14px #b8a9ffaa;
}

/* Button layout container */
.button-card {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 14px;
  padding: 1.1rem 1.2rem;
  text-align: center;
  margin-bottom: 1.2rem;
}
.button-card h3 { margin-bottom:.4rem; color:#eef0ff; }
.button-card p { font-size:.9rem; color:#cfd6e2; margin-bottom:1rem; }

/* Footnote */
.foot { text-align:center; color:#9aa6b2; margin-top:2.2rem; }
</style>
""", unsafe_allow_html=True)

# ---------- Hero Section ----------
st.markdown("### ")
col_hero_left, col_hero_right = st.columns([1.25, 1])
with col_hero_left:
    st.markdown("""
    <div class="hero">
      <h1>Genovate</h1>
      <h3 style="margin-top:-8px; color:#cbb7ff;">
        Fast CRISPR delivery simulation & genomic utilities
      </h3>
      <p style="color:#b7c2d5; line-height:1.55;">
        Explore delivery choices (LNP vs Electroporation), visualize PAM sites, and detect candidate genes
        from DNA fragments. Blend heuristic weights with model outputs and export polished PDFs for collaboration.
      </p>
    </div>
    """, unsafe_allow_html=True)

with col_hero_right:
    st.markdown("""
    <div class="card">
      <h3 style="margin-top:.2rem;">How to use Genovate</h3>
      <ul style="color:#c2cad8;">
        <li><b>Simulation:</b> Choose organ & gene, adjust clinical parameters, toggle <i>Advanced Controls</i>
            to blend heuristics, then export a PDF report.</li>
        <li><b>Gene Detection:</b> Paste a DNA fragment (≥120bp) to get top BLAST matches.</li>
        <li><b>Sequence Viewer:</b> Fetch a transcript by accession and highlight PAM motifs inline.</li>
        <li><b>Learning Mode:</b> Read primers on CRISPR basics and delivery methods, with curated external links.</li>
      </ul>
      <h3>Why I built it</h3>
      <p style="color:#b7c2d5;">
        I wanted a clean, fast sandbox to iterate on CRISPR delivery choices and share results
        with collaborators. Next up: organ-aware priors, additional nucleases, and richer export packs.
      </p>
    </div>
    """, unsafe_allow_html=True)

# ---------- Page Buttons ----------
st.markdown("### ")
c1, c2 = st.columns(2, gap="large")
c3, c4 = st.columns(2, gap="large")

with c1:
    st.markdown("<div class='button-card'>", unsafe_allow_html=True)
    st.markdown("### 🎯 Simulation")
    st.markdown("<p>Compare LNP vs Electroporation using your parameters, view radar plots, and export a PDF summary.</p>", unsafe_allow_html=True)
    st.page_link("pages/2_Simulation.py", label="Open Simulation")
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown("<div class='button-card'>", unsafe_allow_html=True)
    st.markdown("### 🧪 Gene Detection")
    st.markdown("<p>Paste a DNA fragment (≥120 bp). BLASTN returns top matches with identity scores.</p>", unsafe_allow_html=True)
    st.page_link("pages/3_Gene_Detection.py", label="Open Gene Detection")
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown("<div class='button-card'>", unsafe_allow_html=True)
    st.markdown("### 🧬 Sequence Viewer")
    st.markdown("<p>Fetch a transcript by accession and highlight SpCas9 PAM (NGG) motifs inline for gRNA ideation.</p>", unsafe_allow_html=True)
    st.page_link("pages/4_Sequence_Viewer.py", label="Open Sequence Viewer")
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown("<div class='button-card'>", unsafe_allow_html=True)
    st.markdown("### 📘 Learning Mode")
    st.markdown("<p>CRISPR primers & delivery guides with a concise reading list for deeper exploration.</p>", unsafe_allow_html=True)
    st.page_link("pages/5_Learning_Mode.py", label="Open Learning Mode")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Extra info band ----------
st.markdown("### ")
f1, f2, f3 = st.columns(3, gap="large")
with f1:
    st.markdown("""
    <div class="card">
      <h4>Delivery Trade-offs</h4>
      <p style="color:#b7c2d5;">Blend heuristics & models to tune efficiency, off-target risk, and viability.</p>
    </div>""", unsafe_allow_html=True)
with f2:
    st.markdown("""
    <div class="card">
      <h4>Polished Exports</h4>
      <p style="color:#b7c2d5;">One-click PDF including radar plots & rationale for fast collaboration.</p>
    </div>""", unsafe_allow_html=True)
with f3:
    st.markdown("""
    <div class="card">
      <h4>Genomic Utilities</h4>
      <p style="color:#b7c2d5;">PAM highlighting & BLAST-based hints to accelerate exploratory work.</p>
    </div>""", unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown("<div class='foot'>Developed by Raksheet Gummakonda • Genovate</div>", unsafe_allow_html=True)
