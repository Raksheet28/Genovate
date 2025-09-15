# pages/3_Gene_Detection.py — BLAST UI with rich sequence analytics
import re
from collections import Counter

import pandas as pd
import streamlit as st
from genovate_backend import detect_gene_from_sequence

st.set_page_config(page_title="Genovate • Gene Detection", page_icon="🧪", layout="wide")

# ---------- Styling (neon + clean) ----------
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
.hero { padding: 1.1rem 1.2rem; }
.card { padding: 1.0rem 1.1rem; }
h1, h2, h3 { color:#eef0ff; letter-spacing:.2px; }
.small { color:#9fb0c7; font-size:.92rem; }
.kpill {
  border:1px solid rgba(255,255,255,.18);
  border-radius: 10px;
  padding: .2rem .55rem;
  font-weight:700;
  font-size:.82rem;
  background: rgba(255,255,255,.04);
  margin-right:.35rem;
}
.good { color:#9be4c5; }
.warn { color:#ffd08a; }
.bad  { color:#ff9aa9; }
.stButton>button {
  background: linear-gradient(90deg, #6e56cf, #58ffc1);
  color:#0b1722; border:none; border-radius:12px;
  font-weight:800; padding:.55rem 1rem;
  box-shadow: 0 0 18px #6e56cf66, inset 0 0 10px #b8a9ff66;
}
.stButton>button:hover { transform: translateY(-1px); }
.dataframe th { background:#111827 !important; color:#dfe7f5 !important; }
.codebox {
  font-family: ui-monospace, Menlo, Consolas, monospace;
  background:#0e1522; border:1px solid #1c2a3d; border-radius:10px;
  padding:.6rem .8rem; color:#dfe7f5;
}
</style>
""", unsafe_allow_html=True)

# ---------- Title / Intro ----------
st.title("🧪 Gene Detection (BLAST)")
st.caption("Paste a DNA fragment (≥120 bp). The backend is biased to *Homo sapiens* for speed & relevance.")

# ---------- Helpers ----------
def _clean_seq(s: str) -> str:
    """Strip whitespace and uppercase; keep only A/C/G/T/N (drop other chars)."""
    if not s:
        return ""
    s = re.sub(r"\s+", "", s).upper()
    return re.sub(r"[^ACGTN]", "", s)

def _seq_stats(seq: str) -> dict:
    """Compute basic sequence statistics."""
    n = len(seq)
    counts = Counter(seq)
    a, c, g, t, nN = counts.get("A", 0), counts.get("C", 0), counts.get("G", 0), counts.get("T", 0), counts.get("N", 0)
    gc = (g + c) / n * 100 if n else 0.0
    at = (a + t) / n * 100 if n else 0.0
    # top dinucleotides
    di = Counter(seq[i:i+2] for i in range(len(seq) - 1) if "N" not in seq[i:i+2])
    top_di = di.most_common(5)
    return {
        "length": n,
        "A": a, "C": c, "G": g, "T": t, "N": nN,
        "GC%": round(gc, 2),
        "AT%": round(at, 2),
        "dinuc_top5": top_di,
    }

def _preview(seq: str, head=60, tail=60):
    """First/last snippet with ellipsis in the middle for long sequences."""
    if len(seq) <= head + tail + 10:
        return seq
    return f"{seq[:head]} ... {seq[-tail:]}"

def _format_hits(hits_list):
    """Parse the simplified strings returned by detect_gene_from_sequence() into rows."""
    rows = []
    for h in hits_list:
        # Example: "🧬 <id> | <title> | identity ≈ 99.3%"
        parts = [p.strip() for p in h.replace("🧬", "").split("|")]
        if len(parts) >= 3:
            rows.append({
                "Accession / ID": parts[0],
                "Hit Title (truncated)": parts[1],
                "Identity": parts[2].replace("identity ≈ ", ""),
            })
        else:
            rows.append({"Accession / ID": "", "Hit Title (truncated)": h, "Identity": ""})
    return pd.DataFrame(rows)

# ---------- Layout ----------
left, right = st.columns([1.35, 1], gap="large")

# ---- Left: Input & Analytics ----
with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Persist user input across reruns
    if "gd_seq" not in st.session_state:
        st.session_state.gd_seq = ""

    def fill_demo():
        st.session_state.gd_seq = "ACGT" * 50  # 200 bp demo

    top = st.columns([1, .35])
    with top[0]:
        st.write("**Paste DNA sequence (A/C/G/T/N only):**")
    with top[1]:
        st.button("Insert demo", on_click=fill_demo, use_container_width=True)

    raw = st.text_area("", key="gd_seq", height=180, placeholder="ACGT…")
    seq = _clean_seq(raw)

    stats = _seq_stats(seq)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Length (bp)", stats["length"])
    c2.metric("GC %", f"{stats['GC%']:.2f}")
    c3.metric("AT %", f"{stats['AT%']:.2f}")
    c4.metric("N (ambiguous)", stats["N"])

    # Base composition table
    comp_df = pd.DataFrame(
        {
            "Base": ["A", "C", "G", "T", "N"],
            "Count": [stats["A"], stats["C"], stats["G"], stats["T"], stats["N"]],
            "Proportion": [
                (stats["A"]/stats["length"]*100 if stats["length"] else 0),
                (stats["C"]/stats["length"]*100 if stats["length"] else 0),
                (stats["G"]/stats["length"]*100 if stats["length"] else 0),
                (stats["T"]/stats["length"]*100 if stats["length"] else 0),
                (stats["N"]/stats["length"]*100 if stats["length"] else 0),
            ],
        }
    )
    st.dataframe(
        comp_df.style.format({"Proportion":"{:.2f}%"}),
        use_container_width=True,
        hide_index=True,
    )

    # Dinucleotide leaderboard
    di_top = pd.DataFrame(stats["dinuc_top5"], columns=["Dinucleotide", "Count"])
    st.caption("Top dinucleotides (excluding N):")
    if not di_top.empty:
        st.dataframe(di_top, use_container_width=True, hide_index=True)
    else:
        st.info("Not enough length for dinucleotide stats.")

    # Sequence preview
    st.caption("Sequence preview (head … tail):")
    st.markdown(f"<div class='codebox'>{_preview(seq)}</div>", unsafe_allow_html=True)

    # Controls
    show_debug = st.checkbox("Show raw hit strings (debug)", value=False)
    run = st.button("🧬 Run BLAST Detection", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Right: Results ----
with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Results")

    if run:
        if stats["length"] < 120:
            st.error("Please paste a valid sequence ≥ 120 bp.")
        elif re.search(r"[^ACGTN]", seq):
            st.error("Sequence contains invalid characters. Allowed: A, C, G, T, N.")
        else:
            with st.spinner("Running BLAST…"):
                results = detect_gene_from_sequence(seq)

            errors = [r for r in results if r.startswith("❌")]
            hits = [r for r in results if not r.startswith("❌")]

            # Show query summary above the table
            st.markdown("**Query Summary**")
            st.write({
                "Length (bp)": stats["length"],
                "GC %": stats["GC%"],
                "AT %": stats["AT%"],
                "N (ambiguous)": stats["N"],
            })

            if errors:
                for e in errors:
                    st.error(e)

            if hits:
                df_hits = _format_hits(hits)
                st.markdown("**Top Matches (up to 3)**")
                st.dataframe(df_hits, use_container_width=True, hide_index=True)

                # Download
                st.download_button(
                    "Download results (CSV)",
                    data=df_hits.to_csv(index=False).encode("utf-8"),
                    file_name="genovate_gene_detection_hits.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

                if show_debug:
                    st.markdown("**Raw hits**")
                    for h in hits:
                        st.code(h)

            if not hits and not errors:
                st.warning("No high-confidence match found. Try a longer fragment (≥200 bp).")

    else:
        st.info("Paste a sequence and click **Run BLAST Detection** to see up to 3 likely matches.")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("")
st.caption("Note: BLAST queries contact NCBI; please respect their request rate guidelines for repeated use.")
