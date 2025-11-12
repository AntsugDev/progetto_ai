import pymysql
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ============================================================
# 1️⃣ Connessione al DB
# ============================================================
conn = pymysql.connect(
    host="localhost",
    user="asugamele",
    password="83Asugamele@",
    database="projectAI"
)

df = pd.read_sql("SELECT * FROM model_data", conn)
conn.close()


# ============================================================
# 2️⃣ Calcolo soglia dinamica del reddito
# ============================================================
R_min = df["diff_reddito"].min()
R_max = df["diff_reddito"].max()
R_medio = df["diff_reddito"].mean()
R_soglia = R_medio + (R_medio * (R_min / R_max))

print(f"Soglia dinamica reddito: {R_soglia:.2f} €")


# ============================================================
# 3️⃣ Funzioni di calcolo punteggi
# ============================================================

def score_income(reddito):
    """Punteggio reddito (scala 1-5)"""
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
    """Punteggio anticipo in percentuale"""
    if anticipo >= 25:
        return 1
    elif anticipo >= 15:
        return 2
    elif anticipo >= 5:
        return 3
    elif anticipo > 0:
        return 4
    else:
        return 5


def map_RE_continuous_to_discrete(value):
    """Mappa RE continuo su scala discreta 1-5"""
    if value <= 1.5: return 1
    elif value <= 2.4: return 2
    elif value <= 3.2: return 3
    elif value <= 4.0: return 4
    else: return 5


def map_RS(s):
    """Mappa sostenibilità su scala 1-5"""
    if s <= 0.15: return 1
    elif s <= 0.20: return 2
    elif s <= 0.29: return 3
    elif s <= 0.34: return 4
    else: return 5


def map_RD(figli, neopat):
    """Punteggio demografico"""
    if figli >= 3:
        base = 4
    elif figli == 2:
        base = 3
    elif figli == 1:
        base = 2
    else:
        base = 1
    if neopat:
        base += 1
    return min(base, 5)


# ============================================================
# 4️⃣ Calcolo coefficienti e punteggi
# ============================================================

results = []

for _, row in df.iterrows():
    reddito = float(row["diff_reddito"])
    anticipo = float(row["anticipo"])
    costo_auto = float(row["costo_auto"])
    tipo_auto = "nuova" if row["nuovo_usato"] == 0 else "usata"
    rata = float(row["rata"]) if "rata" in df.columns else 0
    nr_figli = int(row["nr_figli"])
    neopat = bool(row["neo_patentato"])

    # Calcolo sostenibilità e coefficiente K
    sostenibilita = rata / reddito if reddito > 0 else np.nan
    K = sostenibilita / 0.20 if sostenibilita > 0 else np.nan

    # Calcolo R_E
    R_income = score_income(reddito)
    R_anticipo = score_anticipo(anticipo) if tipo_auto == "nuova" else 1
    R_E_cont = 0.8 * R_income + 0.2 * R_anticipo
    R_E = map_RE_continuous_to_discrete(R_E_cont)

    # Calcolo R_S e R_D
    R_S = map_RS(sostenibilita)
    R_D = map_RD(nr_figli, neopat)

    # Calcolo R_t con nuovi pesi
    R_t = 0.5 * R_E + 0.3 * R_S + 0.2 * R_D
    R_t = round(R_t, 2)

    # Decisione AI
    if sostenibilita >= 0.35:
        decisione = "Non concedibile"
    elif 0.21 <= sostenibilita <= 0.29 and tipo_auto == "usata" and K > 1.2:
        decisione = "Zona grigia - Proporre anticipo o più rate"
    elif R_t <= 1.5:
        decisione = "Bonifico"
    elif R_t <= 2.4:
        decisione = "Bonifico / Fin3Anni"
    elif R_t <= 3.2:
        decisione = "Fin3Anni / Finanziamento"
    elif R_t <= 4.0:
        decisione = "Finanziamento (rivedere durata/anticipo)"
    else:
        decisione = "Non concedibile"

    results.append({
        "cliente": row["cliente"],
        "reddito": reddito,
        "costo_auto": costo_auto,
        "rata": rata,
        "sostenibilita": (sostenibilita*100),
        "coeff_K": K,
        "R_E": R_E,
        "R_S": R_S,
        "R_D": R_D,
        "R_t": R_t,
        "decisione_AI": decisione
    })

# ============================================================
# 5️⃣ Esportazione CSV finale
# ============================================================
output = pd.DataFrame(results)
output.to_csv("../file/ai_decision_score.csv", index=False, sep=";")
print("✅ File 'csv' generato correttamente.")

# ============================================================
# 6️⃣ Grafici base (opzionale)
# ============================================================

plt.figure(figsize=(6,4))
plt.scatter(output["reddito"], output["sostenibilita"])
plt.xlabel("Reddito netto (€)")
plt.ylabel("Sostenibilità (%)")
plt.title("Relazione reddito vs sostenibilità")
plt.grid(True)
plt.savefig("../img/ai_rata_vs_reddito_score.png", dpi=150)

plt.figure(figsize=(6,4))
plt.scatter(output["reddito"], output["coeff_K"])
plt.xlabel("Reddito netto (€)")
plt.ylabel("Coefficiente K")
plt.title("Coefficiente K rispetto al reddito")
plt.grid(True)
plt.savefig("../img/ai_coefficiente_K_score.png", dpi=150)
