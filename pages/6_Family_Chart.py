# pages/6_Family_Chart.py — Family Chart & Inheritance Risk (Beta)
# Streamlit page to build a simple family chart (pedigree-lite), record diagnoses, 
# and estimate inheritance risk for common patterns (AR, AD, X-linked, Mitochondrial)
#
# Notes
# - Educational tool, not medical advice. Display a clear disclaimer in the UI.
# - Calculations are simplified Bayesian estimates using user-provided family history.
# - Supports: Autosomal Recessive (AR), Autosomal Dominant (AD), X-linked Recessive (XLR),
#            X-linked Dominant (XLD), Mitochondrial (MITO), and a catch‑all "Custom".
# - Outputs: Risk estimates for the user (proband), a graph of the family chart, and a
#            downloadable PDF summary (uses fpdf) for clinic/counseling conversations.
# - Privacy-first: no storage by default; export only on user action.

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st
from fpdf import FPDF

# Optional: Graphviz for pedigree-lite rendering
try:
    import graphviz
    HAS_GRAPHVIZ = True
except Exception:
    HAS_GRAPHVIZ = False

st.set_page_config(page_title="Genovate • Family Chart & Risk", page_icon="👪", layout="wide")

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .risk-badge {padding:6px 10px; border-radius:12px; font-weight:600;}
    .low {background:#E8F5E9; color:#1B5E20;}
    .mod {background:#FFF8E1; color:#E65100;}
    .high {background:#FBE9E7; color:#B71C1C;}
    .disclaimer {font-size:0.9rem; opacity:0.85}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Data Models ----------
@dataclass
class Person:
    pid: str
    name: str
    sex: str  # 'M' or 'F'
    relation: str  # self, mother, father, sibling, child, etc.
    affected: Optional[bool] = None  # True/False/None(unknown)
    carrier: Optional[bool] = None   # For AR/XLR when known
    age: Optional[int] = None
    notes: str = ""
    parents: List[str] = field(default_factory=list)  # [father_pid, mother_pid]


# Store in session (privacy: in-memory only)
if "family" not in st.session_state:
    st.session_state.family: Dict[str, Person] = {}

# Ensure a proband exists
if "proband_id" not in st.session_state:
    st.session_state.proband_id = "P0"
    st.session_state.family["P0"] = Person(
        pid="P0", name="You (Proband)", sex="F", relation="self", affected=None
    )

# ---------- Helper: risk classification ----------
def risk_bucket(prob: float) -> str:
    if prob is None:
        return "Unknown"
    if prob < 0.01:
        return "Low"
    if prob < 0.1:
        return "Moderate"
    return "High"


def badge(prob: Optional[float]) -> str:
    if prob is None:
        return '<span class="risk-badge">Unknown</span>'
    b = risk_bucket(prob)
    cls = {"Low": "low", "Moderate": "mod", "High": "high"}.get(b, "")
    pct = f"{prob*100:.1f}%"
    return f'<span class="risk-badge {cls}">{b} • {pct}</span>'


# ---------- Simplified Risk Engines ----------
# These assume a single‑gene model; users can set prevalence, carrier rate, and penetrance.

@dataclass
class InheritanceParams:
    pattern: str  # AR, AD, XLR, XLD, MITO, Custom
    prevalence: float  # population prevalence (affected)
    carrier_freq: float  # for AR / XLR (q)
    penetrance: float  # probability an individual with genotype expresses phenotype
    de_novo_rate: float  # applies mainly to AD/XLD


def get_parent(persons: Dict[str, Person], pid: str, role: str) -> Optional[Person]:
    p = persons.get(pid)
    if not p or not p.parents:
        return None
    father_id = p.parents[0] if len(p.parents) > 0 else None
    mother_id = p.parents[1] if len(p.parents) > 1 else None
    if role == "father" and father_id:
        return persons.get(father_id)
    if role == "mother" and mother_id:
        return persons.get(mother_id)
    return None


def prob_proband_AR(persons: Dict[str, Person], proband: Person, prm: InheritanceParams) -> float:
    # Base AR: P(affected) = carrier_prob_father * carrier_prob_mother * 1/4 * penetrance
    # Estimate carrier probs from observed family history; start from carrier_freq.
    q = prm.carrier_freq
    cf = q  # father baseline carrier prob
    cm = q  # mother baseline carrier prob

    father = get_parent(persons, proband.pid, "father")
    mother = get_parent(persons, proband.pid, "mother")

    # Simple updates: if parent affected -> obligate carrier (at least heterozygous)
    if father and father.affected is True:
        cf = 1.0  # (simplification: affected implies aa; for AR, they pass a with prob 1)
    if mother and mother.affected is True:
        cm = 1.0

    # If a sibling affected, raise posterior estimate that both parents are carriers.
    sibs = [p for p in persons.values() if p.relation == "sibling"]
    if any(s.affected for s in sibs):
        # If one sibling affected in AR, posterior P(both carriers) ~ 2/3 given unaffected child, but
        # here we assume at least one affected child exists: 
        # P(parents both carriers | >=1 affected child) is very high; set cf=cm=2/3 approximated carriers
        cf = max(cf, 2/3)
        cm = max(cm, 2/3)

    prob = cf * cm * 0.25 * prm.penetrance
    return min(max(prob, 0.0), 1.0)


def prob_proband_AD(persons: Dict[str, Person], proband: Person, prm: InheritanceParams) -> float:
    # Base AD: If one parent affected (heterozygous), child risk ~ 1/2 * penetrance
    # If none affected: de novo rate applies.
    father = get_parent(persons, proband.pid, "father")
    mother = get_parent(persons, proband.pid, "mother")
    parent_risk = 0.0
    for parent in [father, mother]:
        if parent and parent.affected is True:
            parent_risk = max(parent_risk, 0.5 * prm.penetrance)
    if parent_risk == 0.0:
        parent_risk = prm.de_novo_rate * prm.penetrance
    return min(max(parent_risk, 0.0), 1.0)


def prob_proband_XLR(persons: Dict[str, Person], proband: Person, prm: InheritanceParams) -> float:
    # X-linked recessive: males affected if receive mutant X; females typically carriers.
    q = prm.carrier_freq  # female carrier frequency
    if proband.sex == "M":
        mother = get_parent(persons, proband.pid, "mother")
        cm = q
        if mother and (mother.carrier or (mother.affected is True)):
            cm = 1.0
        return 0.5 * cm * prm.penetrance  # mother passes X with prob 1/2
    else:  # female
        father = get_parent(persons, proband.pid, "father")
        mother = get_parent(persons, proband.pid, "mother")
        cf = 1.0 if (father and father.affected) else 0.0
        cm = q if not (mother and (mother.carrier or mother.affected)) else 1.0
        # Female affected in XLR requires both X mutated (rare); approximated as cm*cf*(1/2)*(1/2)
        return cm * cf * 0.25 * prm.penetrance


def prob_proband_XLD(persons: Dict[str, Person], proband: Person, prm: InheritanceParams) -> float:
    father = get_parent(persons, proband.pid, "father")
    mother = get_parent(persons, proband.pid, "mother")
    if proband.sex == "F":
        # If either parent affected: risk ~ 1/2 from mother, 1.0 from father (all daughters get father's X)
        risk = 0.0
        if mother and mother.affected:
            risk = max(risk, 0.5 * prm.penetrance)
        if father and father.affected:
            risk = max(risk, 1.0 * prm.penetrance)
        if risk == 0.0:
            risk = prm.de_novo_rate * prm.penetrance
        return min(max(risk, 0.0), 1.0)
    else:  # male
        # From mother only; if mother affected/carrier, 50% of sons affected
        if mother and mother.affected:
            return 0.5 * prm.penetrance
        return prm.de_novo_rate * prm.penetrance


def prob_proband_MITO(persons: Dict[str, Person], proband: Person, prm: InheritanceParams) -> float:
    mother = get_parent(persons, proband.pid, "mother")
    if mother and mother.affected:
        # Simplified: all children inherit mutant mtDNA; expression scaled by penetrance
        return 1.0 * prm.penetrance
    # Otherwise, background prevalence
    return prm.prevalence * prm.penetrance


PATTERN_ENGINES = {
    "Autosomal Recessive (AR)": prob_proband_AR,
    "Autosomal Dominant (AD)": prob_proband_AD,
    "X-linked Recessive (XLR)": prob_proband_XLR,
    "X-linked Dominant (XLD)": prob_proband_XLD,
    "Mitochondrial (MITO)": prob_proband_MITO,
}

# ---------- Sidebar: Disease / Assumptions ----------
st.sidebar.header("🧬 Condition & Assumptions")
pattern = st.sidebar.selectbox(
    "Inheritance pattern",
    list(PATTERN_ENGINES.keys()) + ["Custom (manual override)"]
)

colA, colB = st.sidebar.columns(2)
with colA:
    prevalence = st.number_input("Population prevalence (affected)", min_value=0.0, max_value=1.0, value=0.001, step=0.0001, format="%0.4f")
    penetrance = st.number_input("Penetrance (0–1)", min_value=0.0, max_value=1.0, value=1.0, step=0.05)
with colB:
    carrier_freq = st.number_input("Carrier frequency q (0–1)", min_value=0.0, max_value=1.0, value=0.02, step=0.001, format="%0.3f")
    de_novo_rate = st.number_input("De novo rate (AD/XLD)", min_value=0.0, max_value=1.0, value=0.0001, step=0.0001, format="%0.4f")

prm = InheritanceParams(
    pattern=pattern,
    prevalence=prevalence,
    carrier_freq=carrier_freq,
    penetrance=penetrance,
    de_novo_rate=de_novo_rate,
)

st.sidebar.markdown(
    """
    **Tip**: If you know your family's specific gene/variant (e.g., *PKD1* c.XXXX), 
    use Genovate's **Gene Detection** first, then return here and set realistic assumptions.
    """
)

st.sidebar.markdown(
    """
    <div class="disclaimer">
    <b>Disclaimer</b>: This tool provides educational estimates based on the information you enter. 
    It is not a diagnosis. Please consult a licensed genetic counselor or physician for medical decisions.
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Family Builder ----------
st.title("👪 Family Chart & Inheritance Risk")
st.caption("Add relatives, mark who is affected or a known carrier, and estimate your risk under different inheritance models.")

with st.expander("Add / Edit Family Members", expanded=True):
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Proband (You)")
        p = st.session_state.family[st.session_state.proband_id]
        p.name = st.text_input("Display name", p.name)
        p.sex = st.selectbox("Sex", ["F", "M"], index=0 if p.sex == "F" else 1)
        p.affected = st.selectbox("Diagnosed/affected?", ["Unknown", "No", "Yes"], index=0 if p.affected is None else (2 if p.affected else 1))
        p.affected = None if p.affected == "Unknown" else (True if p.affected == "Yes" else False)
        p.age = st.number_input("Age (optional)", min_value=0, max_value=120, value=p.age or 0)
        p.notes = st.text_area("Notes", p.notes)
        st.session_state.family[p.pid] = p

    with c2:
        st.subheader("Relatives")
        with st.form("add_relative_form", clear_on_submit=True):
            name = st.text_input("Name")
            relation = st.selectbox("Relation", ["mother", "father", "sibling", "child", "grandparent", "aunt/uncle", "cousin", "other"])
            sex = st.selectbox("Sex", ["F", "M"])            
            affected = st.selectbox("Diagnosed/affected?", ["Unknown", "No", "Yes"])            
            carrier = st.selectbox("Known carrier? (if applicable)", ["Unknown", "No", "Yes"])            
            age = st.number_input("Age (optional)", min_value=0, max_value=120, value=0)
            notes = st.text_area("Notes (optional)")
            submitted = st.form_submit_button("Add relative")
        if submitted and name:
            pid = f"P{len(st.session_state.family)}"
            person = Person(
                pid=pid,
                name=name,
                sex=sex,
                relation=relation,
                affected=None if affected == "Unknown" else (True if affected == "Yes" else False),
                carrier=None if carrier == "Unknown" else (True if carrier == "Yes" else False),
                age=age if age > 0 else None,
                notes=notes,
            )
            # Link parents if adding mother/father
            if relation == "mother":
                st.session_state.family[st.session_state.proband_id].parents = [
                    st.session_state.family[st.session_state.proband_id].parents[0] if st.session_state.family[st.session_state.proband_id].parents else None,
                    pid,
                ]
            elif relation == "father":
                st.session_state.family[st.session_state.proband_id].parents = [
                    pid,
                    st.session_state.family[st.session_state.proband_id].parents[1] if st.session_state.family[st.session_state.proband_id].parents else None,
                ]
            st.session_state.family[pid] = person

# Table view
fam_df = pd.DataFrame([
    {
        "ID": p.pid,
        "Name": p.name,
        "Relation": p.relation,
        "Sex": p.sex,
        "Affected": {True: "Yes", False: "No"}.get(p.affected, "Unknown"),
        "Carrier": {True: "Yes", False: "No"}.get(p.carrier, "Unknown"),
        "Age": p.age,
        "Notes": p.notes,
    }
    for p in st.session_state.family.values()
])

st.markdown("**Family Members**")
st.dataframe(fam_df, use_container_width=True, hide_index=True)

# ---------- Risk Estimation ----------
proband = st.session_state.family[st.session_state.proband_id]

engine = None
for k, fn in PATTERN_ENGINES.items():
    if prm.pattern.startswith(k.split(" (")[0]):
        engine = fn
        break

if engine:
    prob = engine(st.session_state.family, proband, prm)
else:
    prob = None

st.subheader("Your Estimated Risk")
st.markdown(badge(prob), unsafe_allow_html=True)

with st.expander("How this estimate was calculated"):
    st.write(
        "These estimates combine your selected inheritance pattern, assumptions (carrier frequency, penetrance, de novo rate), and your family history (e.g., affected parents/siblings). They are simplified for education and may not capture locus heterogeneity, mosaicism, variable expressivity, or polygenic effects."
    )

# ---------- Pedigree-lite visualization ----------
if HAS_GRAPHVIZ:
    st.subheader("Family Chart (Pedigree‑lite)")
    dot = graphviz.Digraph()
    for p in st.session_state.family.values():
        shape = "box" if p.sex == "M" else "ellipse"
        color = "#2e7d32" if p.affected is True else ("#e65100" if p.affected is False else "#546e7a")
        label = f"{p.name}\n({p.relation})"
        dot.node(p.pid, label=label, shape=shape, color=color, fontname="Helvetica")
    # Draw parent links for proband if available
    father = get_parent(st.session_state.family, proband.pid, "father")
    mother = get_parent(st.session_state.family, proband.pid, "mother")
    if father:
        dot.edge(father.pid, proband.pid)
    if mother:
        dot.edge(mother.pid, proband.pid)
    st.graphviz_chart(dot, use_container_width=True)
else:
    st.info("Install graphviz to enable pedigree visualization: pip install graphviz")

# ---------- Downloadable PDF Summary ----------

def build_pdf_summary(prob: Optional[float], df: pd.DataFrame, prm: InheritanceParams) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Genovate — Family Chart & Risk Summary", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 7, txt=(
        "This report is educational and not a medical diagnosis. For decisions, consult a clinical geneticist or genetic counselor.\n\n"
        f"Inheritance pattern: {prm.pattern}\n"
        f"Prevalence: {prm.prevalence:.5f} | Carrier frequency q: {prm.carrier_freq:.3f} | Penetrance: {prm.penetrance:.2f} | De novo: {prm.de_novo_rate:.5f}\n"
        f"Estimated proband risk: {('N/A' if prob is None else f'{prob*100:.2f}%')}\n\n"
    ))
    # Table header
    pdf.set_font("Arial", "B", 11)
    pdf.cell(25, 8, "ID", 1)
    pdf.cell(55, 8, "Name", 1)
    pdf.cell(30, 8, "Relation", 1)
    pdf.cell(15, 8, "Sex", 1)
    pdf.cell(25, 8, "Affected", 1)
    pdf.cell(25, 8, "Carrier", 1)
    pdf.ln()
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        pdf.cell(25, 8, str(row["ID"])[:12], 1)
        pdf.cell(55, 8, str(row["Name"])[:28], 1)
        pdf.cell(30, 8, str(row["Relation"])[:14], 1)
        pdf.cell(15, 8, str(row["Sex"])[:3], 1)
        pdf.cell(25, 8, str(row["Affected"])[:8], 1)
        pdf.cell(25, 8, str(row["Carrier"])[:8], 1)
        pdf.ln()
    pdf.output(dest='S')
    return bytes(pdf.output(dest='S').encode('latin1'))

colL, colR = st.columns([1,1])
with colL:
    if st.button("📄 Download PDF summary"):
        data = build_pdf_summary(prob, fam_df, prm)
        st.download_button("Download now", data=data, file_name="genovate_family_chart_summary.pdf", mime="application/pdf")

with colR:
    st.download_button(
        "⬇️ Export family table (CSV)",
        data=fam_df.to_csv(index=False).encode("utf-8"),
        file_name="genovate_family.csv",
        mime="text/csv",
    )

# ---------- Community Impact Hooks ----------
st.divider()
st.subheader("Community Impact & Next Steps")
st.markdown(
    """
    - **Family Letter**: Share the summary with relatives to encourage informed testing and early screening.
    - **Local Resources**: Pair this page with a curated list of genetic counseling centers and tele‑counseling options in your region.
    - **Anonymized Insights (Opt‑in)**: Offer an optional checkbox in Settings to anonymously contribute prevalence/carrier data for community dashboards.
    - **Education**: Include explainers for each inheritance pattern and what actions (e.g., confirmatory testing) may be appropriate.
    """
)
