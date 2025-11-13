# AI Decision Engine v9.2
# Allineato con logica PHP (Utils.php)
# Output: ai_decision.csv (solo CSV)

import pymysql
import pandas as pd
import numpy as np
import math
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

# -----------------------
# 1) Connessione DB
# -----------------------
conn = pymysql.connect(
    host="localhost",
    user="asugamele",
    password="83Asugamele@",
    database="projectAI"
)
df = pd.read_sql("SELECT * FROM model_data", conn)
conn.close()

# -----------------------
# 2) Normalizzazione colonne utili
# -----------------------
numeric_cols = [
    "nr_figli", "reddito_mensile_netto", "altre_spese", "diff_reddito",
    "costo_auto", "anticipo", "tan", "nr_rate", "tot_finanziato_usata", "importo_fin3anni"
]
for c in numeric_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Se manca diff_reddito, lo calcola
if "diff_reddito" not in df.columns or df["diff_reddito"].isnull().all():
    if "reddito_mensile_netto" in df.columns and "altre_spese" in df.columns:
        df["diff_reddito"] = df["reddito_mensile_netto"] - df["altre_spese"]
    else:
        df["diff_reddito"] = np.nan

# -----------------------
# 3) Funzioni di calcolo
# -----------------------
def compute_capitale(row):
    tf = row.get("tot_finanziato_usata", np.nan)
    if pd.notna(tf) and tf > 0:
        return float(tf)

    costo = row.get("costo_auto", np.nan)
    anticipo = row.get("anticipo", np.nan)
    if pd.isna(costo):
        return np.nan

    if pd.isna(anticipo) or anticipo == 0:
        return float(costo)

    try:
        anticipo_val = float(anticipo)
    except Exception:
        return float(costo)

    if 0 < anticipo_val <= 1:
        financed = costo * (1 - anticipo_val)
    elif 1 < anticipo_val <= 100:
        financed = costo * (1 - anticipo_val / 100.0)
    else:
        financed = costo - anticipo_val

    return max(0.0, float(financed))

def monthly_annuity(capital, annual_tan, n_months):
    if pd.isna(capital) or pd.isna(n_months) or int(n_months) <= 0:
        return np.nan
    capital = float(capital)
    n = int(n_months)
    if pd.isna(annual_tan):
        annual_tan = 0.0
    else:
        annual_tan = float(annual_tan)
    if annual_tan > 1:
        annual_tan = annual_tan / 100.0
    r = annual_tan / 12.0
    if r == 0:
        return capital / n
    denom = 1 - (1 + r) ** (-n)
    if denom == 0:
        return np.nan
    return capital * (r / denom)

# -----------------------
# 4) Calcolo soglia reddito dinamica
# -----------------------
valid_redditi = df["diff_reddito"].dropna()
if len(valid_redditi) > 0:
    R_min = valid_redditi.min()
    R_max = valid_redditi.max() if valid_redditi.max() != 0 else 1
    R_medio = valid_redditi.mean()
    R_soglia = R_medio + (R_medio * (R_min / R_max))
else:
    R_soglia = 2500.0

if pd.isna(R_soglia) or R_soglia <= 0:
    R_soglia = 2500.0

# -----------------------
# 5) Funzioni punteggio
# -----------------------
def score_income(reddito):
    if pd.isna(reddito):
        return 3
    if reddito >= R_soglia:
        return 1
    elif reddito >= (R_soglia * 0.8):
        return 2
    elif reddito >= (R_soglia * 0.6):
        return 3
    elif reddito >= (R_soglia * 0.4):
        return 4
    else:
        return 5

def score_anticipo(anticipo):
    if pd.isna(anticipo):
        return 5
    try:
        a = float(anticipo)
    except:
        return 5
    if 0 < a <= 1:
        a_pct = a * 100.0
    elif 1 < a <= 100:
        a_pct = a
    else:
        a_pct = 0.0
    if a_pct >= 25:
        return 1
    elif a_pct >= 15:
        return 2
    elif a_pct >= 5:
        return 3
    elif a_pct > 0:
        return 4
    else:
        return 5

def map_RE_continuous(value):
    if pd.isna(value):
        return 3
    if value <= 1.5: return 1
    elif value <= 2.4: return 2
    elif value <= 3.2: return 3
    elif value <= 4.0: return 4
    else: return 5

def map_RS(s):
    if pd.isna(s):
        return 3
    if s <= 0.15: return 1
    elif s <= 0.20: return 2
    elif s <= 0.29: return 3
    elif s <= 0.34: return 4
    else: return 5

def map_RD(figli, neopat):
    f = int(figli) if pd.notna(figli) else 0
    base = 1
    if f >= 3:
        base = 4
    elif f == 2:
        base = 3
    elif f == 1:
        base = 2
    if neopat:
        base += 1
    return min(base, 5)

# -----------------------
# 6) Calcolo per ogni record
# -----------------------
rows_out = []
for idx, row in df.iterrows():
    cliente = row.get("cliente", idx)
    tipo_auto = "nuova" if row.get("nuovo_usato", 0) == 0 else "usata"
    reddito = row.get("diff_reddito", np.nan)
    anticipo = row.get("anticipo", np.nan)
    tan = row.get("tan", 0.0)
    nr_rate = row.get("nr_rate", np.nan)
    figli = row.get("nr_figli", 0)
    neopat = bool(row.get("neo_patentato", False))

    capitale = compute_capitale(row)
    rata = monthly_annuity(capitale, tan, nr_rate)

    if pd.notna(rata) and pd.notna(reddito) and reddito > 0:
        sostenibilita = rata / reddito
        # coefficiente K aggiornato come nel PHP
        if sostenibilita <= 0:
            K = np.nan
        else:
            K = round((sostenibilita / 0.20), 2)
    else:
        sostenibilita = np.nan
        K = np.nan

    # punteggi
    R_income = score_income(reddito)
    R_anticipo = score_anticipo(anticipo) if tipo_auto == "nuova" else 1
    R_E_cont = round(0.8 * R_income + 0.2 * R_anticipo, 2)
    R_E = map_RE_continuous(R_E_cont)
    R_S = map_RS(sostenibilita)
    R_D = map_RD(figli, neopat)

    # formula R_T (stesso arrotondamento PHP)
    R_T = round((0.5 * R_E) + (0.3 * R_S) + (0.2 * R_D), 1)

    # decisione semplificata
    if pd.notna(sostenibilita) and sostenibilita >= 0.35:
        decisione = "Non concedibile"
    elif 0.21 <= sostenibilita <= 0.29 and tipo_auto == "usata" and K > 1.2:
        decisione = "Zona grigia - simulare anticipo/durata"
    else:
        if R_T <= 1.5:
            decisione = "Bonifico"
        elif R_T <= 2.4:
            decisione = "Bonifico / Fin3Anni"
        elif R_T <= 3.2:
            decisione = "Fin3Anni / Finanziamento"
        elif R_T <= 4.0:
            decisione = "Finanziamento (rivedere durata)"
        else:
            decisione = "Non concedibile"

    rows_out.append({
        "cliente": cliente,
        "tipo_auto": tipo_auto,
        "reddito_netto": round(float(reddito), 2) if pd.notna(reddito) else None,
        "anticipo": anticipo,
        "tan": tan,
        "nr_rate": nr_rate,
        "capitale_finanziato": round(float(capitale), 2) if pd.notna(capitale) else None,
        "rata_calcolata": round(float(rata), 2) if pd.notna(rata) else None,
        "sostenibilita": round(float(sostenibilita), 4) if pd.notna(sostenibilita) else None,
        "coeff_K": K,
        "R_E": R_E,
        "R_S": R_S,
        "R_D": R_D,
        "R_T": R_T,
        "decisione_AI": decisione
    })

# -----------------------
# 7) Export CSV
# -----------------------
out_df = pd.DataFrame(rows_out)
out_df.to_csv("../file/ai_decision.csv", index=False, sep=";")
print("✅ ai_decision.csv generato correttamente (righe:", len(out_df), ")")

