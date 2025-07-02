# genovate_backend.py

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Load or simulate data (replace with real data or CSV if needed)
def load_data():
    np.random.seed(42)
    num_samples = 200
    mutations = np.random.choice(
        ['PKD1', 'PKD2', 'PKHD1', 'ATP7B', 'FAH', 'TTR', 'MYBPC3', 'TNNT2', 'MYH7',
         'CFTR', 'AATD', 'HTT', 'MECP2', 'SCN1A', 'RPE65', 'RPGR', 'INS', 'PDX1'],
        num_samples
    )
    organs = np.random.choice(
        ['Kidney', 'Liver', 'Heart', 'Lung', 'Brain', 'Eye', 'Pancreas'],
        num_samples
    )
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

# Prepare and train model
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

# Prediction function
def predict_method(model, le_mut, le_org, le_method, mutation, organ, eff, off, viability, cost):
    features = np.array([[le_mut.transform([mutation])[0],
                         le_org.transform([organ])[0],
                         eff, off, viability, cost]])
    pred = model.predict(features)[0]
    return le_method.inverse_transform([pred])[0]

# PAM Finder (for integration)
def find_pam_sites(dna_sequence, pam="NGG"):
    pam_sites = []
    for i in range(len(dna_sequence) - len(pam) + 1):
        window = dna_sequence[i:i+len(pam)]
        match = all(b == p or p == 'N' for b, p in zip(window, pam))
        if match:
            pam_sites.append((i, window))
    return pam_sites

# Gene mutation summary lookup
def get_mutation_summary():
    return {
        "PKD1": "Causes autosomal dominant polycystic kidney disease, leading to fluid-filled cysts in kidneys and eventual kidney failure.",
        "PKD2": "Another ADPKD gene, its mutation leads to less severe cyst formation and kidney dysfunction compared to PKD1.",
        "PKHD1": "Responsible for autosomal recessive PKD, mostly affecting infants and children with liver and kidney issues.",
        "ATP7B": "Mutations lead to Wilson’s Disease, a rare disorder causing copper buildup in liver, brain, and other organs.",
        "FAH": "Causes Tyrosinemia Type I, a disorder impairing the breakdown of the amino acid tyrosine, primarily affecting the liver.",
        "TTR": "Mutations result in transthyretin amyloidosis, affecting the nerves and heart via protein misfolding and accumulation.",
        "MYBPC3": "Linked to hypertrophic cardiomyopathy, causing thickened heart muscle and potential cardiac arrest.",
        "TNNT2": "Encodes cardiac troponin T, and its mutation leads to inherited cardiomyopathy and sudden cardiac death.",
        "MYH7": "Mutated in hypertrophic and dilated cardiomyopathy, affecting cardiac muscle contraction.",
        "CFTR": "Defective gene in cystic fibrosis, causes thick mucus buildup in lungs and other organs.",
        "AATD": "Alpha-1 antitrypsin deficiency leads to lung disease and liver dysfunction.",
        "HTT": "Responsible for Huntington’s disease, a neurodegenerative disorder with motor, cognitive, and psychiatric symptoms.",
        "MECP2": "Mutations lead to Rett Syndrome, a neurological disorder in girls affecting movement and communication.",
        "SCN1A": "Linked to Dravet Syndrome, a severe epilepsy beginning in infancy.",
        "RPE65": "Gene therapy target for inherited retinal dystrophy; essential in retinal visual cycle.",
        "RPGR": "X-linked retinitis pigmentosa gene; mutation causes progressive vision loss.",
        "INS": "Mutations lead to various forms of monogenic diabetes including neonatal diabetes.",
        "PDX1": "Essential for pancreatic development; mutation leads to MODY (Maturity Onset Diabetes of the Young)."
    }

# Footer
# Developed by Raksheet Gummakonda for Genovate
