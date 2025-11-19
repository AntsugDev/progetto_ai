import csv
import pymysql
from dataclasses import dataclass
from typing import Dict, Any


# ==========================================================
#        CLASSI UTILI
# ==========================================================

@dataclass
class RTResult:
    rt: float
    result: str


class FinancialAnalyzer:
    """Classe per calcolare rate, simulazioni e sostenibilità."""

    def get_import(self, costo_auto: float, formula_nuova: bool) -> float:
        """Calcola l'importo finanziato."""
        return costo_auto * 0.10 if formula_nuova else costo_auto

    def get_rata(self, nr_rate: int, tan: float, importo: float) -> float:
        """Calcola la rata mensile."""
        try:
            if nr_rate <= 0:
                return 0.0

            tam = tan / 12
            numeratore = importo * tam
            denominatore = 1 - ((1 + tam) ** -nr_rate)

            if denominatore == 0:
                return 0.0

            return numeratore / denominatore

        except Exception:
            return 0.0

    def simulazione(self, k: float, costo_auto: float, formula_nuova: bool,
                    tan: float, nr_rate: int, reddito: float) -> Dict[str, Any]:

        ic = min(max(k / 1.6, 0), 1)  # Ic ∈ [0,1]
        importo_fin = self.get_import(costo_auto, formula_nuova)

        result = {
            "simulazione_anticipo_solo_auto_usata": {},
            "simulazione_nr_rate": {},
            "soluzione_consigliata": ""
        }

        # -----------------------
        # A) SIMULAZIONE ANTICIPO
        # -----------------------
        sosten_A = None
        if not formula_nuova:
            anticipo = 0.40 * ic * costo_auto
            importo_fin_A = costo_auto - anticipo
            rata_A = self.get_rata(nr_rate, tan, importo_fin_A)
            sosten_A = rata_A / reddito if reddito > 0 else 1

            result["simulazione_anticipo_solo_auto_usata"] = {
                "anticipo": round(anticipo, 2),
                "importo_fin": round(importo_fin_A, 2),
                "importo_rata": round(rata_A, 2),
                "sostenibilita": round(sosten_A, 3),
                "decisione_finale": "Accettabile" if sosten_A <= 0.25 else "Non accettabile"
            }

        # -----------------------
        # B) SIMULAZIONE DURATA
        # -----------------------
        nr_rate_new = round(nr_rate + (ic * 0.40 * nr_rate))
        rata_B = self.get_rata(nr_rate_new, tan, importo_fin)
        sosten_B = rata_B / reddito if reddito > 0 else 1

        result["simulazione_nr_rate"] = {
            "nr_rate_origin": nr_rate,
            "nr_rata_new": nr_rate_new,
            "importo_rata": round(rata_B, 2),
            "sostenibilita": round(sosten_B, 3),
            "decisione_finale": "Accettabile" if sosten_B <= 0.25 else "Non accettabile"
        }

        # -----------------------
        # C) SCELTA CONSIGLIATA
        # -----------------------
        if sosten_A is not None:
            scelta = "Anticipo" if sosten_A < sosten_B else "Durata"
        else:
            scelta = "Durata"

        result["soluzione_consigliata"] = scelta

        return result


# ==========================================================
#        FUNZIONI DI CALCOLO RATING
# ==========================================================

def get_soglia(connection) -> float:
    """Calcolo della soglia reddito dinamica."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                AVG(diff_reddito) AS media,
                MIN(diff_reddito) AS minimo,
                MAX(diff_reddito) AS massimo
            FROM datamodel
        """)
        row = cursor.fetchone()

        media = float(row['media'])
        minimo = float(row['minimo'])
        massimo = float(row['massimo'])

        soglia = media + (media * (minimo / massimo))
        return round(soglia, 2) if soglia < 2000 else 2000.0


def r_income(reddito, soglia):
    if reddito >= soglia: return 1
    if reddito >= soglia * 0.8: return 2
    if reddito >= soglia * 0.6: return 3
    if reddito >= soglia * 0.4: return 4
    return 5


def r_anticipo(formula_nuova, anticipo):
    if not formula_nuova:
        return 1
    if anticipo >= 25: return 1
    if anticipo >= 15: return 2
    if anticipo >= 5: return 3
    return 4


def get_re(reddito, anticipo, formula, soglia):
    val = (0.8 * r_income(reddito, soglia)) + (0.2 * r_anticipo(formula, anticipo))
    if val <= 1.5: return 1
    if val <= 2.4: return 2
    if val <= 3.2: return 3
    if val <= 4: return 4
    return 5


def get_rs(s):
    if s <= 0.15: return 1
    if s <= 0.20: return 2
    if s <= 0.29: return 3
    if s <= 0.34: return 4
    return 5


def get_rd(figli, neo):
    base = [1,2,3,4][min(figli,3)]
    if neo: base += 1
    return min(base, 5)


def get_rt(re, rs, rd, s, formula):
    rt = float((0.5 * re) + (0.3 * rs) + (0.2 * rd))
    if s >= 0.35:
        esito = "Non concedibile"

    elif 0.21 <= s <= 0.34 and not formula:
        esito = "Revisione con simulazione"

    elif rt <= 1.5:
        esito = "Bonifico"

    elif 1.6 <= rt <= 4:
        esito = "Finanziamento a 3 anni" if formula else "Finanziamento Classico"

    elif 4 < rt < 5:
        esito = "Revisione con simulazione"

    elif rt >= 5:
        esito = "Non concedibile"

    return RTResult(rt=round(rt,2), result=esito)


# ==========================================================
#                   MAIN PROCESSING
# ==========================================================

def main():

    analyzer = FinancialAnalyzer()

    conn = pymysql.connect(
        host="localhost",
        user="asugamele",
        password="83Asugamele@",
        database="projectAI",
        cursorclass=pymysql.cursors.DictCursor
    )

    with conn:
        soglia = get_soglia(conn)
        print("Soglia reddito:", soglia)

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM model")
            rows = cursor.fetchall()
            cursor.execute("DELETE FROM simulation")

        conn.commit()

        with conn.cursor() as cursor:
            for row in rows:

                idc = row["cliente"]
                costo = float(row["costo_auto"])
                formula_nuova = True if row["nuovo_usato_id"] == 1 else False
                nr_rate = int(row["nr_rate"])
                tan = float(row["tan"])
                reddito = float(row["diff_reddito"])
                anticipo = float(row["anticipo"]) * 100
                figli = int(row["nr_figli"])
                neo = True if row["neo_patentato_id"] == 1 else False

                # importo – rata – sostenibilità – k
                importo_fin = analyzer.get_import(costo, formula_nuova)
                rata = analyzer.get_rata(nr_rate, tan, importo_fin)
                sosten = rata / reddito if reddito > 0 else 1
                k = round(sosten / 0.20, 3)

                # rating
                re = get_re(reddito, anticipo, formula_nuova, soglia)
                rs = get_rs(sosten)
                rd = get_rd(figli, neo)
                rt_outpt = get_rt(re, rs, rd, sosten, formula_nuova)

                # simulazione
                simulazione = None
                if (0.21 <= sosten <= 0.34) or (0.21 <= sosten <= 0.34 and 4 < rt_outpt.rt < 5):
                    simulazione = analyzer.simulazione(k, costo, formula_nuova, tan, nr_rate, reddito)

                cursor.execute(
                    """
                    UPDATE model SET importo_finanziato = %s, rata = %s, sostenibilita = %s, 
                    coefficiente_K = %s, re = %s, rs = %s, rd = %s, rt = %s, 
                    decisione_AI = %s, is_simulation = %s WHERE id = %s
                    """,
                    (
                        float(importo_fin),
                        float(rata),
                        float(sosten),
                        float(k),
                        int(re),
                        int(rs),
                        int(rd),
                        float(rt_outpt.rt),
                        rt_outpt.result,
                        'S' if (0.21 <= sosten <= 0.34) or (0.21 <= sosten <= 0.34 and 4 < rt_outpt.rt < 5) else 'N',
                        int(row['id'])
                    )
                )

                # append SIMULAZIONE.csv
                if simulazione:
                    simA = simulazione["simulazione_anticipo_solo_auto_usata"]
                    simB = simulazione["simulazione_nr_rate"]
                    
                    if simA:
                        cursor.execute(
                            """
                            INSERT INTO simulation (model_id, simulation_type_id, anticipo, 
                            importo_finanziamento, importo_rata, sostenibilita, decisione) 
                            VALUES(%s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                row['id'],
                                1,
                                float(simA['anticipo']),
                                float(simA['importo_fin']),
                                float(simA['importo_rata']),
                                float(simA['sostenibilita']),
                                simA['decisione_finale'],
                            )
                        )
                    
                    if simB:
                        cursor.execute(
                            """
                            INSERT INTO simulation (model_id, simulation_type_id, nr_rata, 
                            rata, sostenibilita, decisione) 
                            VALUES(%s, %s, %s, %s, %s, %s)
                            """,
                            (
                                row['id'],
                                2,
                                int(simB['nr_rata_new']),
                                float(simB['importo_rata']),
                                float(simB['sostenibilita']),
                                simB['decisione_finale'],
                            )
                        )
                    
                    cursor.execute(
                        """
                        UPDATE simulation SET decision_AI = %s WHERE model_id = %s
                        """,
                        (
                            simulazione['soluzione_consigliata'],
                            row['id']
                        )
                    )

            conn.commit()


if __name__ == "__main__":
    main()
