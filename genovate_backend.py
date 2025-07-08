import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import os

# Load or simulate training data
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

# Train classifier
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

# Predict best delivery method
def predict_method(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost):
    features = np.array([[le_mut.transform([mutation])[0],
                          le_org.transform([organ])[0],
                          eff, off, viability, cost]])
    pred = model.predict(features)[0]
    return le_method.inverse_transform([pred])[0]

# Predict best delivery method with confidence score
def predict_method_with_confidence(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost):
    features = np.array([[le_mut.transform([mutation])[0],
                          le_org.transform([organ])[0],
                          eff, off, viability, cost]])
    pred_proba = model.predict_proba(features)[0]
    pred_index = np.argmax(pred_proba)
    pred_method = le_method.inverse_transform([pred_index])[0]
    confidence = pred_proba[pred_index]
    return pred_method, confidence

# Simple PAM site finder
def find_pam_sites(dna_sequence, pam="NGG"):
    pam_sites = []
    for i in range(len(dna_sequence) - len(pam) + 1):
        window = dna_sequence[i:i+len(pam)]
        match = all(b == p or p == 'N' for b, p in zip(window, pam))
        if match:
            pam_sites.append((i, window))
    return pam_sites

# Mutation summaries (30 words)
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

# Returns 30-word summary for mutation
def get_mutation_summary(mutation):
    return mutation_summaries.get(mutation, "No summary available for this mutation.")

# Gene image path (static)
def get_gene_image_path(mutation):
    return os.path.join("gene_images", f"{mutation}.png")
