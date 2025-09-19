# pages/4_Sequence_Viewer.py
import streamlit as st
from genovate_backend import fetch_genbank_record, highlight_pam_sites
import pandas as pd

st.set_page_config(page_title="Genovate • Sequence Viewer", page_icon="🧬", layout="wide")

from ui_nav import render_top_nav
render_top_nav(active="pages/4_Sequence_Viewer.py")  # change the string to the current page's label

st.title("🧬 Genomic Sequence Viewer (PAM highlights)")
st.caption("Shows the first N bases of the selected accession and highlights NGG motifs (SpCas9 PAM).")

@st.cache_data(show_spinner=False)
def _cached_fetch(acc):
    rec = fetch_genbank_record(acc)
    return {
        "name": getattr(rec, "name", "N/A"),
        "organism": rec.annotations.get("organism", "Unknown organism"),
        "seq": str(rec.seq),
    }

common_genes = {
    "PKD1 (Homo sapiens)": "NM_001009944.3",
    "CFTR (Homo sapiens)": "NM_000492.4",
    "BRCA1 (Homo sapiens)": "NM_007294.4",
    "HTT (Homo sapiens)": "NM_002111.8",
    "TP53 (Homo sapiens)": "NM_000546.6",
    "Custom": "",
}

top = st.columns([1.5, 1, 1])
with top[0]:
    sel = st.selectbox("Choose a gene", list(common_genes.keys()))
with top[1]:
    show_len = st.slider("Bases to show", 100, 600, 200, step=50)
with top[2]:
    acc = st.text_input("NCBI Accession ID", value=common_genes[sel] if sel != "Custom" else "")

if acc:
    try:
        with st.spinner("Fetching GenBank record…"):
            info = _cached_fetch(acc)
        st.markdown(f"**🧬 Gene:** `{info['name']}`  •  **🌱 Organism:** `{info['organism']}`")
        raw_seq = info["seq"][:show_len]
        highlighted = highlight_pam_sites(raw_seq)
        st.markdown(f"<div style='font-family: ui-monospace, Menlo, Consolas; word-wrap: break-word;'>{highlighted}</div>",
                    unsafe_allow_html=True)
        st.caption(f"🔴 Highlighted = PAM Sites (NGG) • Accession ID: {acc}")
    except Exception as e:
        st.error(f"❌ Error fetching sequence: {e}")
else:
    st.info("Enter a valid accession (e.g., NM_001009944.3) to view sequence and PAMs.")
