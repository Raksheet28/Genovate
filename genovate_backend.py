# genovate_backend.py

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Load or simulate data (expanded for Genovate)
def load_data():
    np.random.seed(42)
    num_samples = 300

    organ_gene_map = {
        "Kidney": ["PKD1", "PKD2", "PKHD1"],
        "Liver": ["ATP7B", "FAH", "TTR"],
        "Heart": ["MYBPC3", "TNNT2", "MYH7"],
        "Lung": ["CFTR", "AATD"],
        "Brain": ["HTT", "MECP2", "SCN1A"],
        "Eye": ["RPE65", "RPGR"],
        "Pancreas": ["INS", "PDX1"]
    }

    delivery_methods = ['LNP', 'Electroporation']

    all_data = []

    for _ in range(num_samples):
        organ = np.random.choice(list(organ_gene_map.keys()))
        mutation = np.random.choice(organ_gene_map[organ])
        method = np.random.choice(delivery_methods)

        if method == 'LNP':
            efficiency = np.clip(np.random.normal(0.72, 0.05), 0, 1)
            off_target = np.clip(np.random.normal(0.07, 0.02), 0, 1)
            viability = np.clip(np.random.normal(0.92, 0.03), 0, 1)
            cost = np.random.randint(1, 3)
        else:
            efficiency = np.clip(np.random.normal(0.85, 0.04), 0, 1)
            off_target = np.clip(np.random.normal(0.12, 0.03), 0, 1)
            viability = np.clip(np.random.normal(0.75, 0.05), 0, 1)
            cost = np.random.randint(3, 5)

        all_data.append([mutation, organ, method, efficiency, off_target, viability, cost])

    df = pd.DataFrame(all_data, columns=["Mutation", "TargetOrgan", "DeliveryMethod", "Efficiency", "OffTargetRisk", "CellViability", "Cost"])
    return df

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

# Footer
# Developed by Raksheet Gummakonda for Genovate
