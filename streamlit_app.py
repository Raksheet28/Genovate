# streamlit_app.py

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from math import pi
import os
from genovate_backend import load_data, train_model, predict_method, find_pam_sites, get_mutation_summary, get_gene_image_path

# Load and train model
data = load_data()
model, le_mut, le_org, le_method = train_model(data)

# Streamlit app setup
st.set_page_config(page_title="Genovate: CRISPR Delivery Predictor", layout="centered")
st.title("🧬 Genovate: CRISPR/Cas9 Delivery Simulation")
st.markdown("""
Welcome to **Genovate**, a predictive simulation tool to identify the optimal CRISPR delivery method 
for treating gene mutations like **PKD1**, **PKD2**, and **PKHD1**.
""")

# Input section
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

# Display mutation summary and image
st.header("🧬 Mutation Details")
col1, col2 = st.columns([2, 3])
with col1:
    summary = get_mutation_summary(mutation)
    st.markdown(f"**Mutation Summary:**\n\n{summary}")
with col2:
    img_path = get_gene_image_path(mutation)
    if os.path.exists(img_path):
        st.image(img_path, caption=f"📍 Gene schematic for {mutation} — domains and mutation hotspots.", use_column_width=True)
        st.caption("ℹ️ This diagram shows functional domains and known mutation sites for the selected gene.")
    else:
        st.warning("No image available for this mutation.")

st.header("📋 Clinical Parameters")
eff = st.slider("Estimated Editing Efficiency (%)", 60, 100, 75) / 100.0
off = st.slider("Estimated Off-target Risk (%)", 0, 20, 9) / 100.0
viability = st.slider("Cell Viability Post-Delivery (%)", 50, 100, 90) / 100.0
cost = st.select_slider("Cost & Scalability (1=Low Cost, 5=High Cost)", options=[1, 2, 3, 4, 5], value=3)

if st.button("🔍 Predict Best Delivery Method"):
    recommendation = predict_method(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost)
    st.success(f"🚀 Recommended Delivery Method: **{recommendation}**")

    # Radar chart for comparison
    st.subheader("📊 Comparison Radar Chart")

    categories = ['Efficiency', 'Off-Target Risk', 'Viability']
    N = len(categories)

    # Mock baseline values
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
    st.pyplot(fig)

# PAM Finder
st.header("🧬 Optional: Find PAM Sequences in Your DNA")
dna_input = st.text_area("Enter a DNA sequence (use only A, T, G, C):", "AGGTCGTTACCGGTAGCGGTACCGTAGGGTAGGCTAGGGTACCGGTAG")
if st.button("🔎 Find PAM Sites"):
    pam_sites = find_pam_sites(dna_input.upper())
    if pam_sites:
        st.success(f"✅ Found {len(pam_sites)} PAM site(s). First 10:")
        st.write(pam_sites[:10])
    else:
        st.warning("❌ No PAM sites (NGG) found in the input sequence.")

# Footer
st.markdown("---")
st.caption("Developed by Raksheet Gummakonda for Genovate")
