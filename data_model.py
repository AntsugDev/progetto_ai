# ==============================================
# ANALISI LOGICA DECISIONALE - PROJECT AI
# Lettura dati da MySQL + Calcolo sostenibilità
# ==============================================

import pymysql
import pandas as pd
import numpy as np

# ---------------------------
# 1️⃣ CONNESSIONE AL DATABASE
# ---------------------------
conn = pymysql.connect(
    host="localhost",
    user="asugamele",
    password="83Asugamele@",
    database="projectAI"
)

# -----------------------------------------------------
# 2️⃣ LETTURA DEI DATI
# -----------------------------------------------------
query = "SELECT * FROM model_data"
df = pd.read_sql(query, conn)
conn.close()

# Conversione dei campi numerici
numeric_cols = [
    "nr_figli", "reddito_mensile_netto", "altre_spese", "diff_reddito",
    "costo_auto", "anticipo", "tan", "nr_rate", "tot_finanziato_usata", "importo_fin3anni"
]
for c in numeric_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# -----------------------------------------------------
# 3️⃣ FUNZIONE DI CALCOLO RATA (formula francese)
# -----------------------------------------------------
def monthly_annuity(capital, annual_tan, n_months):
    """Calcola la rata mensile data la formula francese"""
    if pd.isna(capital) or pd.isna(n_months) or n_months == 0:
        return np.nan
    r = float(annual_tan) / 12.0 if not pd.isna(annual_tan) else 0.0
    if r == 0:
        return capital / n_months
    denom = 1 - (1 + r) ** (-int(n_months))
    return capital * (r / denom) if denom != 0 else np.nan

# -----------------------------------------------------
# 4️⃣ CALCOLO CAPITALI, RATE E SOSTENIBILITÀ
# -----------------------------------------------------
def compute_capitale(row):
    tf = row.get("tot_finanziato_usata", np.nan)
    if pd.notna(tf) and tf > 0:
        return tf
    costo, anticipo = row.get("costo_auto", np.nan), row.get("anticipo", np.nan)
    if pd.isna(costo):
        return np.nan
    if pd.notna(anticipo):
        if 0 <= anticipo <= 100 and anticipo < costo:
            return costo - (costo * (anticipo / 100.0))
        return max(costo - anticipo, 0)
    return costo

df["capitale_finanziato"] = df.apply(compute_capitale, axis=1)

df["rata_calcolata"] = df.apply(
    lambda r: monthly_annuity(r["capitale_finanziato"], r["tan"], r["nr_rate"]),
    axis=1
)

# diff_reddito (se non presente)
if "diff_reddito" not in df.columns or df["diff_reddito"].isnull().all():
    df["diff_reddito"] = df["reddito_mensile_netto"] - df["altre_spese"]

df["sostenibilita"] = df.apply(
    lambda r: r["rata_calcolata"] / r["diff_reddito"]
    if pd.notna(r["rata_calcolata"]) and r["diff_reddito"] > 0
    else np.nan,
    axis=1
)

# -----------------------------------------------------
# 5️⃣ COEFFICIENTE DI COMPENSAZIONE (K)
# -----------------------------------------------------
def calcola_coefficiente(row):
    reddito = row["diff_reddito"]
    rata = row["rata_calcolata"]
    sostenibilita = row["sostenibilita"]

    if pd.isna(sostenibilita):
        return np.nan, "Dati insufficienti"

    if sostenibilita <= 0.20:
        return 1.0, "Ottimale"
    elif sostenibilita >= 0.35:
        return round(sostenibilita / 0.20, 2), "Non concedibile"
    else:
        K = round(sostenibilita / 0.20, 2)
        if K <= 1.20:
            azione = "Piccolo anticipo (~5%)"
        elif K <= 1.40:
            azione = "Aumentare anticipo 10% o +12 rate"
        elif K <= 1.70:
            azione = "Aumentare anticipo 20% o +24 rate"
        else:
            azione = "Non sostenibile, rivedere piano"
        return K, azione

df[["coefficiente_K", "azione_correttiva"]] = df.apply(
    lambda r: pd.Series(calcola_coefficiente(r)), axis=1
)

# -----------------------------------------------------
# 6️⃣ DECISIONE FINALE (LOGICA GERARCHICA)
# -----------------------------------------------------
def decide_formula(row):
    reddito = row["diff_reddito"]
    sostenibilita = row["sostenibilita"]
    preferenza = "nuova" if row.get("nuovo_usato", 0) == 0 else "usata"
    anticipo = row["anticipo"]
    neopatentato = bool(row.get("neo_patentato", False))
    figli = row["nr_figli"]
    K = row["coefficiente_K"]

    # 🔒 1° livello: reddito e sostenibilità
    if sostenibilita >= 0.35 or K > 1.70:
        return "Non concedibile"

    # 💰 2° livello: reddito < 2500
    if reddito < 2500:
        if 0.21 <= sostenibilita <= 0.34:
            return "Fin3Anni" if preferenza == "nuova" else "Finanziamento"
        elif sostenibilita <= 0.20:
            return "Finanziamento"

    # 💼 3° livello: reddito >= 2500
    else:
        if 0.21 <= sostenibilita <= 0.34:
            return "Fin3Anni" if preferenza == "nuova" else "Finanziamento"
        elif sostenibilita <= 0.20:
            if preferenza == "nuova":
                if anticipo >= 0.20:
                    return "Bonifico"
                else:
                    return "Fin3Anni"
            else:
                return "Bonifico"

    # 🚗 4° livello: eccezioni personali
    if neopatentato and sostenibilita <= 0.20:
        return "Finanziamento"

    if figli >= 2:
        if reddito >= 2500 and sostenibilita <= 0.20:
            return "Bonifico"
        else:
            return "Finanziamento"

    return "Finanziamento"

df["formula_AI_decision"] = df.apply(decide_formula, axis=1)

# -----------------------------------------------------
# 7️⃣ ESPORTAZIONE RISULTATI
# -----------------------------------------------------
df.to_csv("ai_decision_output.csv", index=False, encoding="utf-8")
print("✅ File CSV salvato come 'ai_decision_output.csv'")

# Visualizza anteprima
print(df[[
    "cliente", "reddito_mensile_netto", "diff_reddito",
    "costo_auto", "rata_calcolata", "sostenibilita",
    "coefficiente_K", "azione_correttiva", "formula_AI_decision"
]].head())

# (opzionale) Salva anche in MySQL in una nuova tabella
conn = pymysql.connect(
    host="localhost",
    user="asugamele",
    password="83Asugamele@",
    database="projectAI"
)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS model_data_update")

# Salviamo la tabella
df.to_sql("model_data_update", con=conn, if_exists="replace", index=False)

conn.close()
print("✅ Dati salvati anche nella tabella MySQL 'model_data_update'")
