# =====================================================
#  PROJECT AI - DECISION ENGINE v8
#  Con simulazione, grafici, report PDF e Risk Index
# =====================================================

import pymysql
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # necessario per ambiente server/headless
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

# -----------------------
# 1) Connessione al DB
# -----------------------
conn = pymysql.connect(
    host="localhost",
    user="asugamele",
    password="83Asugamele@",
    database="projectAI"
)

query = "SELECT * FROM model_data"
df = pd.read_sql(query, conn)
conn.close()

# -----------------------
# 2) Normalizzazione
# -----------------------
numeric_cols = [
    "nr_figli", "reddito_mensile_netto", "altre_spese", "diff_reddito",
    "costo_auto", "anticipo", "tan", "nr_rate", "tot_finanziato_usata", "importo_fin3anni"
]
for c in numeric_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

if "diff_reddito" not in df.columns or df["diff_reddito"].isnull().all():
    df["diff_reddito"] = df["reddito_mensile_netto"] - df["altre_spese"]

# -----------------------
# 3) Funzioni finanziarie
# -----------------------
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
        # anticipo come percentuale se 0..100 e coerente, altrimenti come valore assoluto
        if 0 <= anticipo <= 100 and anticipo < costo:
            return costo - (costo * (anticipo / 100.0))
        return max(costo - anticipo, 0)
    return costo

df["capitale_finanziato"] = df.apply(compute_capitale, axis=1)
df["rata_calcolata"] = df.apply(
    lambda r: monthly_annuity(r["capitale_finanziato"], r.get("tan", np.nan), r.get("nr_rate", np.nan)),
    axis=1
)

df["sostenibilita"] = df.apply(
    lambda r: r["rata_calcolata"] / r["diff_reddito"]
    if pd.notna(r["rata_calcolata"]) and pd.notna(r["diff_reddito"]) and r["diff_reddito"] > 0
    else np.nan,
    axis=1
)

# -----------------------
# 4) Coefficiente K + simulazione
# -----------------------
def calcola_coefficiente(row):
    reddito = row.get("diff_reddito", np.nan)
    rata = row.get("rata_calcolata", np.nan)
    sostenibilita = row.get("sostenibilita", np.nan)

    if pd.isna(sostenibilita):
        return pd.Series([np.nan, "Dati insufficienti", np.nan, np.nan])

    if sostenibilita <= 0.20:
        return pd.Series([1.0, "Ottimale", 0, 0])
    elif sostenibilita >= 0.35:
        return pd.Series([round(sostenibilita / 0.20, 2), "Non concedibile", np.nan, np.nan])
    else:
        K = round(sostenibilita / 0.20, 2)
        # stima semplificata per anticipo/rate extra
        anticipo_extra = round(max(0.0, (K - 1) * 10), 1)  # es. K=1.4 -> 4.0%
        rate_extra = int(max(0, round(12 * (K - 1))))      # es. K=1.4 -> 4 or 5 months -> int
        if K <= 1.20:
            azione = "Piccolo anticipo (~5%)"
        elif K <= 1.40:
            azione = f"Aumentare anticipo +10% o +{rate_extra} rate"
        elif K <= 1.70:
            azione = f"Aumentare anticipo +20% o +{rate_extra} rate"
        else:
            azione = "Non sostenibile, rivedere piano"
        return pd.Series([K, azione, anticipo_extra, rate_extra])

df[["coefficiente_K", "azione_correttiva", "anticipo_extra_%", "rate_extra"]] = df.apply(calcola_coefficiente, axis=1)

# -----------------------
# 5) Decisione gerarchica
# -----------------------
def decide_formula(row):
    reddito = row.get("diff_reddito", np.nan)
    sostenibilita = row.get("sostenibilita", np.nan)
    anticipo = row.get("anticipo", np.nan)
    preferenza = "nuova" if row.get("nuovo_usato", 0) == 0 else "usata"
    neopatentato = bool(row.get("neo_patentato", False))
    figli = int(row.get("nr_figli", 0)) if not pd.isna(row.get("nr_figli")) else 0
    K = row.get("coefficiente_K", np.nan)

    # 1) limite non concedibile
    if (pd.notna(sostenibilita) and sostenibilita >= 0.35) or (pd.notna(K) and K > 1.7):
        return "Non concedibile"

    # 2) neopatentato
    if neopatentato and pd.notna(sostenibilita) and sostenibilita <= 0.20:
        return "Finanziamento"

    # 3) reddito basso
    if pd.notna(reddito) and reddito < 2500:
        if pd.notna(sostenibilita) and 0.21 <= sostenibilita <= 0.34:
            return "Fin3Anni" if preferenza == "nuova" else "Finanziamento"
        if pd.notna(sostenibilita) and sostenibilita <= 0.20:
            return "Finanziamento"

    # 4) reddito >= 2500
    if pd.notna(reddito) and reddito >= 2500:
        if pd.notna(sostenibilita) and 0.21 <= sostenibilita <= 0.34:
            return "Fin3Anni" if preferenza == "nuova" else "Finanziamento"
        if pd.notna(sostenibilita) and sostenibilita <= 0.20:
            if preferenza == "nuova":
                # preferenza nuova: valutiamo anticipo per 3anni/bonifico
                if pd.notna(anticipo) and anticipo >= 0.25:
                    return "Fin3Anni"
                else:
                    return "Bonifico"
            else:
                return "Bonifico"

    # 5) famiglia numerosa
    if figli >= 2:
        if pd.notna(reddito) and reddito >= 2500 and pd.notna(sostenibilita) and sostenibilita <= 0.20:
            return "Bonifico"
        else:
            return "Finanziamento"

    return "Finanziamento"

df["formula_AI_decision"] = df.apply(decide_formula, axis=1)

# -----------------------
# 6) Risk Index 1..5
# -----------------------
def compute_risk_index(row):
    s = row.get("sostenibilita", np.nan)
    K = row.get("coefficiente_K", np.nan)
    neopat = bool(row.get("neo_patentato", False))
    figli = int(row.get("nr_figli", 0)) if not pd.isna(row.get("nr_figli")) else 0

    if pd.isna(s):
        return np.nan

    # base index
    if s >= 0.35 or (pd.notna(K) and K > 1.7):
        idx = 5
    elif (pd.notna(K) and K > 1.4) or s > 0.30:
        idx = 4
    elif 0.21 <= s <= 0.34:
        idx = 3
    elif 0.15 < s <= 0.20:
        idx = 2
    else:  # s <= 0.15
        idx = 1

    # adjusters
    if neopat:
        idx += 1
    if figli >= 2:
        idx += 1

    # cap between 1 and 5
    if idx < 1: idx = 1
    if idx > 5: idx = 5
    return idx

df["risk_index"] = df.apply(compute_risk_index, axis=1)

# -----------------------
# 7) Export CSV (nome fisso richiesto)
# -----------------------
out_csv = "file/ai_decision.csv"
df.to_csv(out_csv, index=False, encoding="utf-8")
print(f"✅ File CSV salvato come '{out_csv}'")

# -----------------------
# 8) Grafici
# -----------------------
# Scatter rata vs reddito (color = sostenibilita)
plt.figure(figsize=(10, 6))
sc = plt.scatter(df["diff_reddito"], df["rata_calcolata"],
                 c=df["sostenibilita"], cmap="coolwarm", s=80, alpha=0.9, edgecolors='k')
cbar = plt.colorbar(sc)
cbar.set_label("Sostenibilità (rata/diff_reddito)")
# plot soglie relative alla media (visive)
mean_reddito = df["diff_reddito"].mean()
plt.axhline(y=0.20 * mean_reddito, color='green', linestyle='--', label='Soglia 20% (media)')
plt.axhline(y=0.35 * mean_reddito, color='red', linestyle='--', label='Soglia 35% (media)')
plt.title("Rata vs Reddito con Sostenibilità")
plt.xlabel("Reddito netto disponibile (€)")
plt.ylabel("Rata mensile (€)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("img/ai_rata_vs_reddito.png", dpi=300)
plt.close()
print("📊 Grafico 'ai_rata_vs_reddito.png' generato")

# K bar chart
plt.figure(figsize=(10, 5))
plt.bar(df.index, df["coefficiente_K"].fillna(0), color="skyblue", edgecolor="k")
plt.axhline(y=1.0, color='green', linestyle='--', label='K=1 (Ottimale)')
plt.axhline(y=1.7, color='red', linestyle='--', label='K=1.7 (Limite)')
plt.title("Distribuzione del coefficiente K")
plt.xlabel("Record")
plt.ylabel("Valore di K")
plt.legend()
plt.tight_layout()
plt.savefig("img/ai_coefficiente_K.png", dpi=300)
plt.close()
print("📈 Grafico 'ai_coefficiente_K.png' generato")

# -----------------------
# 9) Report PDF (con risk index)
# -----------------------
doc = SimpleDocTemplate("file/ai_report.pdf", pagesize=A4)
styles = getSampleStyleSheet()
story = []

story.append(Paragraph("<b>AI Decision Report</b>", styles['Title']))
story.append(Spacer(1, 8))
story.append(Paragraph("Sintesi dei risultati del motore decisionale AI per la valutazione di sostenibilità finanziaria.", styles['Normal']))
story.append(Spacer(1, 12))

# Tabella con risk index
cols = ["cliente", "diff_reddito", "costo_auto", "rata_calcolata", "sostenibilita", "coefficiente_K", "risk_index", "formula_AI_decision"]
table_data = [cols] + df[cols].round(3).astype(str).values.tolist()
table = Table(table_data, repeatRows=1)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3E7CB1")),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('GRID', (0, 0), (-1, -1), 0.25, colors.gray),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTSIZE', (0,0), (-1,-1), 8),
]))
story.append(table)
story.append(Spacer(1, 16))

story.append(Paragraph("<b>Grafici</b>", styles['Heading2']))
story.append(Image("img/ai_rata_vs_reddito.png", width=450, height=300))
story.append(Spacer(1, 10))
story.append(Image("img/ai_coefficiente_K.png", width=450, height=250))
story.append(Spacer(1, 12))

# commento generale
mean_sost = df["sostenibilita"].mean()
if pd.isna(mean_sost):
    commento = "Dati insufficienti per calcolare la sostenibilità media."
else:
    commento = ("Sostenibilità media: %.2f%%. " % (mean_sost*100))
    if mean_sost <= 0.20:
        commento += "Situazione complessivamente sana."
    elif mean_sost <= 0.34:
        commento += "Situazione mista: attenzione ai borderline (zona grigia)."
    else:
        commento += "Situazione critica: molti casi non concedibili."

story.append(Paragraph(f"<b>Osservazione generale:</b> {commento}", styles['Normal']))
story.append(Spacer(1, 12))

doc.build(story)
print("📄 Report PDF generato: ai_report.pdf")

# Fine
