# streamlit_app.py

import os
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from math import pi

from genovate_backend import (
    load_data,
    train_model,
    predict_method,
    predict_confidence,
    find_pam_sites,
    get_gene_image_path,
    get_mutation_summary,
    generate_pdf_report,
    learning_mode,
    fetch_genbank_record,
    highlight_pam_sites,
    detect_gene_from_sequence,   # NEW BLAST version (no esearch pre-check)
)

# -----------------------
# App setup
# -----------------------
st.set_page_config(page_title="Genovate: CRISPR Delivery Predictor", layout="centered")
st.title("🧬 Genovate: CRISPR/Cas9 Delivery Predictor")

# Train (mock) model once
_data = load_data()
model, le_mut, le_org, le_method = train_model(_data)

# Sidebar controls
mode = st.sidebar.radio("🔍 Select Mode", ["Simulation", "📘 Learning Mode"])
show_genomic_viewer = st.sidebar.checkbox("🔎 Show Genomic Sequence Viewer")
show_seq_detect = st.sidebar.checkbox("🧪 Experimental: Detect Gene from Sequence")

# -----------------------
# Learning Mode
# -----------------------
if mode == "📘 Learning Mode":
    st.header("📘 Learning Mode: CRISPR Education Hub")
    st.markdown("Welcome to **Learning Mode** – a guide to understanding CRISPR and delivery methods.")

    st.subheader("🔬 CRISPR Basics")
    st.write(learning_mode["CRISPR Basics"])

    st.subheader("⚡ Electroporation")
    st.write(learning_mode["Electroporation"])

    st.subheader("🧪 Lipid Nanoparticles (LNPs)")
    st.write(learning_mode["Lipid Nanoparticles (LNPs)"])

    st.subheader("🌐 External Resources")
    for label, url in learning_mode["External Resources"].items():
        st.markdown(f"- [{label}]({url})")

# -----------------------
# Simulation Mode
# -----------------------
if mode == "Simulation":
    st.markdown("""
    Welcome to **Genovate**, a predictive simulation tool to identify the optimal CRISPR delivery method 
    for treating gene mutations like **PKD1**, **PKD2**, and **PKHD1**.
    """)

    # Inputs
    st.header("1️⃣ Input Your Case")
    organ_gene_map = {
        "Kidney": ["PKD1", "PKD2", "PKHD1"],
        "Liver": ["ATP7B", "FAH", "TTR"],
        "Heart": ["MYBPC3", "TNNT2", "MYH7"],
        "Lung": ["CFTR", "AATD"],
        "Brain": ["HTT", "MECP2", "SCN1A"],
        "Eye": ["RPE65", "RPGR"],
        "Pancreas": ["INS", "PDX1"],
    }

    organ = st.selectbox("Select Target Organ:", list(organ_gene_map.keys()))
    mutation = st.selectbox("Select Gene Mutation:", organ_gene_map[organ])
    therapy_type = st.radio("Therapy Type:", ["Ex vivo", "In vivo"])

    st.subheader("Clinical Parameters")
    eff = st.slider("Estimated Editing Efficiency (%)", 60, 100, 75) / 100.0
    off = st.slider("Estimated Off-target Risk (%)", 0, 20, 9) / 100.0
    viability = st.slider("Cell Viability Post-Delivery (%)", 50, 100, 90) / 100.0
    cost = st.select_slider("Cost & Scalability (1=Low Cost, 5=High Cost)",
                            options=[1, 2, 3, 4, 5], value=3)

    # Gene diagram + summary
    st.subheader("🔬 Gene Structure and Summary")
    c1, c2 = st.columns([1, 2])

    with c1:
        img_path = get_gene_image_path(mutation)
        if os.path.exists(img_path):
            st.image(img_path,
                     caption=f"Gene schematic for {mutation} – mutation hotspots highlighted.",
                     use_container_width=True)
            st.caption("ℹ️ Diagram shows functional domains, exons, and common mutation sites.")
        else:
            st.warning("⚠️ No image available for this gene yet.")

    with c2:
        st.markdown(f"**🧠 {mutation} Summary:**")
        st.info(get_mutation_summary(mutation))

    # Predict
    if st.button("🔍 Predict Best Delivery Method"):
        rec = predict_method(model, le_mut, le_org, le_method,
                             mutation, organ, eff, off, viability, cost)
        conf = predict_confidence(model, le_mut, le_org, le_method,
                                  mutation, organ, eff, off, viability, cost, rec)

        st.success(f"🚀 Recommended Delivery Method: **{rec}**")
        st.metric("Model Confidence", f"{conf:.1f}%")
        st.progress(min(max(conf / 100.0, 0.0), 1.0))

        # Radar (Spider) chart
        st.subheader("📊 Comparison Radar Chart")
        categories = ["Efficiency", "Off-Target Risk", "Viability"]
        N = len(categories)

        if rec == "LNP":
            method_scores = [eff, off, viability]
            baseline = [0.85, 0.12, 0.75]
            labels = ["LNP (Input)", "Electroporation (Baseline)"]
        else:
            method_scores = [0.72, 0.07, 0.92]
            baseline = [eff, off, viability]
            labels = ["LNP (Baseline)", "Electroporation (Input)"]

        vals_1 = method_scores + [method_scores[0]]
        vals_2 = baseline + [baseline[0]]
        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.set_theta_offset(pi / 2)
        ax.set_theta_direction(-1)
        plt.xticks(angles[:-1], categories)

        ax.plot(angles, vals_1, linewidth=2, linestyle="solid", label=labels[0])
        ax.fill(angles, vals_1, alpha=0.25)

        ax.plot(angles, vals_2, linewidth=2, linestyle="solid", label=labels[1])
        ax.fill(angles, vals_2, alpha=0.25)

        ax.set_ylim(0, 1)
        plt.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))
        radar_path = "radar_chart.png"
        fig.savefig(radar_path, dpi=150, bbox_inches="tight")
        st.pyplot(fig)

        # PDF download
        st.subheader("📄 Download Summary Report")
        inputs = {
            "Target Organ": organ,
            "Gene Mutation": mutation,
            "Therapy Type": therapy_type,
            "Efficiency": f"{eff*100:.1f}%",
            "Off-Target Risk": f"{off*100:.1f}%",
            "Viability": f"{viability*100:.1f}%",
            "Cost": cost,
            "Recommended Method": rec,
            "Confidence": f"{conf:.1f}%",
        }
        pdf_path = "Genovate_Report.pdf"
        generate_pdf_report(inputs, get_mutation_summary(mutation), radar_path, pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name="Genovate_Report.pdf", mime="application/pdf")

    # PAM finder
    st.header("🧬 Optional: Find PAM Sequences")
    dna_input = st.text_area("Enter a DNA sequence (A/C/G/T only):",
                             "AGGTCGTTACCGGTAGCGGTACCGTAGGGTAGGCTAGGGTACCGGTAG")
    if st.button("🔎 Find PAM Sites"):
        sites = find_pam_sites(dna_input.upper())
        if sites:
            st.success(f"✅ Found {len(sites)} PAM site(s). First 10:")
            st.write(sites[:10])
        else:
            st.warning("❌ No PAM sites (NGG) found in the input sequence.")

# -----------------------
# Genomic Sequence Viewer
# -----------------------
if show_genomic_viewer:
    st.header("🧬 Genomic Sequence Viewer (with PAM highlights)")
    st.write("Paste or pick an accession to view the first ~200 bases with **PAM (NGG)** sites highlighted.")

    common_genes = {
        "PKD1 (Polycystic Kidney Disease)": "NM_001009944.3",  # PKD1 isoform 1 (human) – robust record
        "CFTR (Cystic Fibrosis)": "NM_000492.4",
        "BRCA1 (Breast Cancer)": "NM_007294.4",
        "HTT (Huntington's)": "NM_002111.8",
        "TP53 (Tumor Suppressor)": "NM_000546.6",
        "Custom": "",
    }

    sel = st.selectbox("🔎 Select a Gene or Choose Custom:", list(common_genes.keys()))
    acc = st.text_input("Enter NCBI Accession ID",
                        value=common_genes[sel] if sel != "Custom" else "")

    if acc:
        try:
            record = fetch_genbank_record(acc)
            gene_name = getattr(record, "name", "N/A")
            organism = record.annotations.get("organism", "Unknown organism")

            st.markdown(f"**🧬 Gene:** `{gene_name}`")
            st.markdown(f"**🌱 Organism:** `{organism}`")

            raw_seq = str(record.seq)[:200]
            highlighted = highlight_pam_sites(raw_seq)
            st.markdown(
                f"<div style='font-family: monospace; word-wrap: break-word;'>{highlighted}</div>",
                unsafe_allow_html=True,
            )
            st.caption(f"🔴 Highlighted = PAM Sites (NGG) • Accession ID: {acc}")
        except Exception as e:
            st.error(f"❌ Error fetching sequence: {e}")

# -----------------------
# Experimental BLAST: detect gene from sequence
# -----------------------
if show_seq_detect:
    st.header("🧪 Experimental: Detect Gene from Sequence")
    st.write("Paste a **DNA sequence (≥120 bp)** to auto-detect top matches via **NCBI BLAST** "
             "(biased to *Homo sapiens* for speed).")

    seq_in = st.text_area("Paste DNA sequence to auto-detect gene:", height=140)
    if st.button("🧬 Run Gene Detection"):
        if seq_in and len(seq_in.strip()) >= 1:
            with st.spinner("Running BLAST (may take ~10–30s)…"):
                matches = detect_gene_from_sequence(seq_in)
            # Show up to 3 results or any error strings
            ok = any(not m.startswith("❌") for m in matches)
            (st.success if ok else st.error)("🎯 Match Results:" if ok else "No high-confidence match.")
            for m in matches:
                st.code(m)
            st.caption("Tip: use ≥200 bp, only A/C/G/T (N allowed). For non-human genes, remove the organism bias in backend.")
        else:
            st.warning("Please paste a valid DNA sequence (A/C/G/T).")

# Footer
st.markdown("---")
st.caption("Developed by Raksheet Gummakonda for Genovate")
