# streamlit_app.py — Modern Landing (tiles as glowing holographic buttons)
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
/* App background gradient (soft neon "lightsaber" vibe) */
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

/* Tile (module container) */
.tile {
  background: #101621;
  border: 1px solid #1e2a3a;
  border-radius: 16px;
  padding: 1.1rem 1.1rem 1.0rem 1.1rem;
  height: 100%;
  transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease;
}
.tile:hover {
  transform: translateY(-2px);
  border-color: #a78bfa55;
  box-shadow: 0 16px 38px -12px rgba(167,139,250,.28);
}
.tile h3 { margin:.1rem 0 .15rem 0; font-size:1.1rem; color:#ecf1ff; }
.tile p { color:#cdd6e6; font-size:.95rem; margin:.1rem 0 .8rem 0; }

/* Badges on tiles */
.badge {
  display:inline-block;
  font-size:.78rem;
  color:#dfe3ea;
  border:1px solid rgba(255,255,255,.18);
  border-radius:999px;
  padding:.12rem .55rem;
  margin:.08rem .35rem .25rem 0;
  background: rgba(255,255,255,.04);
}

/* Glowing holographic button style */
.holo-btn {
  display:inline-block;
  width:100%;
  text-align:center;
  padding:.7rem 1rem;
  margin-top:.5rem;
  font-weight:800;
  color:#0b1722;
  background: linear-gradient(90deg, #6e56cf, #58ffc1);
  border-radius:14px;
  box-shadow: 0 0 20px #6e56cf66, inset 0 0 12px #b8a9ff66;
  transition: all .15s ease-in-out;
}
.holo-btn:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 0 30px #6e56cfaa, inset 0 0 14px #c3b0ff99;
  cursor:pointer;
  text-decoration:none;
}

/* Small footnote */
.foot { text-align:center; color:#9aa6b2; margin-top:2rem; }
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
      </ul>
      <h3>Why I built it</h3>
      <p style="color:#b7c2d5;">
        I wanted a clean, fast sandbox to iterate on CRISPR delivery choices and share results
        with collaborators. Next up: organ-aware priors, additional nucleases, and richer export packs.
      </p>
    </div>
    """, unsafe_allow_html=True)

# ---------- Tiles (modules as buttons) ----------
st.markdown("### ")
row1 = st.columns(2, gap="large")
row2 = st.columns(2, gap="large")

def tile(title, emoji, desc, badges, page_py, col):
    with col:
        st.markdown('<div class="tile">', unsafe_allow_html=True)
        st.markdown(f"### {emoji} {title}")
        st.markdown(f"<p>{desc}</p>", unsafe_allow_html=True)
        for b in badges:
            st.markdown(f"<span class='badge'>{b}</span>", unsafe_allow_html=True)
        # Glow button styled with holo-btn
        st.markdown(f"<a href='/pages/{page_py}' class='holo-btn'>Open {title}</a>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

tile(
    title="Simulation",
    emoji="🎯",
    desc="Compare LNP vs Electroporation using your clinical parameters, view radar plots, and export a PDF summary.",
    badges=["Delivery trade-offs", "Confidence", "PDF export"],
    page_py="2_Simulation.py",
    col=row1[0],
)
tile(
    title="Gene Detection",
    emoji="🧪",
    desc="Paste a DNA fragment (≥120 bp). BLASTN (human-biased) returns the top matches with identity scores.",
    badges=["BLAST", "Top matches", "Quick triage"],
    page_py="3_Gene_Detection.py",
    col=row1[1],
)
tile(
    title="Sequence Viewer",
    emoji="🧬",
    desc="Fetch a transcript by accession and highlight SpCas9 PAM (NGG) motifs inline for rapid gRNA ideation.",
    badges=["NCBI fetch", "PAM (NGG)", "Inline highlighting"],
    page_py="4_Sequence_Viewer.py",
    col=row2[0],
)
tile(
    title="Learning Mode",
    emoji="📘",
    desc="Short primers on CRISPR and delivery methods, with a concise reading list for deeper dives.",
    badges=["CRISPR basics", "LNP vs Electro", "Reading list"],
    page_py="5_Learning_Mode.py",
    col=row2[1],
)

# ---------- Extra info band ----------
st.markdown("### ")
c1, c2, c3 = st.columns([1,1,1], gap="large")
with c1:
    st.markdown("""
    <div class="card">
      <h4>Delivery Trade-offs</h4>
      <p style="color:#b7c2d5;">Model vs weighted heuristic with blend controls to tune efficiency, off-target risk, and viability.</p>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="card">
      <h4>Polished Exports</h4>
      <p style="color:#b7c2d5;">One-click PDF including radar comparisons and decision rationale for quick sharing.</p>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""
    <div class="card">
      <h4>Genomic Utilities</h4>
      <p style="color:#b7c2d5;">PAM highlighting and BLAST-based gene hints to accelerate exploratory work.</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<div class='foot'>Developed by Raksheet Gummakonda • Genovate</div>", unsafe_allow_html=True)
