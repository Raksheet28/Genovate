# pages/3_Gene_Detection.py — Modern BLAST UI
import re
import pandas as pd
import streamlit as st
from genovate_backend import detect_gene_from_sequence

st.set_page_config(page_title="Genovate • Gene Detection", page_icon="🧪", layout="wide")

# ---------- Global CSS (neon, sleek) ----------
st.markdown("""
<style>
.stApp {
  background:
    radial-gradient(1000px 700px at 15% 8%, #b388ff22 0%, transparent 55%),
    radial-gradient(900px 600px at 85% 5%, #7ef9c222 0%, transparent 50%),
    linear-gradient(180deg, #0a0f15 0%, #0b0f14 100%);
  color: #e8eaf0;
}
.hero, .card {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 16px;
  box-shadow: 0 18px 42px rgba(0,0,0,.35);
}
.hero { padding: 1.2rem 1.3rem; }
.card { padding: 1.0rem 1.1rem; }
h1, h2, h3 { color:#eef0ff; letter-spacing:.2px; }
.small { color:#9fb0c7; font-size:.9rem; }
.good { color:#9be4c5; }
.warn { color:#ffd08a; }
.bad { color:#ff9aa9; }
.kpi { display:flex; gap:12px; align-items:center; }
.kpill {
  border:1px solid rgba(255,255,255,.18);
  border-radius: 10px;
  padding: .2rem .55rem;
  font-weight:700;
  font-size:.82rem;
  background: rgba(255,255,255,.04);
}
.stButton>button {
  background: linear-gradient(90deg, #6e56cf, #58ffc1);
  color:#0b1722; border:none; border-radius:12px;
  font-weight:800; padding:.55rem 1rem;
  box-shadow: 0 0 18px #6e56cf66, inset 0 0 10px #b8a9ff66;
}
.stButton>button:hover { transform: translateY(-1px); }
.dataframe th { background:#111827 !important; color:#dfe7f5 !important; }
</style>
""", unsafe_allow_html=True)

# ---------- Title / Hero ----------
st.title("🧪 Gene Detection (BLAST)")
st.caption("Paste a DNA fragment (≥120 bp). The backend is biased to *Homo sapiens* for speed & relevance.")

c_hero_l, c_hero_r = st.columns([1.25, 1], gap="large")
with c_hero_l:
    st.markdown("""
    <div class="hero">
      <h3 style="margin-top:0;">What this does</h3>
      <p class="small">
        We run <b>BLASTN (megablast)</b> on your sequence and show up to three likely matches with quick identity
        estimates. Use this to sanity-check gene context from a fragment you’re exploring.
      </p>
      <div class="kpi">
        <span class="kpill">Megablast</span>
        <span class="kpill">Human-biased</span>
        <span class="kpill">Top 3 hits</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with c_hero_r:
    st.markdown("""
    <div class="card">
      <h4 style="margin:.2rem 0 .4rem 0;">Tips</h4>
      <ul class="small" style="margin-top:.2rem;">
        <li>Use clean A/C/G/T/N characters only (remove FASTA headers).</li>
        <li>Longer is better — aim for <span class="good">≥ 200 bp</span> when possible.</li>
        <li>If you’re testing multiple fragments, throttle requests to avoid NCBI rate limits.</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# ---------- Input & validators ----------
left, right = st.columns([1.35, 1], gap="large")

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Keep value stable across reruns
    if "blast_seq" not in st.session_state:
        st.session_state.blast_seq = ""

    def set_demo():
        # clean demo (160bp)
        st.session_state.blast_seq = ("ACGT" * 40)

    top_cols = st.columns([1, .35])
    with top_cols[0]:
        st.write("**Paste DNA sequence (A/C/G/T/N only):**")
    with top_cols[1]:
        st.button("Insert demo", on_click=set_demo, use_container_width=True)

    seq_in = st.text_area(
        label="",
        key="blast_seq",
        height=170,
        placeholder="ACGT…",
        help="Tip: copy from NCBI FASTA and remove the header line.",
    )

    # Live validators
    stripped = re.sub(r"\s", "", seq_in or "")
    bad_chars = re.findall(r"[^ACGTNacgtn]", stripped)
    length = len(stripped)

    vcol1, vcol2, vcol3 = st.columns(3)
    with vcol1:
        st.markdown(f"**Length:** {length} bp")
    with vcol2:
        if length >= 200:
            st.markdown("**Quality:** <span class='good'>Great</span>", unsafe_allow_html=True)
        elif length >= 120:
            st.markdown("**Quality:** <span class='warn'>Okay</span>", unsafe_allow_html=True)
        else:
            st.markdown("**Quality:** <span class='bad'>Too short</span>", unsafe_allow_html=True)
    with vcol3:
        if bad_chars:
            st.markdown(f"**Invalid chars:** <span class='bad'>{len(bad_chars)}</span>", unsafe_allow_html=True)
        else:
            st.markdown("**Invalid chars:** 0")

    # Options / Debug
    show_debug = st.checkbox("Show raw hit strings (debug)", value=False)

    run = st.button("🧬 Run BLAST Detection", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Results")

    if run:
        if length < 120:
            st.error("Please paste a valid sequence ≥120 bp.")
        elif bad_chars:
            st.error("Sequence contains invalid characters. Allowed: A, C, G, T, N.")
        else:
            with st.spinner("Running BLAST…"):
                results = detect_gene_from_sequence(stripped)

            errors = [r for r in results if r.startswith("❌")]
            hits = [r for r in results if not r.startswith("❌")]

            if errors:
                for e in errors:
                    st.error(e)

            if hits:
                rows = []
                for h in hits:
                    parts = [p.strip() for p in h.replace("🧬", "").split("|")]
                    if len(parts) >= 3:
                        rows.append({
                            "Accession / ID": parts[0],
                            "Title (truncated)": parts[1],
                            "Identity": parts[2].replace("identity ≈ ", ""),
                        })
                    else:
                        rows.append({"Accession / ID": "", "Title (truncated)": h, "Identity": ""})

                df = pd.DataFrame(rows)
                # nicer table (index off)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )

                if show_debug:
                    st.markdown("**Raw hits**")
                    for h in hits:
                        st.code(h)

            if not hits and not errors:
                st.warning("No high-confidence match found. Try a longer region (≥200 bp).")

    else:
        st.info("Paste a sequence and click **Run BLAST Detection** to see matches.")

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("")
st.caption("Note: BLAST queries call NCBI. Consider their request rate guidelines for repeated use.")
