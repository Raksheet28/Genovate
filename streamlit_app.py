import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import os
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
    detect_gene_from_sequence
)

# Load model
data = load_data()
model, le_mut, le_org, le_method = train_model(data)

# UI
st.set_page_config(page_title="Genovate", layout="centered")
st.title("🧬 Genovate: CRISPR/Cas9 Delivery Predictor")

# Sidebar for mode selection
mode = st.sidebar.radio("🔍 Select Mode", ["Simulation", "📘 Learning Mode"])

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

else:
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
        "Pancreas": ["INS", "PDX1"]
    }

    organ = st.selectbox("Select Target Organ:", list(organ_gene_map.keys()))
    mutation = st.selectbox("Select Gene Mutation:", organ_gene_map[organ])
    therapy_type = st.radio("Therapy Type:", ["Ex vivo", "In vivo"])

    st.subheader("Clinical Parameters")
    eff = st.slider("Estimated Editing Efficiency (%)", 60, 100, 75) / 100.0
    off = st.slider("Estimated Off-target Risk (%)", 0, 20, 9) / 100.0
    viability = st.slider("Cell Viability Post-Delivery (%)", 50, 100, 90) / 100.0
    cost = st.select_slider("Cost & Scalability (1=Low Cost, 5=High Cost)", options=[1, 2, 3, 4, 5], value=3)

    # Image + Summary
    st.subheader("🔬 Gene Structure and Summary")
    col1, col2 = st.columns([1, 2])

    with col1:
        img_path = get_gene_image_path(mutation)
        if os.path.exists(img_path):
            st.image(img_path, caption=f"Gene schematic for {mutation} – Mutation hotspots highlighted.", use_container_width=True)
            st.caption("ℹ️ This diagram shows functional domains and known mutation sites.")
        else:
            st.warning("⚠️ No image available for this mutation.")

    with col2:
        st.markdown(f"**🧠 {mutation} Summary:**")
        st.info(get_mutation_summary(mutation))

    # Predict Button
    if st.button("🔍 Predict Best Delivery Method"):
        recommendation = predict_method(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost)
        confidence = predict_confidence(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost, recommendation)

        st.success(f"🚀 Recommended Delivery Method: **{recommendation}**")
        st.metric("Model Confidence", f"{confidence:.1f}%")
        st.progress(confidence / 100.0)

        # Radar chart
        st.subheader("📊 Comparison Radar Chart")
        categories = ['Efficiency', 'Off-Target Risk', 'Viability']
        N = len(categories)

        if recommendation == "LNP":
            method_scores = [eff, off, viability]
            alt_scores = [0.85, 0.12, 0.75]
            labels = ['LNP (Input)', 'Electroporation (Baseline)']
        else:
            method_scores = [0.72, 0.07, 0.92]
            alt_scores = [eff, off, viability]
            labels = ['LNP (Baseline)', 'Electroporation (Input)']

        values_1 = method_scores + [method_scores[0]]
        values_2 = alt_scores + [alt_scores[0]]

        angles = [n / float(N) * 2 * pi for n in range(N)]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.set_theta_offset(pi / 2)
        ax.set_theta_direction(-1)
        plt.xticks(angles[:-1], categories)

        ax.plot(angles, values_1, linewidth=2, linestyle='solid', label=labels[0])
        ax.fill(angles, values_1, alpha=0.25)

        ax.plot(angles, values_2, linewidth=2, linestyle='solid', label=labels[1])
        ax.fill(angles, values_2, alpha=0.25)

        ax.set_ylim(0, 1)
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

        radar_path = "radar_chart.png"
        fig.savefig(radar_path)
        st.pyplot(fig)

        # PDF download
        st.subheader("📄 Download Summary Report")
        mutation_summary = get_mutation_summary(mutation)
        inputs = {
            "Target Organ": organ,
            "Gene Mutation": mutation,
            "Therapy Type": therapy_type,
            "Efficiency": f"{eff*100:.1f}%",
            "Off-Target Risk": f"{off*100:.1f}%",
            "Viability": f"{viability*100:.1f}%",
            "Cost": cost,
            "Recommended Method": recommendation,
            "Confidence": f"{confidence:.1f}%"
        }
        output_path = "Genovate_Report.pdf"
        generate_pdf_report(inputs, mutation_summary, radar_path, output_path)

        with open(output_path, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name="Genovate_Report.pdf", mime="application/pdf")

    # PAM
    st.header("🧬 Optional: Find PAM Sequences")
    dna_input = st.text_area("Enter a DNA sequence:", "AGGTCGTTACCGGTAGCGGTACCGTAGGGTAGGCTAGGGTACCGGTAG")
    if st.button("🔎 Find PAM Sites"):
        pam_sites = find_pam_sites(dna_input.upper())
        if pam_sites:
            st.success(f"✅ Found {len(pam_sites)} PAM site(s). First 10:")
            st.write(pam_sites[:10])
        else:
            st.warning("❌ No PAM sites (NGG) found in the input.")

 # Optional: Genomic Viewer with PAM Highlighting (Enhanced)
if st.sidebar.checkbox("🧬 Show Genomic Sequence"):
    st.subheader("Genomic Sequence (First ~200 bases with PAM sites)")

    # Dropdown of common genes + custom option
    common_genes = {
        "PKD1 (Polycystic Kidney Disease)": "NM_000296.4",
        "CFTR (Cystic Fibrosis)": "NM_000492.4",
        "BRCA1 (Breast Cancer)": "NM_007294.4",
        "HTT (Huntington's)": "NM_002111.8",
        "TP53 (Tumor Suppressor)": "NM_000546.6",
        "Custom": ""
    }

    selected_gene = st.selectbox("🔎 Select a Gene or Choose Custom:", list(common_genes.keys()))
    accession_id = st.text_input("Enter NCBI Accession ID", value=common_genes[selected_gene] if selected_gene != "Custom" else "")

    if accession_id:
        try:
            record = fetch_genbank_record(accession_id)

            if record is None or not record.annotations:
                st.error("❌ Invalid Accession ID or no data found. Please try a different one.")
            else:
                # Extract basic info
                gene_name = record.name if hasattr(record, "name") else "N/A"
                organism = record.annotations.get("organism", "Unknown Organism")

                raw_sequence = str(record.seq)[:200]
                highlighted = highlight_pam_sites(raw_sequence)

                # Display details
                st.markdown(f"**🧬 Gene:** `{gene_name}`")
                st.markdown(f"**🌱 Organism:** `{organism}`")

                st.markdown("<div style='font-family: monospace; word-wrap: break-word;'>"
                            f"{highlighted}</div>", unsafe_allow_html=True)
                st.caption(f"🔴 Highlighted = PAM Sites (NGG) | Accession ID: {accession_id}")

        except Exception as e:
            st.error(f"❌ Error fetching sequence: {e}")

       # 🧬 Optional: Detect Gene from Input DNA Sequence (Advanced)
st.header("🧬 Experimental: Detect Gene from Sequence")

detect_sequence = st.text_area("Paste a DNA sequence to auto-detect gene:")

if st.button("🧬 Run Gene Detection"):
    if detect_sequence.strip():  # Check if input is not empty
        with st.spinner("Running BLAST to detect gene..."):
            gene_info = detect_gene_from_sequence(detect_sequence)
            st.success("🎯 Match Found:")
            st.code(gene_info)
    else:
        st.warning("⚠️ Please paste a valid DNA sequence to detect the gene.")

    # Footer
    st.markdown("---")
    st.caption("Developed by Raksheet Gummakonda for Genovate")
