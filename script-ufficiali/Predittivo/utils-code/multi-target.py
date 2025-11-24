import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# Genera dati sintetici per case
np.random.seed(42)
n_samples = 1000

# Features: superficie, numero camere, distanza dal centro, anno costruzione
superficie = np.random.randint(50, 250, n_samples)
n_camere = np.random.randint(1, 6, n_samples)
distanza_centro = np.random.uniform(0.5, 30, n_samples)
anno_costruzione = np.random.randint(1970, 2023, n_samples)

# Target 1: Prezzo casa (in migliaia di euro)
prezzo = (
    superficie * 2.5 + 
    n_camere * 30 + 
    (2023 - anno_costruzione) * -0.5 +
    distanza_centro * -3 +
    np.random.normal(0, 30, n_samples)
)

# Target 2: Giorni per vendere
giorni_vendita = (
    50 + 
    (prezzo / 10) * 0.5 +
    distanza_centro * 2 +
    np.random.normal(0, 15, n_samples)
)
giorni_vendita = np.clip(giorni_vendita, 10, 300)

# Crea DataFrame
df = pd.DataFrame({
    'superficie': superficie,
    'n_camere': n_camere,
    'distanza_centro': distanza_centro,
    'anno_costruzione': anno_costruzione,
    'prezzo': prezzo,
    'giorni_vendita': giorni_vendita
})

print("=== DATASET ===")
print(df.head(10))
print(f"\nShape: {df.shape}")

# Separa features e targets
X = df[['superficie', 'n_camere', 'distanza_centro', 'anno_costruzione']]
# Combina entrambi i target in una matrice
y = df[['prezzo', 'giorni_vendita']]

print(f"\nX shape: {X.shape}")
print(f"y shape: {y.shape} (2 target simultanei)")

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("\n=== TRAINING CON MULTIOUTPUTREGRESSOR ===")
print("Addestra un modello per ogni target in modo coordinato")

# Crea il MultiOutputRegressor con XGBoost come base estimator
multi_model = MultiOutputRegressor(
    XGBRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
)

# Addestra su entrambi i target contemporaneamente
multi_model.fit(X_train, y_train)

# Predizioni (restituisce una matrice con entrambi i target)
predictions = multi_model.predict(X_test)

# Separa le predizioni per target
pred_prezzo = predictions[:, 0]
pred_giorni = predictions[:, 1]

# Valutazione
print("\n=== RISULTATI TARGET 1: PREZZO ===")
print(f"MAE: {mean_absolute_error(y_test['prezzo'], pred_prezzo):.2f} k€")
print(f"R²: {r2_score(y_test['prezzo'], pred_prezzo):.3f}")

print("\n=== RISULTATI TARGET 2: GIORNI VENDITA ===")
print(f"MAE: {mean_absolute_error(y_test['giorni_vendita'], pred_giorni):.2f} giorni")
print(f"R²: {r2_score(y_test['giorni_vendita'], pred_giorni):.3f}")

# Esempio di predizione su nuovi dati
print("\n=== PREDIZIONE SU NUOVE CASE ===")
nuove_case = pd.DataFrame({
    'superficie': [100, 180, 75],
    'n_camere': [2, 4, 1],
    'distanza_centro': [5.0, 15.0, 2.0],
    'anno_costruzione': [2010, 1985, 2020]
})

# Una singola chiamata restituisce entrambi i target
pred_nuove = multi_model.predict(nuove_case)

for i in range(len(nuove_case)):
    print(f"\nCasa {i+1}:")
    print(f"  Caratteristiche: {nuove_case.iloc[i].to_dict()}")
    print(f"  Prezzo previsto: {pred_nuove[i, 0]:.2f} k€")
    print(f"  Giorni vendita previsti: {pred_nuove[i, 1]:.0f} giorni")

# Feature importance per ogni target
print("\n=== FEATURE IMPORTANCE ===")
print("\nTarget 1 (Prezzo):")
for feature, importance in zip(X.columns, multi_model.estimators_[0].feature_importances_):
    print(f"  {feature}: {importance:.3f}")

print("\nTarget 2 (Giorni Vendita):")
for feature, importance in zip(X.columns, multi_model.estimators_[1].feature_importances_):
    print(f"  {feature}: {importance:.3f}")

# Informazioni sul modello
print("\n=== INFO MODELLO ===")
print(f"Numero di estimatori (uno per target): {len(multi_model.estimators_)}")
print(f"Tipo base estimator: {type(multi_model.estimators_[0]).__name__}")

# Confronto: predizioni separate vs insieme
print("\n=== CONFRONTO APPROCCI ===")
print("✓ MultiOutputRegressor: predice entrambi i target con una chiamata")
print("✓ Gestisce automaticamente la coordinazione tra modelli")
print("✓ Interfaccia semplificata per training e predizione")
print("✓ Ogni target ha comunque il suo modello XGBoost interno")