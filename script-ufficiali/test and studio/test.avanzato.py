#il test serve per dimostrare le differenze tra Label Encoder e OneHot Encoder

import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Dataset
df = pd.DataFrame({
    "colore": ["rosso", "blu", "verde"],
    "carburante": ["benzina", "diesel", "elettrico"],
    "km": [100, 50, 10],
    "esci": [1, 0, 1]
})

X = df[["colore", "carburante", "km"]]
y = df["esci"]

# Encoder per categorie
categorical_features = ["colore", "carburante"]

preprocess = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
    ],
    remainder="passthrough"   # lascia passare km senza modifiche
)

# Pipeline = preprocessing + modello
model = Pipeline(steps=[
    ("preprocess", preprocess),
    ("rf", RandomForestClassifier())
])

model.fit(X, y)

# Importanze delle feature
rf = model["rf"]
print("Importanza features:", rf.feature_importances_)

test = pd.DataFrame({
    'colore': ['rosso'],
    'carburante': ['diesel'],
    'km': [100]
})
# --- Predizione corretta ---
p = model.predict(test)

print("\n" + "*"*60)
print(f"Predizione = {p[0]}")
