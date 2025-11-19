import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, mean_squared_error, r2_score
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib
"""
1. Prepara i dati: Separa features (X) e target (y_clf, y_reg)
2. Preprocessing: Identifica feature numeriche e categoriche
3. Costruisce pipeline con preprocessor per classificazione e regressione
4. Addestra modelli: RandomForest per classificazione e regressione
5. Valuta i modelli: Accuracy, classification report, RMSE, R²
6. Salva i modelli e preprocessor
"""
CLASSIFIER_FILE = "classifier.pkl"
REGRESSOR_FILE = "regressor.pkl"
PREPROCESSOR_FILE = "preprocessor.pkl"

def build_preprocessor(numeric_features, categorical_features):
    # numeric: impute median + scale
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    # categorical: impute constant + onehot
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value=-1)),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    preprocessor = ColumnTransformer(transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])
    return preprocessor

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

