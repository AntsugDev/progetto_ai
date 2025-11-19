# ml_train_models.py
import os
import joblib
import warnings
import numpy as np
import pandas as pd
import pymysql
from typing import List
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             mean_squared_error, r2_score)

warnings.filterwarnings("ignore")

# ---------- CONFIG DB ----------
DB_CONF = {
    "host": "localhost",
    "user": "asugamele",           # aggiorna se necessario
    "password": "83Asugamele@",    # aggiorna se necessario
    "database": "projectAI",
    "cursorclass": pymysql.cursors.DictCursor
}

# ---------- OUTPUT FILE NAMES ----------
DATASET_CSV = "dataset_ml.csv"
CLASSIFIER_FILE = "rf_classifier.joblib"
REGRESSOR_FILE = "rf_regressor.joblib"
PREPROCESSOR_FILE = "preprocessor.joblib"

# ---------- Helper: load model table from DB ----------
def load_model_table() -> pd.DataFrame:
    conn = pymysql.connect(**DB_CONF)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM model")
            rows = cur.fetchall()
            df = pd.DataFrame(rows)
    finally:
        conn.close()
    return df

# ---------- Feature selection & engineering ----------
def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    - Selects relevant features, safely casts types, derives some computed columns if missing.
    - Returns cleaned dataframe ready for ML.
    """
    # Ensure expected columns exist (use safe get with defaults)
    # Core numeric features
    df['diff_reddito'] = pd.to_numeric(df.get('diff_reddito', df.get('reddito_mensie', np.nan)), errors='coerce')
    df['costo_auto'] = pd.to_numeric(df.get('costo_auto', np.nan), errors='coerce')
    df['anticipo'] = pd.to_numeric(df.get('anticipo', 0.0), errors='coerce')
    df['tan'] = pd.to_numeric(df.get('tan', 0.0), errors='coerce')
    df['nr_rate'] = pd.to_numeric(df.get('nr_rate', 0), errors='coerce')
    df['nr_figli'] = pd.to_numeric(df.get('nr_figli', 0), errors='coerce')
    df['eta'] = pd.to_numeric(df.get('eta', np.nan), errors='coerce')
    df['eta_veicolo'] = pd.to_numeric(df.get('eta_veicolo', 0), errors='coerce')
    # computed financials (if not present, compute)
    if 'importo_finanziato' not in df.columns or df['importo_finanziato'].isnull().all():
        # assume getImport logic: if nuovo_usato_id indicates new -> 10% of costo? In earlier PHP new -> 10% else full cost.
        # He used nuovo_usato flag as 0=new, 1=used; but in DB we have novo id. We'll approximate:
        df['importo_finanziato'] = df.apply(
            lambda r: r['costo_auto'] * 0.10 if int(r.get('nuovo_usato_id', 1)) == 1 and False else r['costo_auto'],
            axis=1
        )
        # To be safe, if importo_finanziato equals 0 or NaN, fallback to costo_auto
        df['importo_finanziato'] = df['importo_finanziato'].replace({0: np.nan})
        df['importo_finanziato'] = df['importo_finanziato'].fillna(df['costo_auto'])
    # rata/sostenibilita/coeff K may exist from your pipeline; compute if missing
    if 'rata' not in df.columns or df['rata'].isnull().all():
        # compute annuity monthly: use TAN stored as decimal (e.g. 0.05) or percent (5). Normalize later
        def compute_r(row):
            P = row['importo_finanziato'] if pd.notna(row['importo_finanziato']) else row['costo_auto']
            n = int(row['nr_rate']) if pd.notna(row['nr_rate']) and row['nr_rate']>0 else 1
            tan = float(row['tan']) if pd.notna(row['tan']) else 0.0
            if tan > 1:
                tan = tan/100.0
            r = tan/12.0
            if r == 0:
                return P / n
            denom = 1 - (1+r)**(-n)
            if denom == 0:
                return 0.0
            return P * (r/denom)
        df['rata'] = df.apply(compute_r, axis=1)
    if 'sostenibilita' not in df.columns or df['sostenibilita'].isnull().all():
        df['sostenibilita'] = df.apply(lambda r: r['rata']/r['diff_reddito'] if r['diff_reddito'] and r['diff_reddito']>0 else np.nan, axis=1)
    if 'coefficiente_k' not in df.columns or df['coefficiente_k'].isnull().all():
        df['coefficiente_k'] = df['sostenibilita'].apply(lambda s: s/0.20 if pd.notna(s) else np.nan)
    # Targets: decisione_AI (categorical) and rt (numeric)
    df['decisione_AI'] = df.get('decisione_AI', df.get('Decisione_finale', np.nan))
    df['rt'] = pd.to_numeric(df.get('rt', df.get('RT', np.nan)), errors='coerce')
    # Categorical columns (IDs)
    cat_cols = ['nuovo_usato_id','tipologia_auto_id','sesso_id','zona_id','neo_patentato_id','formula_acquisto_id']
    for c in cat_cols:
        if c not in df.columns:
            df[c] = np.nan
    # select final feature list
    features = [
        'diff_reddito','costo_auto','anticipo','tan','nr_rate','nr_figli','eta','eta_veicolo',
        'importo_finanziato','rata','sostenibilita','coefficiente_k',
        'nuovo_usato_id','tipologia_auto_id','sesso_id','zona_id','neo_patentato_id','formula_acquisto_id'
    ]
    # keep target columns
    keep = features + ['decisione_AI','rt']
    df2 = df[keep].copy()
    # drop rows with missing target
    df2 = df2[df2['decisione_AI'].notna() & df2['rt'].notna()]
    # reset index
    df2 = df2.reset_index(drop=True)
    return df2

# ---------- Build preprocessing pipeline ----------
def build_preprocessor(numeric_features: List[str], categorical_features: List[str]):
    # numeric: impute median + scale
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    # categorical: impute constant + onehot
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value=-1)),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse=False))
    ])
    preprocessor = ColumnTransformer(transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])
    return preprocessor

# ---------- Train & evaluate ----------
def train_and_evaluate(df: pd.DataFrame):
    # Features / targets
    X = df.drop(columns=['decisione_AI','rt'])
    y_clf = df['decisione_AI']
    y_reg = df['rt']

    numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
    # we treat id-like numeric categorical features as categorical: ensure they are strings
    cat_candidate = ['nuovo_usato_id','tipologia_auto_id','sesso_id','zona_id','neo_patentato_id','formula_acquisto_id']
    categorical_features = [c for c in cat_candidate if c in X.columns]

    # convert categorical columns to string (so OneHotEncoder treats them as categories)
    for c in categorical_features:
        X[c] = X[c].fillna(-1).astype(int).astype(str)

    # final numeric features exclude the categorical ones if numeric
    numeric_features = [c for c in numeric_features if c not in categorical_features]

    preprocessor = build_preprocessor(numeric_features, categorical_features)

    # Split
    X_train, X_test, y_clf_train, y_clf_test, y_reg_train, y_reg_test = train_test_split(
        X, y_clf, y_reg, test_size=0.2, random_state=42, stratify=y_clf
    )

    # ---------- CLASSIFIER ----------
    clf_pipeline = Pipeline(steps=[
        ('pre', preprocessor),
        ('clf', RandomForestClassifier(n_estimators=200, random_state=42))
    ])
    print("Training classifier...")
    clf_pipeline.fit(X_train, y_clf_train)
    y_pred = clf_pipeline.predict(X_test)
    acc = accuracy_score(y_clf_test, y_pred)
    print(f"Classifier Accuracy: {acc:.4f}")
    print("Classification report:")
    print(classification_report(y_clf_test, y_pred))
    print("Confusion matrix:")
    print(confusion_matrix(y_clf_test, y_pred))

    # cross-val (optional)
    cv_scores = cross_val_score(clf_pipeline, X, y_clf, cv=5, scoring='accuracy')
    print(f"Cross-val accuracy (5-fold): mean={cv_scores.mean():.4f} std={cv_scores.std():.4f}")

    # save classifier and preprocessor
    joblib.dump(clf_pipeline, CLASSIFIER_FILE)
    print(f"Saved classifier to {CLASSIFIER_FILE}")

    # ---------- REGRESSOR ----------
    reg_pipeline = Pipeline(steps=[
        ('pre', preprocessor),
        ('reg', RandomForestRegressor(n_estimators=200, random_state=42))
    ])
    print("Training regressor...")
    reg_pipeline.fit(X_train, y_reg_train)
    y_reg_pred = reg_pipeline.predict(X_test)
    rmse = mean_squared_error(y_reg_test, y_reg_pred, squared=False)
    r2 = r2_score(y_reg_test, y_reg_pred)
    print(f"Regressor RMSE: {rmse:.4f}, R2: {r2:.4f}")

    # save regressor
    joblib.dump(reg_pipeline, REGRESSOR_FILE)
    print(f"Saved regressor to {REGRESSOR_FILE}")

    # save preprocessor (already embedded in pipelines but export separately too)
    joblib.dump(preprocessor, PREPROCESSOR_FILE)
    print(f"Saved preprocessor to {PREPROCESSOR_FILE}")

    return clf_pipeline, reg_pipeline

# ---------- Main ----------
def main():
    print("Loading data from DB...")
    df_raw = load_model_table()
    print(f"Rows loaded: {len(df_raw)}")

    print("Preparing dataset...")
    df = prepare_features(df_raw)
    print(f"Rows after cleaning: {len(df)}")

    # save dataset
    df.to_csv(DATASET_CSV, index=False)
    print(f"Saved dataset to {DATASET_CSV}")

    # train
    clf, reg = train_and_evaluate(df)
    print("Training completed.")

if __name__ == "__main__":
    main()

