# genovate_backend.py

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from fpdf import FPDF

# --- Biopython (NCBI + BLAST) ---
from Bio import Entrez, SeqIO
from Bio.Blast import NCBIWWW, NCBIXML

# REQUIRED by NCBI: set your real email
Entrez.email = "raksheetgummakonda28@gmail.com"   # <-- keep your real email here


# -------------------------------
# NCBI helpers
# -------------------------------
def fetch_genbank_record(accession_id: str):
    """Fetch a GenBank record and return a Biopython SeqRecord."""
    with Entrez.efetch(db="nucleotide", id=accession_id, rettype="gb", retmode="text") as handle:
        return SeqIO.read(handle, "genbank")


def highlight_pam_sites(sequence: str, pam: str = "NGG") -> str:
    """
    Return an HTML string with PAM (NGG) motifs highlighted.
    Designed for Streamlit's st.markdown(..., unsafe_allow_html=True).
    """
    import re
    pam_regex = re.compile(r'(?=(.GG))')  # N=any base
    highlighted = []
    seq = sequence.upper()

    i = 0
    matches = {m.start(1) for m in pam_regex.finditer(seq)}
    while i < len(seq):
        if i in matches:
            pam_seq = seq[i:i+3]
            highlighted.append(f'<span style="background-color:#FFDD57;font-weight:bold">{pam_seq}</span>')
            i += 3
        else:
            highlighted.append(seq[i])
            i += 1
    return "".join(highlighted)


# -------------------------------
# ML data + model
# -------------------------------
def load_data() -> pd.DataFrame:
    """Simulate training data (replace with real data when ready)."""
    np.random.seed(42)
    num_samples = 200
    mutations = np.random.choice(
        ['PKD1', 'PKD2', 'PKHD1', 'ATP7B', 'FAH', 'TTR', 'MYBPC3', 'TNNT2', 'MYH7',
         'CFTR', 'AATD', 'HTT', 'MECP2', 'SCN1A', 'RPE65', 'RPGR', 'INS', 'PDX1'],
        num_samples
    )
    organs = np.random.choice(['Kidney', 'Liver', 'Heart', 'Lung', 'Brain', 'Eye', 'Pancreas'], num_samples)
    methods = np.random.choice(['LNP', 'Electroporation'], num_samples)

    efficiency = np.where(methods == 'LNP',
                          np.random.normal(0.72, 0.05, num_samples),
                          np.random.normal(0.85, 0.04, num_samples))
    off_target = np.where(methods == 'LNP',
                          np.random.normal(0.07, 0.02, num_samples),
                          np.random.normal(0.12, 0.03, num_samples))
    cell_viability = np.where(methods == 'LNP',
                              np.random.normal(0.92, 0.03, num_samples),
                              np.random.normal(0.75, 0.05, num_samples))
    cost = np.where(methods == 'LNP',
                    np.random.randint(1, 3, num_samples),
                    np.random.randint(3, 5, num_samples))

    data = pd.DataFrame({
        "Mutation": mutations,
        "TargetOrgan": organs,
        "DeliveryMethod": methods,
        "Efficiency": np.clip(efficiency, 0, 1),
        "OffTargetRisk": np.clip(off_target, 0, 1),
        "CellViability": np.clip(cell_viability, 0, 1),
        "Cost": cost
    })
    return data


def train_model(data: pd.DataFrame):
    le_mut = LabelEncoder()
    le_org = LabelEncoder()
    le_method = LabelEncoder()

    data['Mutation_enc'] = le_mut.fit_transform(data['Mutation'])
    data['Organ_enc'] = le_org.fit_transform(data['TargetOrgan'])
    data['Method_enc'] = le_method.fit_transform(data['DeliveryMethod'])

    X = data[['Mutation_enc', 'Organ_enc', 'Efficiency', 'OffTargetRisk', 'CellViability', 'Cost']]
    y = data['Method_enc']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    return model, le_mut, le_org, le_method


def predict_method(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost) -> str:
    features = np.array([[le_mut.transform([mutation])[0],
                          le_org.transform([organ])[0],
                          eff, off, viability, cost]])
    pred = model.predict(features)[0]
    return le_method.inverse_transform([pred])[0]


def predict_confidence(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost, predicted_method) -> float:
    features = np.array([[le_mut.transform([mutation])[0],
                          le_org.transform([organ])[0],
                          eff, off, viability, cost]])
    proba = model.predict_proba(features)[0]
    method_index = le_method.transform([predicted_method])[0]
    return proba[method_index] * 100.0


# -------------------------------
# PDF Report (robust wrapping; fixes width error)
# -------------------------------
def _wrap_unbreakables(s: str, max_chunk: int = 40, use_unicode: bool = True) -> str:
    """
    Insert soft break points inside long tokens so fpdf2 can wrap them.
    - If Unicode is available, use ZERO-WIDTH SPACE (U+200B) every max_chunk chars.
    - Otherwise, insert a normal space every max_chunk chars.
    """
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)

    soft = "\u200b" if use_unicode else " "
    out_tokens = []
    for token in s.split(" "):
        if len(token) > max_chunk:
            chunks = [token[i:i+max_chunk] for i in range(0, len(token), max_chunk)]
            out_tokens.append(soft.join(chunks))
        else:
            out_tokens.append(token)
    return " ".join(out_tokens)


def _to_latin1_safe(s: str) -> str:
    """Sanitize to Latin-1 for classic FPDF fallback."""
    import unicodedata as _ud
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)

    replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201C": '"', "\u201D": '"',
        "\u2013": "-",  "\u2014": "-",
        "\u2022": "-",  "\u00A0": " ",
        "✅": "[OK]", "☑️": "[OK]", "⚠️": "[!]", "❗": "!",
        "🔴": "*", "🧬": "DNA", "📄": "Report",
    }
    for k, v in replacements.items():
        s = s.replace(k, v)

    s = _ud.normalize("NFKD", s)
    s = "".join(ch for ch in s if _ud.category(ch) != "Mn")
    return s.encode("latin-1", "replace").decode("latin-1")


def generate_pdf_report(inputs: dict, mutation_summary: str, radar_path: str, output_path: str):
    """
    Create a compact summary PDF with robust wrapping.
    - Uses explicit usable width for all multi_cell calls (no w=0).
    - Inserts soft break points inside long unbreakable tokens.
    - Uses Unicode TTF if fonts/DejaVuSans.ttf exists, else Latin-1 fallback.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)

    # Safe margins and page
    pdf.set_left_margin(12)
    pdf.set_right_margin(12)
    pdf.add_page()

    # Explicit usable width to avoid the "Not enough horizontal space" exception
    usable_w = pdf.w - pdf.l_margin - pdf.r_margin
    if usable_w <= 0:
        pdf.set_left_margin(10)
        pdf.set_right_margin(10)
        usable_w = pdf.w - pdf.l_margin - pdf.r_margin

    # Font selection
    font_path = os.path.join("fonts", "DejaVuSans.ttf")
    use_unicode = os.path.exists(font_path)
    if use_unicode:
        try:
            pdf.add_font("DejaVu", "", font_path, uni=True)
            pdf.add_font("DejaVu", "B", font_path, uni=True)
            body_font = ("DejaVu", "")
            bold_font = ("DejaVu", "B")
        except Exception:
            use_unicode = False

    if not use_unicode:
        body_font = ("Arial", "")
        bold_font = ("Arial", "B")

    def title(txt: str):
        pdf.set_font(bold_font[0], bold_font[1], 14)
        safe = _wrap_unbreakables(txt, 40, use_unicode)
        if not use_unicode:
            safe = _to_latin1_safe(safe)
        pdf.cell(0, 10, safe, ln=True, align="C")

    def line(txt: str, bold: bool = False, size: int = 11):
        pdf.set_font(*(bold_font if bold else body_font), size)
        safe = _wrap_unbreakables(txt, 40, use_unicode)
        if not use_unicode:
            safe = _to_latin1_safe(safe)
        # IMPORTANT: explicit width (usable_w), never 0
        pdf.multi_cell(usable_w, 7, safe)

    # Title
    title("Genovate: CRISPR Delivery Prediction Summary")
    pdf.ln(2)

    # Inputs
    line("Case Inputs", bold=True, size=12)
    for k, v in inputs.items():
        line(f"{k}: {v}")

    pdf.ln(1)
    line("Mutation Summary", bold=True, size=12)
    line(mutation_summary)

    pdf.ln(2)
    if radar_path and os.path.exists(radar_path):
        try:
            img_w = min(150, usable_w)
            x = pdf.l_margin + (usable_w - img_w) / 2.0
            pdf.image(radar_path, x=x, w=img_w)
        except Exception:
            line("[Radar chart could not be embedded]")

    pdf.output(output_path)


# -------------------------------
# PAM finder
# -------------------------------
def find_pam_sites(dna_sequence: str, pam: str = "NGG"):
    """Return list of (index, window) where the PAM motif occurs."""
    pam_sites = []
    seq = dna_sequence.upper()
    for i in range(len(seq) - len(pam) + 1):
        window = seq[i:i+len(pam)]
        match = all(b == p or p == 'N' for b, p in zip(window, pam))
        if match:
            pam_sites.append((i, window))
    return pam_sites


# -------------------------------
# Content + metadata
# -------------------------------
mutation_summaries = {
    "PKD1": "PKD1 mutations lead to polycystic kidney disease, disrupting cell polarity and tubule formation through polycystin-1 dysfunction.",
    "PKD2": "PKD2 mutations affect polycystin-2, impairing calcium signaling and leading to progressive kidney cyst formation.",
    "PKHD1": "PKHD1 mutations cause autosomal recessive polycystic kidney disease, affecting fibrocystin and collecting duct structure.",
    "ATP7B": "ATP7B mutations lead to Wilson's disease, impairing copper transport and causing hepatic and neurological symptoms.",
    "FAH": "FAH mutations result in tyrosinemia type I, disrupting tyrosine metabolism and causing liver and kidney dysfunction.",
    "TTR": "TTR mutations cause transthyretin amyloidosis, leading to protein misfolding and nerve and heart complications.",
    "MYBPC3": "MYBPC3 mutations disrupt cardiac sarcomere structure, commonly causing hypertrophic cardiomyopathy.",
    "TNNT2": "TNNT2 gene mutations affect cardiac troponin T, causing familial hypertrophic cardiomyopathy and heart failure.",
    "MYH7": "MYH7 mutations impair beta-myosin heavy chain, linked to cardiomyopathies and skeletal myopathies.",
    "CFTR": "CFTR mutations cause cystic fibrosis, blocking chloride ion transport and leading to mucus buildup in lungs.",
    "AATD": "AATD mutations reduce alpha-1 antitrypsin levels, causing emphysema and liver disease.",
    "HTT": "HTT mutations lead to Huntington's disease, a neurodegenerative disorder affecting movement, cognition, and behavior.",
    "MECP2": "MECP2 mutations result in Rett syndrome, affecting brain development primarily in females.",
    "SCN1A": "SCN1A mutations impair sodium channels, often causing epilepsy syndromes such as Dravet syndrome.",
    "RPE65": "RPE65 mutations disrupt visual cycle enzymes, causing inherited retinal diseases like Leber congenital amaurosis.",
    "RPGR": "RPGR mutations lead to X-linked retinitis pigmentosa, causing progressive retinal degeneration.",
    "INS": "INS gene mutations affect insulin production, causing neonatal diabetes or MODY forms.",
    "PDX1": "PDX1 mutations impair pancreatic development, leading to diabetes due to beta-cell dysfunction."
}

def get_mutation_summary(mutation: str) -> str:
    return mutation_summaries.get(mutation, "No summary available for this mutation.")

def get_gene_image_path(mutation: str) -> str:
    return os.path.join("gene_images", f"{mutation}.png")


learning_mode = {
    "CRISPR Basics": """
CRISPR is a gene-editing tool derived from bacterial defense mechanisms. It uses an RNA guide and Cas9 enzyme to cut DNA at specific sites, allowing precise edits to genetic material.
""",
    "Electroporation": """
Electroporation uses short electric pulses to open membrane pores so CRISPR components (Cas9 + gRNA) can enter cells. Common for ex vivo cell editing (T cells, HSCs).
""",
    "Lipid Nanoparticles (LNPs)": """
LNPs are fat-based vesicles that encapsulate CRISPR cargo (mRNA/protein/sgRNA) for systemic in vivo delivery, with strong liver tropism and improving kidney targeting.
""",
    "External Resources": {
        "Broad CRISPR Overview": "https://www.broadinstitute.org/what-broad/areas-focus/project-spotlight/crispr",
        "Nature CRISPR Guide": "https://www.nature.com/subjects/crispr-cas9",
        "NCBI Bookshelf: Genome Editing": "https://www.ncbi.nlm.nih.gov/books/"
    }
}


# -------------------------------
# BLAST-based gene detection (no esearch pre-check)
# -------------------------------
def detect_gene_from_sequence(sequence: str):
    """
    Run BLASTN on the given DNA sequence and return up to 3 top matches.
    Assumes Biopython and outbound internet are available.
    """
    try:
        # Cleanup & basic validation
        seq = "".join(sequence.upper().split())
        if any(ch not in "ACGTN" for ch in seq):
            return ["❌ Input must contain only A/C/G/T (and optional N)."]
        if len(seq) < 120:
            return ["❌ Sequence too short for reliable BLAST. Please paste ≥120 bp."]

        # BLAST tuned for speed & relevance
        result_handle = NCBIWWW.qblast(
            program="blastn",
            database="nt",
            sequence=seq,
            megablast=True,        # faster for close matches
            word_size=28,          # speed/precision tradeoff
            expect=1e-20,          # stringent
            entrez_query="Homo sapiens[Organism]"  # bias to human
        )
        blast_record = NCBIXML.read(result_handle)

        matches = []
        for alignment in blast_record.alignments[:3]:
            title_short = " ".join(alignment.hit_def.split()[:12])
            hsp = alignment.hsps[0] if alignment.hsps else None
            ident = f"{(hsp.identities / hsp.align_length * 100):.1f}%" if hsp else "n/a"
            matches.append(f"🧬 {alignment.hit_id} | {title_short} | identity ≈ {ident}")

        return matches if matches else ["❌ No high-confidence gene match found."]
    except Exception as e:
        return [f"❌ Error during BLAST: {e}"]
