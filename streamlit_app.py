# streamlit_app.py

import os
import numpy as np
import pandas as pd
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
    generate_pdf_report,  # returns BYTES
    learning_mode,
    fetch_genbank_record,
    highlight_pam_sites,
    detect_gene_from_sequence,
)

# ========= UI helper =========
def render_confidence_card(conf: float):
    """Colored KPI-style card for model confidence."""
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
        <div style="
            padding:0.6rem 0.8rem;
            border-radius:8px;
            background-color:{bg};
            color:white;
            font-weight:600;
            text-align:center;
            border:1px solid {border};
            letter-spacing:0.2px;">
            Model Confidence: {conf:.1f}% • {label}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ========= Page setup / CSS =========
st.set_page_config(
    page_title="Genovate • CRISPR Delivery & Gene Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
.block-container {padding-top: 1.0rem; padding-bottom: 1.2rem;}
.stButton>button, .stDownloadButton>button {background-color:#2e86de;color:white;border-radius:8px;}
.kpi {padding:0.6rem 0.8rem;border-radius:8px;background:#f8f9fa;border:1px solid #e9ecef;}
.codebox {font-family: ui-monospace, Menlo, Consolas, monospace;}
.section-divider {margin: 0.6rem 0;}
.smallnote {color:#6c757d;}
.badge {display:inline-block;padding:0.25rem 0.5rem;border-radius:6px;font-size:0.8rem;font-weight:600;}
.badge-heur {background:#0b7285;color:#fff;border:1px solid #0c8599;}
</style>
""",
    unsafe_allow_html=True,
)

# ========= Sidebar =========
if os.path.exists("gene_images/PKD1.png"):
    st.sidebar.image("gene_images/PKD1.png", use_container_width=True)
st.sidebar.markdown("### Genovate")
st.sidebar.caption("CRISPR Delivery Predictor & Gene Analysis")

with st.sidebar.expander("⚙️ Settings", expanded=False):
    show_confidence_bar = st.checkbox("Show confidence progress bar", value=True)
    show_pdf_download = st.checkbox("Enable PDF download", value=True)
    show_advanced = st.checkbox("Show advanced controls", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("**Contact:** support@genovate.app")
st.sidebar.caption("Research prototype — not for clinical use.")

# ========= Title =========
st.title("🧬 Genovate")
st.caption("CRISPR delivery simulation • Genomic sequence viewer • PAM highlighting • Gene detection")

# ========= Cached fetch =========
@st.cache_data(show_spinner=False)
def _cached_fetch(accession: str):
    rec = fetch_genbank_record(accession)
    return {
        "name": getattr(rec, "name", "N/A"),
        "organism": rec.annotations.get("organism", "Unknown organism"),
        "seq": str(rec.seq),
    }

# Ensure session keys exist (prevents KeyError across reruns)
for k, v in [("pdf_bytes", None), ("pdf_name", "Genovate_Report.pdf")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ========= Tabs =========
tab_sim, tab_detect, tab_viewer, tab_learn = st.tabs(
    ["🎯 Simulation", "🧪 Gene Detection", "🧬 Sequence Viewer", "📘 Learning Mode"]
)

# ===========================
# 1) SIMULATION TAB
# ===========================
with tab_sim:
    # Train once on mock data
    _data = load_data()
    model, le_mut, le_org, le_method = train_model(_data)

    left, right = st.columns([1.05, 1.0])

    # ---------- LEFT: inputs (wrapped in a form to prevent flicker) ----------
    with left:
        with st.form("sim_form", clear_on_submit=False):
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

            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.subheader("Clinical Parameters")
            c1, c2 = st.columns(2)
            with c1:
                eff = st.slider("Editing Efficiency (%)", 60, 100, 75) / 100.0
                off = st.slider("Off-target Risk (%)", 0, 20, 9) / 100.0
            with c2:
                viability = st.slider("Cell Viability (%)", 50, 100, 90) / 100.0
                cost = st.select_slider("Cost & Scalability (1=Low Cost, 5=High Cost)", [1, 2, 3, 4, 5], value=3)

            # Advanced Controls
            if show_advanced:
                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                st.subheader("Advanced Controls")
                ac1, ac2 = st.columns(2)
                with ac1:
                    nuclease = st.selectbox("Nuclease (for record/report only)", ["SpCas9", "SaCas9", "AsCas12a", "LbCas12a"])
                    show_probs = st.checkbox("Show raw model class probabilities", value=True)
                    use_heuristic = st.checkbox("Use weighted heuristic instead of model (experimental)", value=False)
                with ac2:
                    st.caption("User-weighted scoring (used when heuristic is enabled):")
                    w_eff = st.slider("Weight: Efficiency", 0.0, 1.0, 0.5, 0.05)
                    w_off = st.slider("Weight: Off-target (lower is better)", 0.0, 1.0, 0.3, 0.05)
                    w_via = st.slider("Weight: Viability", 0.0, 1.0, 0.2, 0.05)
                    blend_alpha = st.slider("Blend profiles with your inputs (0 = profiles, 1 = your inputs)",
                                            0.0, 1.0, 0.35, 0.05)

            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
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
            # ------- Heuristic path -------
            if show_advanced and 'use_heuristic' in locals() and use_heuristic:
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

                # Softmax over two scores -> confidence
                scores = np.array([score_lnp, score_elec])
                scores = scores - scores.max()
                probs = np.exp(scores) / np.exp(scores).sum()
                conf = float(100.0 * (probs[0] if rec == "LNP" else probs[1]))

                st.markdown('<span class="badge badge-heur">Heuristic mode (blended)</span>', unsafe_allow_html=True)

                if show_probs:
                    st.caption("Blended profiles and heuristic scores:")
                    dfp = pd.DataFrame([
                        {"Method": "LNP", "eff": round(p_lnp["eff"], 3), "off": round(p_lnp["off"], 3),
                         "via": round(p_lnp["via"], 3), "Weighted Score": round(score_lnp, 4)},
                        {"Method": "Electroporation", "eff": round(p_elec["eff"], 3), "off": round(p_elec["off"], 3),
                         "via": round(p_elec["via"], 3), "Weighted Score": round(score_elec, 4)},
                    ])
                    st.dataframe(dfp, use_container_width=True)

                # Radar values for heuristic
                radar_vals_1 = [p_lnp["eff"], p_lnp["off"], p_lnp["via"]]
                radar_vals_2 = [p_elec["eff"], p_elec["off"], p_elec["via"]]
                radar_labels = ["LNP (blended)", "Electroporation (blended)"]

            # ------- Model path -------
            else:
                rec = predict_method(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost)
                conf = predict_confidence(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost, rec)

                if show_advanced and 'show_probs' in locals() and show_probs:
                    feat = np.array([[le_mut.transform([mutation])[0],
                                      le_org.transform([organ])[0],
                                      eff, off, viability, cost]])
                    proba = model.predict_proba(feat)[0]
                    labels = le_method.inverse_transform(np.arange(len(proba)))
                    df_probs = pd.DataFrame({"Method": labels, "Probability (%)": (proba * 100).round(2)})
                    st.markdown("**Model class probabilities**")
                    st.dataframe(df_probs, use_container_width=True)

                # Radar values for model path
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

            # KPI row
            k1, k2 = st.columns(2)
            with k1:
                st.success(f"**Recommended Method:** {rec}")
            with k2:
                render_confidence_card(conf)

            if show_confidence_bar:
                st.progress(min(max(conf / 100.0, 0.0), 1.0))

            # Radar chart
            st.markdown("### Comparison (Radar Chart)")
            categories = ["Efficiency", "Off-Target Risk", "Viability"]
            N = len(categories)
            angles = [n / float(N) * 2 * pi for n in range(N)]
            angles += angles[:1]

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

            # Save radar image for the PDF
            radar_path = "radar_chart.png"
            fig.savefig(radar_path, dpi=150, bbox_inches="tight")
            st.pyplot(fig)
            plt.close(fig)

            # -------- Persist PDF bytes in session_state (SURVIVES RERUNS) --------
            if show_pdf_download:
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
                if show_advanced:
                    inputs["Nuclease"] = nuclease if "nuclease" in locals() else "SpCas9"
                    if 'use_heuristic' in locals() and use_heuristic:
                        inputs["Decision Mode"] = "Heuristic (blended)"
                        inputs["Weights"] = f"eff={w_eff:.2f}, off={w_off:.2f}, via={w_via:.2f}"
                        inputs["Blend α"] = f"{blend_alpha:.2f}"
                    else:
                        inputs["Decision Mode"] = "Model"

                # BACKEND RETURNS BYTES — do NOT open a file here
                pdf_bytes = generate_pdf_report(inputs, get_mutation_summary(mutation), radar_path, output_path=None)
                # Safety: only store bytes; Streamlit Cloud rejects str/None
                if isinstance(pdf_bytes, (bytes, bytearray)):
                    st.session_state["pdf_bytes"] = bytes(pdf_bytes)
                    st.session_state["pdf_name"] = "Genovate_Report.pdf"
                    st.success("Report generated. Scroll down to download ⬇️")
                else:
                    st.error("PDF generation returned non-bytes data. Please retry.")

    # ---- Persistent download area (outside submit so it never vanishes) ----
    if show_pdf_download and isinstance(st.session_state.get("pdf_bytes"), (bytes, bytearray)):
        st.markdown("### 📄 Download Summary Report")
        st.download_button(
            "📥 Download PDF",
            data=bytes(st.session_state["pdf_bytes"]),   # ensure bytes
            file_name=st.session_state.get("pdf_name", "Genovate_Report.pdf"),
            mime="application/pdf",
            use_container_width=True,
            key="download_report_btn",
        )

    # ---- PAM finder ----
    st.markdown("---")
    st.subheader("Optional: PAM Site Finder")
    pam_motif = st.text_input("PAM motif (IUPAC; default NGG)", value="NGG",
                              help="Use N to match any base. Example: NGG, TTTV, NNGRRT") if show_advanced else "NGG"
    dna_input = st.text_area(
        "Enter a DNA sequence (A/C/G/T only):",
        "AGGTCGTTACCGGTAGCGGTACCGTAGGGTAGGCTAGGGTACCGGTAG",
        help="Finds PAM motifs (default NGG for SpCas9).",
    )
    if st.button("🔎 Find PAM Sites", use_container_width=True):
        sites = find_pam_sites(dna_input.upper(), pam=pam_motif)
        if sites:
            st.success(f"✅ Found {len(sites)} PAM site(s). Showing first 10:")
            st.write(sites[:10])
        else:
            st.warning(f"❌ No {pam_motif} motifs found.")

# ===========================
# 2) GENE DETECTION TAB
# ===========================
with tab_detect:
    st.subheader("Auto-detect Gene from DNA Sequence (BLAST)")
    st.caption("Paste a DNA fragment (≥120 bp). Backend is biased to *Homo sapiens* for speed.")

    seq_in = st.text_area("Paste DNA sequence (A/C/G/T/N only):", height=160,
                          help="Tip: copy from NCBI FASTA (remove header).")
    if show_advanced:
        st.caption("Advanced: BLAST diagnostics will display raw hits as a table.")

    if st.button("🧬 Run BLAST Detection", use_container_width=True):
        if not seq_in or len(seq_in.strip()) < 120:
            st.error("Please paste a valid sequence ≥120 bp.")
        else:
            with st.spinner("Running BLAST (may take 10–30s)…"):
                results = detect_gene_from_sequence(seq_in)

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
                            "Accession/ID": parts[0],
                            "Title": parts[1],
                            "Identity": parts[2].replace("identity ≈ ", ""),
                        })
                    else:
                        rows.append({"Accession/ID": "", "Title": h, "Identity": ""})
                st.dataframe(pd.DataFrame(rows), use_container_width=True)

                if show_advanced:
                    st.caption("Raw hit strings (debug):")
                    for h in hits:
                        st.code(h)
            if not hits and not errors:
                st.warning("No high-confidence match found. Try a longer region (≥200 bp).")

# ===========================
# 3) SEQUENCE VIEWER TAB
# ===========================
with tab_viewer:
    st.subheader("Genomic Sequence Viewer (with PAM highlights)")
    st.caption("Shows the first N bases of the selected accession and highlights NGG motifs (SpCas9 PAM).")

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
        acc = st.text_input("NCBI Accession ID",
                            value=common_genes[sel] if sel != "Custom" else "")

    if acc:
        try:
            with st.spinner("Fetching GenBank record…"):
                info = _cached_fetch(acc)
            st.markdown(f"**🧬 Gene:** `{info['name']}`  •  **🌱 Organism:** `{info['organism']}`")

            raw_seq = info["seq"][:show_len]
            highlighted = highlight_pam_sites(raw_seq)
            st.markdown(
                f"<div class='codebox' style='word-wrap: break-word;'>{highlighted}</div>",
                unsafe_allow_html=True,
            )
            st.caption(f"🔴 Highlighted = PAM Sites (NGG) • Accession ID: {acc}")
        except Exception as e:
            st.error(f"❌ Error fetching sequence: {e}")
    else:
        st.info("Enter a valid accession (e.g., NM_001009944.3) to view sequence and PAMs.")

# ===========================
# 4) LEARNING MODE TAB
# ===========================
with tab_learn:
    st.subheader("CRISPR Education Hub")
    with st.expander("🔬 CRISPR Basics", expanded=True):
        st.write(learning_mode["CRISPR Basics"])
    c3, c4 = st.columns(2)
    with c3:
        with st.expander("⚡ Electroporation", expanded=True):
            st.write(learning_mode["Electroporation"])
    with c4:
        with st.expander("🧪 Lipid Nanoparticles (LNPs)", expanded=True):
            st.write(learning_mode["Lipid Nanoparticles (LNPs)"])
    with st.expander("🌐 External Resources", expanded=True):
        for label, url in learning_mode["External Resources"].items():
            st.markdown(f"- [{label}]({url})")

# ========= Footer =========
st.markdown("---")
st.caption("Developed by Raksheet Gummakonda • Genovate")
