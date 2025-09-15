# pages/2_Simulation.py
import os
from math import pi

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from genovate_backend import (
    load_data, train_model,
    predict_method, predict_confidence,
    get_gene_image_path, get_mutation_summary,
    generate_pdf_report,  # returns bytes
    find_pam_sites,
)

# ---------- Page config ----------
st.set_page_config(page_title="Genovate • Simulation", page_icon="🎯", layout="wide")

# ---------- CSS ----------
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #0b0f14 0%, #0b0f14 100%); color: #e8eaf0; }
.card { background:#101621;border:1px solid #1e2a3a;border-radius:12px;padding:1rem; }
.stButton>button, .stDownloadButton>button {
  background:#6e56cf;color:white;border:none;border-radius:10px;padding:.6rem 1rem;
  font-weight:600; box-shadow:0 0 18px #6e56cf55, inset 0 0 8px #8f7bf5aa;
}
.badge {display:inline-block;padding:.2rem .5rem;border-radius:6px;font-size:.82rem;font-weight:600;}
.badge-heur {background:#0b7285;color:#fff;border:1px solid #0c8599;}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar Nav ----------
st.sidebar.page_link("pages/1_Home.py", label="🏠 Home")
st.sidebar.page_link("pages/2_Simulation.py", label="🎯 Simulation")
st.sidebar.page_link("pages/3_Gene_Detection.py", label="🧪 Gene Detection")
st.sidebar.page_link("pages/4_Sequence_Viewer.py", label="🧬 Sequence Viewer")
st.sidebar.page_link("pages/5_Learning_Mode.py", label="📘 Learning Mode")

# ========= UI helper =========
def render_confidence_card(conf: float):
    if conf >= 85:
        bg, label, border = "#155d27", "High ✅", "#1f7a3a"
    elif conf >= 70:
        bg, label, border = "#b58100", "Good ☑️", "#d69e2e"
    elif conf >= 50:
        bg, label, border = "#b45309", "Moderate ⚠️", "#ea580c"
    else:
        bg, label, border = "#7f1d1d", "Low ❗", "#991b1b"
    st.markdown(
        f"""
        <div style="padding:.6rem .8rem;border-radius:8px;background:{bg};
        color:white;font-weight:600;text-align:center;border:1px solid {border};">
            Model Confidence: {conf:.1f}% • {label}
        </div>
        """, unsafe_allow_html=True
    )

st.title("🎯 Simulation")

# Train once on mock data
_data = load_data()
model, le_mut, le_org, le_method = train_model(_data)

left, right = st.columns([1.05, 1.0])

# ---------- LEFT: inputs (form) ----------
with left:
    with st.form("sim_form"):
        st.subheader("Case Setup")
        organ_gene_map = {
            "Kidney": ["PKD1", "PKD2", "PKHD1"],
            "Liver": ["ATP7B", "FAH", "TTR"],
            "Heart": ["MYBPC3", "TNNT2", "MYH7"],
            "Lung": ["CFTR", "AATD"],
            "Brain": ["HTT", "MECP2", "SCN1A"],
            "Eye": ["RPE65", "RPGR"],
            "Pancreas": ["INS", "PDX1"],
        }
        organ = st.selectbox("Target Organ", list(organ_gene_map.keys()))
        mutation = st.selectbox("Gene Mutation", organ_gene_map[organ])
        therapy_type = st.radio("Therapy Type", ["Ex vivo", "In vivo"], horizontal=True)

        st.write("")
        st.subheader("Clinical Parameters")
        c1, c2 = st.columns(2)
        with c1:
            eff = st.slider("Editing Efficiency (%)", 60, 100, 75) / 100.0
            off = st.slider("Off-target Risk (%)", 0, 20, 9) / 100.0
        with c2:
            viability = st.slider("Cell Viability (%)", 50, 100, 90) / 100.0
            cost = st.select_slider("Cost & Scalability (1=Low Cost, 5=High Cost)", [1, 2, 3, 4, 5], value=3)

        # Advanced Controls
        show_advanced = st.checkbox("Show advanced controls", value=False)
        if show_advanced:
            st.subheader("Advanced Controls")
            ac1, ac2 = st.columns(2)
            with ac1:
                nuclease = st.selectbox("Nuclease (for report only)", ["SpCas9", "SaCas9", "AsCas12a", "LbCas12a"])
                show_probs = st.checkbox("Show raw model class probabilities", value=True)
                use_heuristic = st.checkbox("Use weighted heuristic instead of model", value=False)
            with ac2:
                st.caption("Weights used when heuristic is enabled:")
                w_eff = st.slider("Weight: Efficiency", 0.0, 1.0, 0.5, 0.05)
                w_off = st.slider("Weight: Off-target (lower is better)", 0.0, 1.0, 0.3, 0.05)
                w_via = st.slider("Weight: Viability", 0.0, 1.0, 0.2, 0.05)
                blend_alpha = st.slider("Blend (0=profiles, 1=your inputs)", 0.0, 1.0, 0.35, 0.05)

        submitted = st.form_submit_button("🔍 Predict Best Delivery Method", use_container_width=True)

# ---------- RIGHT: outputs ----------
with right:
    st.subheader("Gene Context")
    g1, g2 = st.columns([1, 1.6])
    with g1:
        img_path = get_gene_image_path(mutation)
        if os.path.exists(img_path):
            st.image(img_path, caption=f"{mutation} schematic", use_container_width=True)
        else:
            st.info("No gene schematic available yet.")
    with g2:
        st.markdown(f"**{mutation} – Summary**")
        st.info(get_mutation_summary(mutation))

    # Base method profiles
    method_profiles = {
        "LNP": {"eff": 0.72, "off": 0.07, "via": 0.92},
        "Electroporation": {"eff": 0.85, "off": 0.12, "via": 0.75},
    }

    if submitted:
        # Heuristic path
        if ('show_advanced' in locals()) and show_advanced and ('use_heuristic' in locals()) and use_heuristic:
            def score_method(profile, w_eff, w_off, w_via):
                return w_eff * profile["eff"] + w_off * (1.0 - profile["off"]) + w_via * profile["via"]

            def blend_profile(profile, eff_in, off_in, via_in, alpha):
                return {
                    "eff": (1 - alpha) * profile["eff"] + alpha * eff_in,
                    "off": (1 - alpha) * profile["off"] + alpha * off_in,
                    "via": (1 - alpha) * profile["via"] + alpha * via_in,
                }

            p_lnp  = blend_profile(method_profiles["LNP"], eff, off, viability, blend_alpha)
            p_elec = blend_profile(method_profiles["Electroporation"], eff, off, viability, blend_alpha)
            score_lnp  = score_method(p_lnp,  w_eff, w_off, w_via)
            score_elec = score_method(p_elec, w_eff, w_off, w_via)
            rec = "LNP" if score_lnp >= score_elec else "Electroporation"

            # softmax for confidence
            scores = np.array([score_lnp, score_elec])
            scores = scores - scores.max()
            probs = np.exp(scores) / np.exp(scores).sum()
            conf = float(100.0 * (probs[0] if rec == "LNP" else probs[1]))

            st.markdown('<span class="badge badge-heur">Heuristic mode (blended)</span>', unsafe_allow_html=True)

            if ('show_probs' in locals()) and show_probs:
                st.caption("Blended profiles and scores:")
                st.dataframe(pd.DataFrame([
                    {"Method": "LNP", "eff": round(p_lnp["eff"], 3), "off": round(p_lnp["off"], 3),
                     "via": round(p_lnp["via"], 3), "Weighted Score": round(score_lnp, 4)},
                    {"Method": "Electroporation", "eff": round(p_elec["eff"], 3), "off": round(p_elec["off"], 3),
                     "via": round(p_elec["via"], 3), "Weighted Score": round(score_elec, 4)},
                ]), use_container_width=True)

            radar_vals_1 = [p_lnp["eff"], p_lnp["off"], p_lnp["via"]]
            radar_vals_2 = [p_elec["eff"], p_elec["off"], p_elec["via"]]
            radar_labels = ["LNP (blended)", "Electroporation (blended)"]

        # Model path
        else:
            rec = predict_method(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost)
            conf = predict_confidence(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost, rec)

            if ('show_advanced' in locals()) and show_advanced and ('show_probs' in locals()) and show_probs:
                feat = np.array([[le_mut.transform([mutation])[0],
                                  le_org.transform([organ])[0],
                                  eff, off, viability, cost]])
                proba = model.predict_proba(feat)[0]
                labels = le_method.inverse_transform(np.arange(len(proba)))
                st.markdown("**Model class probabilities**")
                st.dataframe(pd.DataFrame({"Method": labels, "Probability (%)": (proba * 100).round(2)}),
                             use_container_width=True)

            if rec == "LNP":
                method_scores = [eff, off, viability]
                baseline = [0.85, 0.12, 0.75]
                radar_labels = ["LNP (Input)", "Electroporation (Baseline)"]
            else:
                method_scores = [0.72, 0.07, 0.92]
                baseline = [eff, off, viability]
                radar_labels = ["LNP (Baseline)", "Electroporation (Input)"]
            radar_vals_1 = method_scores
            radar_vals_2 = baseline

        # KPI
        k1, k2 = st.columns(2)
        with k1: st.success(f"**Recommended Method:** {rec}")
        with k2: render_confidence_card(conf)

        st.progress(min(max(conf / 100.0, 0.0), 1.0))

        # Radar
        st.markdown("### Comparison (Radar Chart)")
        categories = ["Efficiency", "Off-Target Risk", "Viability"]
        N = len(categories)
        angles = [n / float(N) * 2 * pi for n in range(N)] + [0]

        vals_1 = radar_vals_1 + [radar_vals_1[0]]
        vals_2 = radar_vals_2 + [radar_vals_2[0]]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.set_theta_offset(pi / 2)
        ax.set_theta_direction(-1)
        plt.xticks(angles[:-1], categories)
        ax.plot(angles, vals_1, linewidth=2, linestyle="solid", label=radar_labels[0])
        ax.fill(angles, vals_1, alpha=0.25)
        ax.plot(angles, vals_2, linewidth=2, linestyle="solid", label=radar_labels[1])
        ax.fill(angles, vals_2, alpha=0.25)
        ax.set_ylim(0, 1)
        plt.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))

        radar_path = "radar_chart.png"
        fig.savefig(radar_path, dpi=150, bbox_inches="tight")
        st.pyplot(fig)

        # Persist PDF in session_state
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
        if ('show_advanced' in locals()) and show_advanced:
            inputs["Nuclease"] = nuclease if 'nuclease' in locals() else "SpCas9"
            if ('use_heuristic' in locals()) and use_heuristic:
                inputs["Decision Mode"] = "Heuristic (blended)"
                inputs["Weights"] = f"eff={w_eff:.2f}, off={w_off:.2f}, via={w_via:.2f}"
                inputs["Blend α"] = f"{blend_alpha:.2f}"
            else:
                inputs["Decision Mode"] = "Model"

        pdf_bytes = generate_pdf_report(inputs, get_mutation_summary(mutation), radar_path, output_path=None)
        st.session_state["pdf_bytes"] = pdf_bytes
        st.session_state["pdf_name"] = "Genovate_Report.pdf"
        st.success("Report generated. Use the download area below ⬇️")

# Persistent download area (outside form submit so it never vanishes)
st.markdown("---")
st.subheader("📄 Download Summary Report")
if "pdf_bytes" in st.session_state:
    st.download_button(
        "📥 Download PDF",
        data=st.session_state["pdf_bytes"],
        file_name=st.session_state.get("pdf_name", "Genovate_Report.pdf"),
        mime="application/pdf",
        use_container_width=True,
        key="download_report_btn",
    )
else:
    st.info("Run a simulation to enable the download.")
