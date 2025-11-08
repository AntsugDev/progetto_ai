# =====================================================
#  PROJECT AI - DECISION ENGINE v6
#  Con simulazione e grafici automatici
# =====================================================

import pymysql
import pandas as pd
import numpy as np
import math
import matplotlib
matplotlib.use('Agg')  # ✅ necessario per generare immagini senza GUI
import matplotlib.pyplot as plt

# -----------------------------------------------------
# 1️⃣ CONNESSIONE AL DATABASE
# -----------------------------------------------------
conn = pymysql.connect(
    host="localhost",
    user="asugamele",
    password="83Asugamele@",
    database="projectAI"
)

query = "SELECT * FROM model_data"
df = pd.read_sql(query, conn)
conn.close()

# -----------------------------------------------------
# 2️⃣ NORMALIZZAZIONE DATI
# -----------------------------------------------------
numeric_cols = [
    "nr_figli", "reddito_mensile_netto", "altre_spese", "diff_reddito",
    "costo_auto", "anticipo", "tan", "nr_rate", "tot_finanziato_usata", "importo_fin3anni"
]
for c in numeric_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

if "diff_reddito" not in df.columns or df["diff_reddito"].isnull().all():
    df["diff_reddito"] = df["reddito_mensile_netto"] - df["altre_spese"]

# -----------------------------------------------------
# 3️⃣ CALCOLO RATA (formula francese)
# -----------------------------------------------------
def monthly_annuity(capital, annual_tan, n_months):
    if pd.isna(capital) or pd.isna(n_months) or n_months == 0:
        return np.nan
    r = float(annual_tan) / 12.0
    if r == 0:
        return capital / n_months
    denom = 1 - (1 + r) ** (-int(n_months))
    return capital * (r / denom) if denom != 0 else np.nan

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
df["sostenibilita"] = df.apply(
    lambda r: r["rata_calcolata"] / r["diff_reddito"]
    if pd.notna(r["rata_calcolata"]) and r["diff_reddito"] > 0
    else np.nan,
    axis=1
)

# -----------------------------------------------------
# 4️⃣ COEFFICIENTE K + SIMULAZIONE AUTOMATICA
# -----------------------------------------------------
def calcola_coefficiente(row):
    reddito = row["diff_reddito"]
    rata = row["rata_calcolata"]
    sostenibilita = row["sostenibilita"]

    if pd.isna(sostenibilita):
        return np.nan, "Dati insufficienti", np.nan, np.nan

    if sostenibilita <= 0.20:
        return 1.0, "Ottimale", 0, 0
    elif sostenibilita >= 0.35:
        return round(sostenibilita / 0.20, 2), "Non concedibile", np.nan, np.nan
    else:
        K = round(sostenibilita / 0.20, 2)
        target_rata = 0.20 * reddito
        delta_rata = rata - target_rata

        anticipo_extra = round((K - 1) * 10, 1)  # ogni +0.1 su K = +10% anticipo
        rate_extra = int(12 * (K - 1))           # ogni +0.1 su K = +12 rate

        if K <= 1.20:
            azione = "Piccolo anticipo (~5%)"
        elif K <= 1.40:
            azione = f"Aumentare anticipo +10% o +{rate_extra} rate"
        elif K <= 1.70:
            azione = f"Aumentare anticipo +20% o +{rate_extra} rate"
        else:
            azione = "Non sostenibile, rivedere piano"

        return K, azione, anticipo_extra, rate_extra

df[["coefficiente_K", "azione_correttiva", "anticipo_extra_%", "rate_extra"]] = df.apply(
    lambda r: pd.Series(calcola_coefficiente(r)), axis=1
)

# -----------------------------------------------------
# 5️⃣ DECISIONE LOGICA GERARCHICA
# -----------------------------------------------------
def decide_formula(row):
    reddito = row["diff_reddito"]
    sostenibilita = row["sostenibilita"]
    anticipo = row["anticipo"]
    preferenza = "nuova" if row.get("nuovo_usato", 0) == 0 else "usata"
    neopatentato = bool(row.get("neo_patentato", False))
    figli = row["nr_figli"]
    K = row["coefficiente_K"]

    if sostenibilita >= 0.35 or (pd.notna(K) and K > 1.7):
        return "Non concedibile"
    if neopatentato and sostenibilita <= 0.20:
        return "Finanziamento"
    if reddito < 2500:
        if 0.21 <= sostenibilita <= 0.34:
            return "Fin3Anni" if preferenza == "nuova" else "Finanziamento"
        elif sostenibilita <= 0.20:
            return "Finanziamento"
    else:
        if 0.21 <= sostenibilita <= 0.34:
            return "Fin3Anni" if preferenza == "nuova" else "Finanziamento"
        elif sostenibilita <= 0.20:
            if preferenza == "nuova":
                return "Fin3Anni" if anticipo >= 0.25 else "Bonifico"
            else:
                return "Bonifico"
    if figli >= 2:
        if reddito >= 2500 and sostenibilita <= 0.20:
            return "Bonifico"
        else:
            return "Finanziamento"
    return "Finanziamento"

df["formula_AI_decision"] = df.apply(decide_formula, axis=1)

# -----------------------------------------------------
# 6️⃣ ESPORTAZIONE RISULTATI
# -----------------------------------------------------
df.to_csv("ai_decision.csv", index=False, encoding="utf-8")
print("✅ File CSV salvato come 'ai_decision.csv'")

# -----------------------------------------------------
# 7️⃣ VISUALIZZAZIONE AUTOMATICA
# -----------------------------------------------------
plt.figure(figsize=(10, 6))
plt.scatter(df["diff_reddito"], df["rata_calcolata"],
            c=df["sostenibilita"], cmap="coolwarm", s=80, alpha=0.8, edgecolors='k')
plt.axhline(y=0.20 * df["diff_reddito"].mean(), color='green', linestyle='--', label='Soglia 20%')
plt.axhline(y=0.35 * df["diff_reddito"].mean(), color='red', linestyle='--', label='Soglia 35%')
plt.title("Rata vs Reddito con Sostenibilità")
plt.xlabel("Reddito netto (€)")
plt.ylabel("Rata mensile (€)")
plt.legend()
plt.grid(True)
plt.savefig("img/ai_rata_vs_reddito.png", dpi=300)
print("📊 Grafico 'ai_rata_vs_reddito.png' generato")

# Coefficiente K bar chart
plt.figure(figsize=(10, 5))
plt.bar(df.index, df["coefficiente_K"], color="skyblue", edgecolor="k")
plt.axhline(y=1.0, color='green', linestyle='--', label='K=1 (Ottimale)')
plt.axhline(y=1.7, color='red', linestyle='--', label='K=1.7 (Limite)')
plt.title("Distribuzione del coefficiente K")
plt.xlabel("Clienti")
plt.ylabel("Valore di K")
plt.legend()
plt.tight_layout()
plt.savefig("img/ai_coefficiente_K.png", dpi=300)
print("📈 Grafico 'ai_coefficiente_K.png' generato")
