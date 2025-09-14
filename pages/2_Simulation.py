import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from math import pi

from genovate_backend import (
    load_data, train_model, predict_method, predict_confidence,
    get_gene_image_path, get_mutation_summary, generate_pdf_report
)

st.set_page_config(page_title="Genovate • Simulation", page_icon="🧪", layout="wide")
st.page_link("streamlit_app.py", label="🏠 Home")

st.markdown("""
<style>
.block-container {padding-top: 0.8rem;}
.stButton>button, .stDownloadButton>button {background-color:#2e86de;color:white;border-radius:8px;}
.badge {display:inline-block;padding:0.25rem 0.5rem;border-radius:6px;font-size:0.8rem;font-weight:600;}
.badge-heur {background:#0b7285;color:#fff;border:1px solid #0c8599;}
.codebox {font-family: ui-monospace, Menlo, Consolas, monospace;}
</style>
""", unsafe_allow_html=True)

# --- helpers ---
def render_confidence_card(conf: float):
    if conf >= 85:
        bg, label, border = "#155d27", "High ✅", "#1f7a3a"
    elif conf >= 70:
        bg, label, border = "#b58100", "Good ☑️", "#d69e2e"
    elif conf >= 50:
        bg, label, border = "#b45309", "Moderate ⚠️", "#ea580c"
    else:
        bg, label, border = "#7f1d1d", "Low ❗", "#991b1b"
    st.markdown(f"""
    <div style="padding:0.6rem 0.8rem;border-radius:8px;background-color:{bg};
    color:white;font-weight:600;text-align:center;border:1px solid {border};letter-spacing:0.2px;">
    Model Confidence: {conf:.1f}% • {label}
    </div>""", unsafe_allow_html=True)

# --- sidebar settings ---
st.sidebar.markdown("### ⚙️ Settings")
show_confidence_bar = st.sidebar.checkbox("Show confidence progress bar", value=True)
show_pdf_download = st.sidebar.checkbox("Enable PDF download", value=True)
show_advanced = st.sidebar.checkbox("Show advanced controls", value=False)

# --- title ---
st.title("🎯 Simulation")
st.caption("Predict the best CRISPR delivery method and export a PDF summary.")

# Train once (mock data)
_data = load_data()
model, le_mut, le_org, le_method = train_model(_data)

left, right = st.columns([1.05, 1.0])

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

        st.subheader("Clinical Parameters")
        c1, c2 = st.columns(2)
        with c1:
            eff = st.slider("Editing Efficiency (%)", 60, 100, 75) / 100.0
            off = st.slider("Off-target Risk (%)", 0, 20, 9) / 100.0
        with c2:
            viability = st.slider("Cell Viability (%)", 50, 100, 90) / 100.0
            cost = st.select_slider("Cost & Scalability (1=Low Cost, 5=High Cost)", [1,2,3,4,5], value=3)

        if show_advanced:
            st.subheader("Advanced Controls")
            ac1, ac2 = st.columns(2)
            with ac1:
                nuclease = st.selectbox("Nuclease (for report only)", ["SpCas9","SaCas9","AsCas12a","LbCas12a"])
                show_probs = st.checkbox("Show model class probabilities", value=True)
                use_heuristic = st.checkbox("Use weighted heuristic (experimental)", value=False)
            with ac2:
                st.caption("Heuristic weights (used only when enabled):")
                w_eff = st.slider("Weight: Efficiency", 0.0, 1.0, 0.5, 0.05)
                w_off = st.slider("Weight: Off-target (lower is better)", 0.0, 1.0, 0.3, 0.05)
                w_via = st.slider("Weight: Viability", 0.0, 1.0, 0.2, 0.05)
                blend_alpha = st.slider("Blend profiles with your inputs", 0.0, 1.0, 0.35, 0.05)

        submitted = st.form_submit_button("🔍 Predict Best Delivery Method", use_container_width=True)

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

    # Profiles
    method_profiles = {
        "LNP": {"eff": 0.72, "off": 0.07, "via": 0.92},
        "Electroporation": {"eff": 0.85, "off": 0.12, "via": 0.75},
    }

    if submitted:
        if show_advanced and 'use_heuristic' in locals() and use_heuristic:
            def score_method(p, we, wo, wv):
                return we*p["eff"] + wo*(1.0 - p["off"]) + wv*p["via"]
            def blend(p, ei, oi, vi, a):
                return {"eff": (1-a)*p["eff"] + a*ei, "off": (1-a)*p["off"] + a*oi, "via": (1-a)*p["via"] + a*vi}

            p_lnp  = blend(method_profiles["LNP"], eff, off, viability, blend_alpha)
            p_elec = blend(method_profiles["Electroporation"], eff, off, viability, blend_alpha)
            s_lnp, s_elec = score_method(p_lnp, w_eff, w_off, w_via), score_method(p_elec, w_eff, w_off, w_via)
            rec = "LNP" if s_lnp >= s_elec else "Electroporation"
            scores = np.array([s_lnp, s_elec]); scores -= scores.max()
            probs = np.exp(scores) / np.exp(scores).sum()
            conf = float(100.0 * (probs[0] if rec == "LNP" else probs[1]))
            st.markdown('<span class="badge badge-heur">Heuristic mode (blended)</span>', unsafe_allow_html=True)
            if show_probs:
                st.caption("Blended profiles & heuristic scores:")
                st.dataframe(pd.DataFrame([
                    {"Method":"LNP", "eff":round(p_lnp["eff"],3), "off":round(p_lnp["off"],3), "via":round(p_lnp["via"],3), "Score":round(s_lnp,4)},
                    {"Method":"Electroporation", "eff":round(p_elec["eff"],3), "off":round(p_elec["off"],3), "via":round(p_elec["via"],3), "Score":round(s_elec,4)}
                ]), use_container_width=True)
            radar_vals_1 = [p_lnp["eff"], p_lnp["off"], p_lnp["via"]]
            radar_vals_2 = [p_elec["eff"], p_elec["off"], p_elec["via"]]
            radar_labels = ["LNP (blended)", "Electroporation (blended)"]
        else:
            rec = predict_method(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost)
            conf = predict_confidence(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost, rec)
            if show_advanced and 'show_probs' in locals() and show_probs:
                feat = np.array([[le_mut.transform([mutation])[0], le_org.transform([organ])[0], eff, off, viability, cost]])
                proba = model.predict_proba(feat)[0]
                labels = le_method.inverse_transform(np.arange(len(proba)))
                st.dataframe(pd.DataFrame({"Method": labels, "Probability (%)": (proba*100).round(2)}), use_container_width=True)
            if rec == "LNP":
                method_scores = [eff, off, viability]
                baseline = [0.85, 0.12, 0.75]
                radar_labels = ["LNP (Input)", "Electroporation (Baseline)"]
            else:
                method_scores = [0.72, 0.07, 0.92]
                baseline = [eff, off, viability]
                radar_labels = ["LNP (Baseline)", "Electroporation (Input)"]
            radar_vals_1, radar_vals_2 = method_scores, baseline

        # KPI
        k1, k2 = st.columns(2)
        with k1: st.success(f"**Recommended Method:** {rec}")
        with k2: render_confidence_card(conf)
        if show_confidence_bar: st.progress(min(max(conf/100.0, 0.0), 1.0))

        # Radar
        st.markdown("### Comparison (Radar Chart)")
        cats = ["Efficiency", "Off-Target Risk", "Viability"]
        N = len(cats)
        angles = [n/float(N)*2*pi for n in range(N)] + [0]
        v1 = radar_vals_1 + [radar_vals_1[0]]
        v2 = radar_vals_2 + [radar_vals_2[0]]
        fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
        ax.set_theta_offset(pi/2); ax.set_theta_direction(-1)
        plt.xticks(angles[:-1], cats)
        ax.plot(angles, v1, linewidth=2, linestyle="solid", label=radar_labels[0]); ax.fill(angles, v1, alpha=0.25)
        ax.plot(angles, v2, linewidth=2, linestyle="solid", label=radar_labels[1]); ax.fill(angles, v2, alpha=0.25)
        ax.set_ylim(0,1); plt.legend(loc="upper right", bbox_to_anchor=(0.1,0.1))
        radar_path = "radar_chart.png"; fig.savefig(radar_path, dpi=150, bbox_inches="tight"); st.pyplot(fig)

        # Generate PDF bytes and persist
        if show_pdf_download:
            inputs = {
                "Target Organ": organ, "Gene Mutation": mutation, "Therapy Type": therapy_type,
                "Efficiency": f"{eff*100:.1f}%", "Off-Target Risk": f"{off*100:.1f}%",
                "Viability": f"{viability*100:.1f}%", "Cost": cost,
                "Recommended Method": rec, "Confidence": f"{conf:.1f}%"
            }
            if show_advanced:
                inputs["Nuclease"] = (locals().get("nuclease") or "SpCas9")
                if locals().get("use_heuristic"): 
                    inputs["Decision Mode"] = "Heuristic (blended)"
                    inputs["Weights"] = f"eff={w_eff:.2f}, off={w_off:.2f}, via={w_via:.2f}"
                    inputs["Blend α"] = f"{blend_alpha:.2f}"
                else:
                    inputs["Decision Mode"] = "Model"
            pdf_bytes = generate_pdf_report(inputs, get_mutation_summary(mutation), radar_path, output_path=None)
            st.session_state["pdf_bytes"] = pdf_bytes
            st.session_state["pdf_name"] = "Genovate_Report.pdf"
            st.success("Report generated. Scroll down to download ⬇️")

# Persistent download area
if show_pdf_download and "pdf_bytes" in st.session_state:
    st.markdown("### 📄 Download Summary Report")
    st.download_button("📥 Download PDF",
        data=st.session_state["pdf_bytes"],
        file_name=st.session_state.get("pdf_name","Genovate_Report.pdf"),
        mime="application/pdf",
        use_container_width=True,
        key="download_report_btn")
