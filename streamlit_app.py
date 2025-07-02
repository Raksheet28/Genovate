# streamlit_app.py

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from math import pi
from genovate_backend import load_data, train_model, predict_method, find_pam_sites

# Load and train model
data = load_data()
model, le_mut, le_org, le_method = train_model(data)

# Disease summaries (30-word summaries for each mutation)
disease_summaries = {
    "PKD1": "PKD1 mutations cause ADPKD, characterized by progressive kidney cyst formation, hypertension, and renal failure. CRISPR holds promise to disrupt cyst pathways and prevent kidney enlargement.",
    "PKD2": "PKD2 causes a milder form of ADPKD with later-onset symptoms. It encodes a calcium channel; gene therapy may restore signaling and delay kidney cyst development.",
    "PKHD1": "PKHD1 mutations lead to ARPKD, affecting infants and children. It causes enlarged kidneys and liver fibrosis. Editing this gene can improve pediatric outcomes significantly.",
    "ATP7B": "ATP7B mutations cause Wilson’s Disease, a disorder of copper metabolism resulting in liver damage. CRISPR therapy may enable correction to restore copper transport.",
    "FAH": "FAH mutations result in Tyrosinemia Type I, causing liver failure in infants. Gene editing can restore normal enzyme production and prevent toxic metabolite accumulation.",
    "TTR": "TTR mutations lead to hereditary amyloidosis, with abnormal protein deposits in organs. CRISPR therapies aim to reduce TTR protein production to manage symptoms.",
    "MYBPC3": "Mutations in MYBPC3 cause hypertrophic cardiomyopathy, leading to thickened heart walls. CRISPR can potentially correct gene defects to prevent cardiac arrest.",
    "TNNT2": "TNNT2 mutations affect cardiac troponin, disrupting muscle contraction and causing dilated cardiomyopathy. Precision gene editing may help restore normal heart function.",
    "MYH7": "MYH7 gene defects lead to cardiomyopathies with risk of sudden death. Targeted therapies may normalize muscle function and reduce disease severity.",
    "CFTR": "CFTR gene mutations cause Cystic Fibrosis, leading to thick mucus in lungs and pancreas. Gene editing targets correction of defective chloride transport pathways.",
    "AATD": "AATD arises from mutations in SERPINA1, affecting lung and liver function. CRISPR strategies aim to restore alpha-1 antitrypsin production and protect tissues.",
    "HTT": "HTT gene mutations cause Huntington’s disease, leading to neurodegeneration. Editing the expanded CAG repeat may delay or prevent disease progression.",
    "MECP2": "MECP2 mutations result in Rett Syndrome, affecting brain development. Gene therapy aims to restore proper gene regulation in neurons.",
    "SCN1A": "SCN1A mutations lead to Dravet Syndrome, a severe epilepsy disorder. Targeted editing could normalize sodium channel function in neurons.",
    "RPE65": "RPE65 defects cause childhood blindness via retinal dystrophy. CRISPR-based gene replacement has shown success in restoring partial vision.",
    "RPGR": "RPGR mutations result in X-linked retinitis pigmentosa, causing gradual vision loss. Correcting the mutation could delay photoreceptor degeneration.",
    "INS": "INS gene mutations can lead to neonatal diabetes. Gene editing aims to restore insulin production and regulate blood glucose.",
    "PDX1": "PDX1 mutations disrupt pancreatic development and insulin regulation. CRISPR therapy holds promise to reprogram beta cell function."
}

# Streamlit app setup
st.set_page_config(page_title="Genovate: CRISPR Delivery Predictor", layout="centered")
st.title(" Genovate: CRISPR/Cas9 Delivery Simulation")
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

# Show disease summary
if mutation in disease_summaries:
    st.markdown("### 🧾 Disease Summary")
    st.info(disease_summaries[mutation])

therapy_type = st.radio("Therapy Type:", ["Ex vivo", "In vivo"])

st.subheader("Clinical Parameters")
eff = st.slider("Estimated Editing Efficiency (%)", 60, 100, 75) / 100.0
off = st.slider("Estimated Off-target Risk (%)", 0, 20, 9) / 100.0
viability = st.slider("Cell Viability Post-Delivery (%)", 50, 100, 90) / 100.0
cost = st.select_slider("Cost & Scalability (1=Low Cost, 5=High Cost)", options=[1, 2, 3, 4, 5], value=3)

if st.button("🔍 Predict Best Delivery Method"):
    recommendation = predict_method(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost)
    st.success(f" Recommended Delivery Method: **{recommendation}**")

    # Radar chart for comparison
    st.subheader(" Comparison Radar Chart")

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
st.header(" Optional: Find PAM Sequences in Your DNA")
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
