import csv
import pymysql
import math

# -------------------------
#  FUNZIONI DI BASE
# -------------------------

def get_import(costo_auto, formula_nuova):
    """formula_nuova = True se auto nuova (quindi 10%)"""
    if formula_nuova:
        return costo_auto * 0.10
    return costo_auto

def get_rata(nr_rate, importo, tan):
    try:
        if nr_rate <= 0:
            return 0
        tam = tan / 12
        numeratore = importo * tam
        denominatore = 1 - ((1 + tam) ** -nr_rate)
        if denominatore == 0:
            return 0
        return numeratore / denominatore
    except:
        return 0

def sostenibilita(reddito, rata):
    return rata / reddito if reddito > 0 else 999

def coefficiente_k(sostenibilita):
    if sostenibilita <= 0.20:
        return 1.0, "Ottima"
    if sostenibilita >= 0.35:
        return round(sostenibilita / 0.20), "Non concedibile"
    k = sostenibilita / 0.20
    return k, "Revisione"


# -------------------------
#  SIMULAZIONE ZONA GRIGIA
# -------------------------

def simulazione(k, costo_auto, formula_nuova, tan, nr_rate, reddito):
    """Replica identica della funzione PHP simulazione()"""

    importo_fin = get_import(costo_auto, formula_nuova)
    Ic = (k - 1.3) / (1.6 - 1.3)

    # ---- Simulazione A: anticipo (SOLO AUTO USATA: formula_nuova=False) ----
    sostenibilitaA = None
    anticipo = None
    finNuovaA = None
    rataNuovaA = None

    if not formula_nuova:
        anticipo = 0.40 * Ic * costo_auto
        finNuovaA = costo_auto - anticipo
        rataNuovaA = get_rata(nr_rate, finNuovaA, tan)
        sostenibilitaA = rataNuovaA / reddito
    else:
        sostenibilitaA = 999  # non si usa per auto nuova

    # ---- Simulazione B: aumento rate (TUTTI) ----
    nrRateNuove = round(nr_rate + (Ic * 0.40 * nr_rate))
    rataNuovaB = get_rata(nrRateNuove, importo_fin, tan)
    sostenibilitaB = rataNuovaB / reddito

    # ---- Soluzione migliore ----
    best = "Anticipo" if sostenibilitaA < sostenibilitaB else "Aumentare durata"

    return {
        "simulazione_anticipo_solo_auto_usata": {} if formula_nuova else {
            "anticipo": round(anticipo, 2),
            "importo_fin": round(finNuovaA, 2),
            "importo_rata": round(rataNuovaA, 2),
            "sostenibilita": round(sostenibilitaA, 4),
            "decisione_finale": "Accettabile" if sostenibilitaA <= 0.30 else "Non accettabile"
        },
        "simulazione_nr_rate": {
            "nr_rate_origin": nr_rate,
            "nr_rate_new": nrRateNuove,
            "importo_rata": round(rataNuovaB, 2),
            "sostenibilita": round(sostenibilitaB, 4),
            "decisione_finale": "Accettabile" if sostenibilitaB <= 0.30 else "Non accettabile"
        },
        "soluzione_consiglata": best
    }


# -------------------------
#  MAIN SCRIPT
# -------------------------

def main():
    conn = pymysql.connect(
        host="localhost",
        user="asugamele",
        password="83Asugamele@",
        database="projectAI"
    )

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM model_data")
    rows = cursor.fetchall()

    output = []

    for idx, row in enumerate(rows, start=1):

        costo = float(row["costo_auto"])
        formula_nuova = not bool(row["nuovo_usato"])
        nr_rate = int(row["nr_rate"])
        tan = float(row["tan"])
        reddito = float(row["diff_reddito"])

        # importo
        importo = get_import(costo, formula_nuova)

        # rata
        rata = get_rata(nr_rate, importo, tan)

        # sostenibilità
        S = sostenibilita(reddito, rata)

        # coefficiente K
        k, k_label = coefficiente_k(S)

        # simulazione SOLO se S in 0.21–0.29
        if 0.21 <= S <= 0.29:
            sim = simulazione(k, costo, formula_nuova, tan, nr_rate, reddito)
        else:
            sim = {}

        output.append({
            "id": idx,
            "reddito": reddito,
            "costo_auto": costo,
            "formula": "nuova" if formula_nuova else "usata",
            "importo": importo,
            "nr_rate": nr_rate,
            "rata": rata,
            "sostenibilita": S,
            "coefficienteK": k,
            "simulazione": sim
        })

    # Salva CSV
    with open("../file/ai_decision.score.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "reddito", "costo_auto", "formula",
                         "importo", "nr_rate", "rata", "sostenibilita", "coefficienteK"])
        for r in output:
            writer.writerow([
                r["id"],
                r["reddito"],
                r["costo_auto"],
                r["formula"],
                r["importo"],
                r["nr_rate"],
                r["rata"],
                r["sostenibilita"],
                r["coefficienteK"]
            ])

    print("ai_decision.csv generato correttamente.")

if __name__ == "__main__":
    main()

