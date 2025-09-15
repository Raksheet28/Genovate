# pages/3_Gene_Detection.py
import pandas as pd
import streamlit as st
from genovate_backend import detect_gene_from_sequence

st.set_page_config(page_title="Genovate • Gene Detection", page_icon="🧪", layout="wide")

# Sidebar nav
st.sidebar.page_link("pages/1_Home.py", label="🏠 Home")
st.sidebar.page_link("pages/2_Simulation.py", label="🎯 Simulation")
st.sidebar.page_link("pages/3_Gene_Detection.py", label="🧪 Gene Detection")
st.sidebar.page_link("pages/4_Sequence_Viewer.py", label="🧬 Sequence Viewer")
st.sidebar.page_link("pages/5_Learning_Mode.py", label="📘 Learning Mode")

st.title("🧪 Gene Detection (BLAST)")
st.caption("Paste a DNA fragment (≥120 bp). Backend is biased to Homo sapiens for speed.")

seq_in = st.text_area("Paste DNA sequence (A/C/G/T/N only):", height=160,
                      help="Tip: copy from NCBI FASTA (remove header).")
if st.button("🧬 Run BLAST Detection", use_container_width=True):
    if not seq_in or len(seq_in.strip()) < 120:
        st.error("Please paste a valid sequence ≥120 bp.")
    else:
        with st.spinner("Running BLAST…"):
            results = detect_gene_from_sequence(seq_in)

        errors = [r for r in results if r.startswith("❌")]
        hits = [r for r in results if not r.startswith("❌")]

        if errors:
            for e in errors: st.error(e)

        if hits:
            rows = []
            for h in hits:
                parts = [p.strip() for p in h.replace("🧬", "").split("|")]
                if len(parts) >= 3:
                    rows.append({
                        "Accession/ID": parts[0],
                        "Title": parts[1],
                        "Identity": parts[2].replace("identity ≈ ", ""),
                    })
                else:
                    rows.append({"Accession/ID": "", "Title": h, "Identity": ""})
            st.dataframe(pd.DataFrame(rows), use_container_width=True)

        if not hits and not errors:
            st.warning("No high-confidence match found. Try a longer region (≥200 bp).")
