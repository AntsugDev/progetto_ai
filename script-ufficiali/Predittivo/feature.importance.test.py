import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

# Supponiamo df già pronto con tutte le colonne
# df = pd.DataFrame(...)

X = df[['eta','neo_patentato','nr_figli','reddito_mensile','altre_spese',
        'sesso','zona','tipologia_auto','nuovo_usato','costo_auto','eta_veicolo',
        'anticipo','formula_acquisto','nr_rate','importo_finanziato','rata',
        'sostenibilita','coefficiente_k','re','rs','rd','rt','is_simulation']]
y_raw = df['decisione_AI']

# LabelEncoder sul target
le = LabelEncoder()
y = le.fit_transform(y_raw)

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Preprocessing
toConvert = ['neo_patentato','sesso','zona','tipologia_auto','nuovo_usato',
             'formula_acquisto','is_simulation']

process = ColumnTransformer(
    transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), toConvert)],
    remainder="passthrough"
)

# Modello XGBoost
model = Pipeline([
    ("preprocess", process),
    ("xgb", XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="mlogloss"
    ))
])

# Fit
model.fit(X_train, y_train)

# -------------------------------------------------
# 1️⃣ Feature importance delle colonne finali
xgb_model = model.named_steps['xgb']
columns_encoded = model.named_steps['preprocess'].get_feature_names_out()
importances = xgb_model.feature_importances_

feat_importance = pd.DataFrame({
    'feature': columns_encoded,
    'importance': importances
}).sort_values(by='importance', ascending=False)

print("-"*10, "Feature importance (colonne OneHotEncoder)", "-"*10)
print(feat_importance.head(20))

# -------------------------------------------------
# 2️⃣ Grafico
plt.figure(figsize=(10,6))
plt.barh(feat_importance['feature'], feat_importance['importance'])
plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("Feature Importance - XGBoost")
plt.gca().invert_yaxis()
plt.show()

# -------------------------------------------------
# 3️⃣ Aggregazione per feature originale
# esempio: somma tutte le colonne generate da 'sesso' in una sola
import re
original_features = X.columns
agg_importance = {}
for feat in original_features:
    # somma importances delle colonne che iniziano con il nome della feature
    pattern = re.compile(f"^{re.escape(feat)}")
    agg_importance[feat] = importances[[i for i, col in enumerate(columns_encoded) if pattern.match(col)]].sum()

agg_df = pd.DataFrame({
    'feature': list(agg_importance.keys()),
    'importance': list(agg_importance.values())
}).sort_values(by='importance', ascending=False)

print("-"*10, "Feature importance (aggregata per feature originale)", "-"*10)
print(agg_df)
