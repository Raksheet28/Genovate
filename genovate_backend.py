# genovate_backend.py
# Compatible with Python 3.9 (no PEP 604 unions). No multi_cell calls anywhere.

import os
import re
import unicodedata
from typing import Optional, List, Dict

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from fpdf import FPDF  # fpdf2

# --- Biopython (NCBI + BLAST) ---
from Bio import Entrez, SeqIO
from Bio.Blast import NCBIWWW, NCBIXML

# REQUIRED by NCBI: set your real email
Entrez.email = "raksheetgummakonda28@gmail.com"   # keep your real email here


# ===============================
# NCBI helpers
# ===============================
def fetch_genbank_record(accession_id: str):
    """Fetch a GenBank record and return a Biopython SeqRecord."""
    with Entrez.efetch(db="nucleotide", id=accession_id, rettype="gb", retmode="text") as handle:
        return SeqIO.read(handle, "genbank")


# ===============================
# PAM highlighting (IUPAC aware)
# ===============================
_IUPAC_MAP = {
    "R": "[AG]", "Y": "[CT]", "S": "[GC]", "W": "[AT]",
    "K": "[GT]", "M": "[AC]", "B": "[CGT]", "D": "[AGT]",
    "H": "[ACT]", "V": "[ACG]", "N": "[ACGT]",
}

def _iupac_to_regex(motif: str) -> str:
    return "".join(_IUPAC_MAP.get(ch, ch) for ch in motif.upper())

def highlight_pam_sites(sequence: str, pam: str = "NGG") -> str:
    """
    Return an HTML string with PAM motifs highlighted.
    Designed for Streamlit's st.markdown(..., unsafe_allow_html=True).
    """
    seq = (sequence or "").upper()
    motif = pam.upper()
    # Overlapping lookahead to find all starts
    if motif == "NGG":
        rx = re.compile(r"(?=(.GG))")
        width = 3
    else:
        pat = _iupac_to_regex(motif)
        rx = re.compile(fr"(?=({pat}))")
        width = len(motif)

    starts = {m.start(1) for m in rx.finditer(seq)}
    out: List[str] = []
    i = 0
    while i < len(seq):
        if i in starts:
            out.append(f'<span style="background-color:#FFDD57;font-weight:bold">{seq[i:i+width]}</span>')
            i += width
        else:
            out.append(seq[i])
            i += 1
    return "".join(out)


# ===============================
# ML mock data + model
# ===============================
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

    return pd.DataFrame({
        "Mutation": mutations,
        "TargetOrgan": organs,
        "DeliveryMethod": methods,
        "Efficiency": np.clip(efficiency, 0, 1),
        "OffTargetRisk": np.clip(off_target, 0, 1),
        "CellViability": np.clip(cell_viability, 0, 1),
        "Cost": cost
    })


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
    return float(proba[method_index] * 100.0)


# ===============================
# PDF helpers — robust wrapping (NO multi_cell) and returns BYTES
# ===============================
def _to_latin1(s: str) -> str:
    """
    Convert arbitrary Unicode to Latin-1 for classic FPDF fallback.
    Also replaces emojis/specials to ASCII tokens to avoid width issues.
    """
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

    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.encode("latin-1", "replace").decode("latin-1")


def _chunk_word_to_fit(pdf: FPDF, word: str, max_w: float) -> List[str]:
    """Break a single long token (no spaces) into chunks that fit within max_w."""
    chunks: List[str] = []
    cur = ""
    for ch in word:
        w = pdf.get_string_width(cur + ch)
        if w <= max_w or not cur:
            cur += ch
        else:
            chunks.append(cur)
            cur = ch
    if cur:
        chunks.append(cur)
    return chunks


def _wrap_text_to_width(pdf: FPDF, text: str, max_w: float) -> List[str]:
    """
    Wrap text to a given width using font metrics; splits overlong tokens safely.
    Returns list of lines that each fit within max_w.
    """
    lines_out: List[str] = []
    for para in (text or "").splitlines():
        words = para.split(" ")
        line = ""
        for w in words:
            token = w if w != "" else " "
            tentative = (line + " " + token).strip() if line else token
            if pdf.get_string_width(tentative) <= max_w:
                line = tentative
            else:
                if line:
                    lines_out.append(line)
                if pdf.get_string_width(token) > max_w:
                    for part in _chunk_word_to_fit(pdf, token, max_w):
                        if pdf.get_string_width(part) <= max_w:
                            lines_out.append(part)
                        else:
                            # extreme fallback split
                            lines_out.append(part[:1]); lines_out.append(part[1:])
                    line = ""
                else:
                    line = token
        if line:
            lines_out.append(line)
    return lines_out


def generate_pdf_report(
    inputs: Dict[str, str],
    mutation_summary: str,
    radar_path: Optional[str],
    output_path: Optional[str] = None
) -> bytes:
    """
    Create the summary PDF and return raw bytes.
    - Uses full Unicode if fonts/DejaVuSans.ttf exists; else Latin-1 with sanitization
    - NO multi_cell calls (prevents 'Not enough horizontal space' errors)
    - If output_path is provided, writes bytes to that path too.
    """
    font_path = os.path.join("fonts", "DejaVuSans.ttf")
    use_unicode = os.path.exists(font_path)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(left=15, top=15, right=15)

    content_w = pdf.w - pdf.l_margin - pdf.r_margin  # usable width

    # Font setup
    if use_unicode:
        try:
            pdf.add_font("DejaVu", "", font_path, uni=True)
            pdf.add_font("DejaVu", "B", font_path, uni=True)
            def set_font(bold: bool = False, size: int = 11) -> None:
                pdf.set_font("DejaVu", "B" if bold else "", size)
            sanitizer = (lambda s: s)
        except Exception:
            use_unicode = False

    if not use_unicode:
        def set_font(bold: bool = False, size: int = 11) -> None:
            pdf.set_font("Arial", "B" if bold else "", size)
        sanitizer = _to_latin1

    def write_wrapped(text: str, line_h: float = 7) -> None:
        safe = sanitizer(text)
        for ln in _wrap_text_to_width(pdf, safe, content_w):
            pdf.cell(0, line_h, ln, ln=1)

    # Title
    set_font(bold=True, size=14)
    pdf.cell(0, 10, sanitizer("Genovate: CRISPR Delivery Prediction Summary"), ln=1, align="C")
    pdf.ln(2)

    # Case Inputs
    set_font(bold=True, size=12)
    pdf.cell(0, 8, sanitizer("Case Inputs"), ln=1)
    set_font(size=11)
    for k, v in (inputs or {}).items():
        # Encourage wrapping by inserting zero-width spaces after spaces
        safe_v = str(v).replace(" ", "\u200b ")
        write_wrapped(f"{k}: {safe_v}")
    pdf.ln(2)

    # Mutation summary
    set_font(bold=True, size=12)
    pdf.cell(0, 8, sanitizer("Mutation Summary"), ln=1)
    set_font(size=11)
    write_wrapped(mutation_summary, line_h=7)
    pdf.ln(3)

    # Radar image (optional)
    if radar_path and os.path.exists(radar_path):
        try:
            img_w = min(160, content_w)
            x = pdf.l_margin + (content_w - img_w) / 2.0
            pdf.image(radar_path, x=x, w=img_w)
        except Exception:
            set_font(size=11)
            write_wrapped("[Radar chart could not be embedded]")

    # Output to bytes (fpdf2 returns str); encode to bytes
    raw = pdf.output(dest="S")
    pdf_bytes: bytes = raw.encode("latin-1") if isinstance(raw, str) else raw
    if output_path:
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
    return pdf_bytes


# ===============================
# PAM finder (IUPAC aware)
# ===============================
def find_pam_sites(dna_sequence: str, pam: str = "NGG"):
    """Return list of (index, window) where the PAM motif occurs (simple IUPAC support)."""
    dna = (dna_sequence or "").upper()
    pat = _iupac_to_regex(pam.upper())
    rx = re.compile(pat)
    hits = []
    L = len(pam)
    for i in range(len(dna) - L + 1):
        if rx.fullmatch(dna[i:i+L]):
            hits.append((i, dna[i:i+L]))
    return hits


# ===============================
# Content + metadata
# ===============================
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


# ===============================
# BLAST-based gene detection (no esearch pre-check)
# ===============================
def detect_gene_from_sequence(sequence: str):
    """
    Run BLASTN on the given DNA sequence and return up to 3 top matches.
    Assumes Biopython and outbound internet are available.
    """
    try:
        seq = "".join((sequence or "").upper().split())
        if any(ch not in "ACGTN" for ch in seq):
            return ["❌ Input must contain only A/C/G/T (and optional N)."]
        if len(seq) < 120:
            return ["❌ Sequence too short for reliable BLAST. Please paste ≥120 bp."]

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
