import numpy as np
import pandas as pd
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from fpdf import FPDF
import matplotlib.pyplot as plt
from Bio import Entrez, SeqIO

# Always include your email for NCBI usage policy
Entrez.email = "your.email@example.com"  # Replace with your actual email

from Bio import Entrez, SeqIO
Entrez.email = "your.email@example.com"

def fetch_genbank_record(accession_id):
    with Entrez.efetch(db="nucleotide", id=accession_id, rettype="gb", retmode="text") as handle:
        return SeqIO.read(handle, "genbank")

def highlight_pam_sites(sequence, pam="NGG"):
    import re
    pam_regex = re.compile(r'(?=(.GG))')
    highlighted = ""
    i = 0
    matches = [m.start(1) for m in pam_regex.finditer(sequence)]
    while i < len(sequence):
        if i in matches:
            pam_seq = sequence[i:i+3]
            highlighted += f'<span style="background-color:#FFDD57; font-weight:bold">{pam_seq}</span>'
            i += 3
        else:
            highlighted += sequence[i]
            i += 1
    return highlighted

# 1. Simulate training data
def load_data():
    np.random.seed(42)
    num_samples = 200
    mutations = np.random.choice(['PKD1', 'PKD2', 'PKHD1', 'ATP7B', 'FAH', 'TTR', 'MYBPC3', 'TNNT2', 'MYH7',
                                  'CFTR', 'AATD', 'HTT', 'MECP2', 'SCN1A', 'RPE65', 'RPGR', 'INS', 'PDX1'], num_samples)
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

# 2. Train model
def train_model(data):
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

# 3. Predict method
def predict_method(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost):
    features = np.array([[le_mut.transform([mutation])[0],
                          le_org.transform([organ])[0],
                          eff, off, viability, cost]])
    pred = model.predict(features)[0]
    return le_method.inverse_transform([pred])[0]

# 4. Confidence score
def predict_confidence(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost, predicted_method):
    features = np.array([[le_mut.transform([mutation])[0],
                          le_org.transform([organ])[0],
                          eff, off, viability, cost]])
    proba = model.predict_proba(features)[0]
    method_index = le_method.transform([predicted_method])[0]
    confidence_score = proba[method_index] * 100
    return confidence_score

# 5. Generate PDF summary report
def generate_pdf_report(inputs, mutation_summary, radar_path, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "Genovate: CRISPR Delivery Prediction Summary", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=11)
    for key, value in inputs.items():
        pdf.cell(0, 10, f"{key}: {value}", ln=True)
    
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Mutation Summary: {mutation_summary}")

    pdf.ln(10)
    if os.path.exists(radar_path):
        pdf.image(radar_path, x=30, w=150)

    pdf.output(output_path)

# 6. PAM site finder
def find_pam_sites(dna_sequence, pam="NGG"):
    pam_sites = []
    for i in range(len(dna_sequence) - len(pam) + 1):
        window = dna_sequence[i:i+len(pam)]
        match = all(b == p or p == 'N' for b, p in zip(window, pam))
        if match:
            pam_sites.append((i, window))
    return pam_sites

# 7. Gene mutation summaries
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
    "HTT": "HTT mutations lead to Huntington’s disease, a neurodegenerative disorder affecting movement, cognition, and behavior.",
    "MECP2": "MECP2 mutations result in Rett syndrome, affecting brain development primarily in females.",
    "SCN1A": "SCN1A mutations impair sodium channels, often causing epilepsy syndromes such as Dravet syndrome.",
    "RPE65": "RPE65 mutations disrupt visual cycle enzymes, causing inherited retinal diseases like Leber congenital amaurosis.",
    "RPGR": "RPGR mutations lead to X-linked retinitis pigmentosa, causing progressive retinal degeneration.",
    "INS": "INS gene mutations affect insulin production, causing neonatal diabetes or MODY forms.",
    "PDX1": "PDX1 mutations impair pancreatic development, leading to diabetes due to beta-cell dysfunction."
}

def get_mutation_summary(mutation):
    return mutation_summaries.get(mutation, "No summary available for this mutation.")

def get_gene_image_path(mutation):
    return os.path.join("gene_images", f"{mutation}.png")

# 8. Learning mode content
learning_mode = {
    "CRISPR Basics": """
CRISPR is a gene-editing tool derived from bacterial defense mechanisms. It uses an RNA guide and Cas9 enzyme to cut DNA at specific sites, allowing for editing of genetic material.
""",
    "Electroporation": """
Electroporation involves applying electric fields to open pores in cell membranes, allowing CRISPR components (like Cas9 + guide RNA) to enter cells. It's commonly used for ex vivo editing.
""",
    "Lipid Nanoparticles (LNPs)": """
LNPs are tiny fat-based particles that encapsulate CRISPR components and deliver them into cells, especially useful for in vivo treatments via bloodstream injection.
""",
    "External Resources": {
        "CRISPR Tutorial by Broad Institute": "https://www.broadinstitute.org/what-broad/areas-focus/project-spotlight/crispr",
        "Nature CRISPR Guide": "https://www.nature.com/subjects/crispr-cas9",
        "MIT’s CRISPR Explainer": "https://biology.mit.edu/understanding-crispr/"
    }
}

def detect_gene_from_sequence(sequence):
    from Bio.Blast import NCBIWWW, NCBIXML

    try:
        result_handle = NCBIWWW.qblast("blastn", "nt", sequence, hitlist_size=5)
        blast_record = NCBIXML.read(result_handle)

        matches = []
        for alignment in blast_record.alignments[:3]:  # Top 3 matches
            hit_info = f"{alignment.hit_id} | {alignment.hit_def}"
            matches.append(hit_info)

        if matches:
            return matches
        else:
            return ["❌ No high-confidence gene match found"]
    except Exception as e:
        return [f"❌ Error running BLAST: {str(e)}"]
