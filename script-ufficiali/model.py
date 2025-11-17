import csv
import pymysql
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class StatisticheReddito:
    """Classe per contenere le statistiche del reddito"""
    media: float
    minimo: float
    massimo: float


class FinancialAnalyzer:
    """Classe per l'analisi finanziaria dei finanziamenti auto"""
    
    def __init__(self):
        self.soglia_reddito = None
    
    def get_import(self, costo_auto: float, formula_nuova: bool) -> float:
        """Calcola l'importo finanziato"""
        return costo_auto * 0.1 if formula_nuova else costo_auto
    
    def get_rata(self, nr_rate: int, importo: float, tan: float) -> float:
        """Calcola la rata mensile del finanziamento"""
        try:
            if nr_rate <= 0:
                return 0.0
                
            tam = tan / 12
            numeratore = importo * tam
            denominatore = 1 - ((1 + tam) ** -nr_rate)
            
            if denominatore == 0:
                return 0.0
                
            return numeratore / denominatore
            
        except (ZeroDivisionError, OverflowError):
            return 0.0
    
    def simulazione(self, k: float, costo_auto: float, formula: bool, 
                   tan: float, nr_rate: int, reddito: float) -> Dict[str, Any]:
        """
        Genera simulazioni alternative per migliorare la sostenibilità del finanziamento.
        
        Args:
            k: Coefficiente K di sostenibilità
            costo_auto: Costo dell'automobile
            formula: True se auto nuova, False se usata
            tan: Tasso Annuo Nominale
            nr_rate: Numero di rate
            reddito: Reddito del richiedente
            
        Returns:
            Dizionario con le simulazioni e la soluzione consigliata
        """
        sostenibilita_a = 0
        importo_fin = self.get_import(costo_auto, formula)
        anticipo = 0
        fin_nuova_a = 0
        rata_nuova_a = 0
        
        # Simulazione A: aumento anticipo (solo per auto usate)
        if not formula:
            ic = k / 1.6
            anticipo = 0.40 * ic * costo_auto
            fin_nuova_a = costo_auto - anticipo
            rata_nuova_a = self.get_rata(nr_rate, fin_nuova_a, tan)
            sostenibilita_a = rata_nuova_a / reddito if reddito > 0 else 0
        
        # Simulazione B: aumento durata
        ic = k / 1.6 if not formula else k / 1.6
        nr_rate_nuove = round(nr_rate + (ic * 0.40 * nr_rate))
        rata_nuova_b = self.get_rata(nr_rate_nuove, importo_fin, tan)
        sostenibilita_b = rata_nuova_b / reddito if reddito > 0 else 0
        
        # Determina la soluzione migliore
        min_sostenibilita = min(sostenibilita_a, sostenibilita_b) if sostenibilita_a > 0 else sostenibilita_b
        
        result = {
            "simulazione_anticipo_solo_auto_usata": {},
            "simulazione_nr_rate": {
                "nr_rate_origin": nr_rate,
                "nr_rata_new": nr_rate_nuove,
                "importo_rata": round(rata_nuova_b, 2),
                "sostenibilita": round(sostenibilita_b, 3),
                "decisione_finale": 'Accettabile' if sostenibilita_b <= 0.30 else 'Non accettabile'
            },
            "soluzione_consigliata": 'Anticipo' if min_sostenibilita == sostenibilita_a else 'Aumentare la durata del finanziamento'
        }
        
        # Aggiungi simulazione anticipo solo se auto usata
        if not formula:
            result["simulazione_anticipo_solo_auto_usata"] = {
                "anticipo": round(anticipo, 2),
                "importo_fin": round(fin_nuova_a, 2),
                "importo_rata": round(rata_nuova_a, 2),
                "sostenibilita": round(sostenibilita_a, 3),
                "decisione_finale": 'Accettabile' if sostenibilita_a <= 0.30 else 'Non accettabile'
            }
        
        return result


def get_soglia(connection: pymysql.connections.Connection) -> Optional[float]:
    """
    Calcola la soglia di reddito basata su statistiche aggregate.
    
    Args:
        connection: Connessione al database MySQL
        
    Returns:
        Soglia calcolata o None in caso di errore
    """
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT 
                    ROUND(AVG(md.diff_reddito), 2) AS media,
                    MIN(md.diff_reddito) AS minimo,
                    MAX(md.diff_reddito) AS massimo
                FROM model_data md
            """
            cursor.execute(sql)
            result = cursor.fetchone()
            
            if not result or result['media'] is None:
                raise ValueError("Nessun risultato trovato o result è NULL")
            
            media = result['media']
            massimo = result['massimo']
            
            # Calcolo personalizzato della soglia
            soglia = round(media + (media * (media / massimo)), 2)
            return soglia
                
    except (pymysql.Error, ValueError) as e:
        print(f"Errore get_soglia: {e}")
        return None


def get_importo_finanziato(formula_nuova: bool, costo_auto: float) -> float:
    """
    Calcola l'importo finanziato in base alla formula.
    
    Args:
        formula_nuova: True se auto nuova, False se usata
        costo_auto: Costo totale dell'auto
        
    Returns:
        Importo da finanziare
    """
    return costo_auto * 0.1 if formula_nuova else costo_auto


def get_rata(nr_rate: int, tan: float, importo: float) -> float:
    """
    Calcola la rata mensile del finanziamento.
    
    Args:
        nr_rate: Numero di rate
        tan: Tasso Annuo Nominale
        importo: Importo finanziato
        
    Returns:
        Rata mensile calcolata
    """
    try:
        if nr_rate <= 0:
            return 0.0
            
        tam = tan / 12  # Tasso Annuo Mensile
        numeratore = importo * tam
        denominatore = 1 - ((1 + tam) ** -nr_rate)
        
        if denominatore == 0:
            return 0.0
            
        return numeratore / denominatore
        
    except (ZeroDivisionError, OverflowError):
        return 0.0


def get_sostenibilita(reddito: float, rata: float) -> float:
    """Calcola l'indice di sostenibilità (rata/reddito)"""
    if reddito == 0:
        return 0.0
    return round(rata / reddito, 3)


def get_k(sostenibilita: float) -> float:
    """Calcola il coefficiente K basato sulla sostenibilità"""
    return round(sostenibilita / 0.20, 3) if sostenibilita >= 0.20 else 0.0


def r_income(reddito: float, soglia: float) -> int:
    """
    Calcola il rating del reddito (1-5).
    
    Args:
        reddito: Reddito del richiedente
        soglia: Soglia di riferimento
        
    Returns:
        Rating da 1 (migliore) a 5 (peggiore)
    """
    if reddito >= soglia:
        return 1
    elif reddito >= soglia * 0.8:
        return 2
    elif reddito >= soglia * 0.6:
        return 3
    elif reddito >= soglia * 0.4:
        return 4
    else:
        return 5


def r_anticipo(formula_nuova: bool, anticipo: float) -> int:
    """
    Calcola il rating dell'anticipo (1-4).
    
    Args:
        formula_nuova: True se auto nuova
        anticipo: Percentuale di anticipo
        
    Returns:
        Rating da 1 (migliore) a 4 (peggiore)
    """
    if not formula_nuova:
        return 1
    
    if anticipo >= 25:
        return 1
    elif 15 <= anticipo <= 24:
        return 2
    elif 5 <= anticipo <= 14:
        return 3
    else:
        return 4


def get_re(reddito: float, anticipo: float, formula_nuova: bool, soglia: float) -> int:
    """
    Calcola il Rating Economico (RE) combinato.
    
    Returns:
        Rating da 1 a 5
    """
    ri = r_income(reddito, soglia)
    ra = r_anticipo(formula_nuova, anticipo)
    re = (0.8 * ri) + (0.2 * ra)
    
    if re <= 1.5:
        return 1
    elif re <= 2.4:
        return 2
    elif re <= 3.2:
        return 3
    elif re <= 4:
        return 4
    else:
        return 5


def get_rs(sostenibilita: float) -> int:
    """
    Calcola il Rating di Sostenibilità (RS).
    
    Returns:
        Rating da 1 a 5
    """
    if sostenibilita <= 0.15:
        return 1
    elif 0.16 <= sostenibilita <= 0.20:
        return 2
    elif 0.21 <= sostenibilita <= 0.29:
        return 3
    elif 0.30 <= sostenibilita <= 0.34:
        return 4
    else:
        return 5


def get_rd(nr_figli: int, neo_patentato: bool) -> int:
    """
    Calcola il Rating Demografico (RD).
    
    Args:
        nr_figli: Numero di figli
        neo_patentato: True se neopatentato
        
    Returns:
        Rating da 1 a 5
    """
    if nr_figli == 0:
        base = 1
    elif nr_figli == 1:
        base = 2
    elif nr_figli == 2:
        base = 3
    else:
        base = 4
    
    if neo_patentato:
        base += 1
        
    return min(base, 5)  # Cap a 5


def get_rt(re: int, rs: int, rd: int, sostenibilita: float, formula_nuova: bool) -> str:
    """
    Calcola il Rating Totale (RT) e determina l'esito del finanziamento.
    
    Returns:
        Stringa che descrive l'esito della valutazione
    """
    rt = round((0.5 * re) + (0.3 * rs) + (0.2 * rd), 2)
    
    if sostenibilita >= 0.35:
        return "Non concedibile"
    elif 0.21 <= sostenibilita <= 0.34 and not formula_nuova:
        return ("L'accettazione del finanziamento è soggetta a revisione con una "
                "simulazione che preveda un anticipo o che aumenti la durata del finanziamento")
    else:
        if rt <= 1.5:
            return "Bonifico"
        elif 1.6 <= rt < 4:
            return 'Finanziamento a 3 anni' if formula_nuova else 'Finanziamento Classico'
        elif 4 <= rt < 5:
            return ("L'accettazione del finanziamento è soggetta a revisione con una "
                    "simulazione che preveda un anticipo o che aumenti la durata del finanziamento")
        else:
            return "Non concedibile"


def main():
    """Funzione principale per l'elaborazione dei dati di finanziamento"""
    conn = None
    analyzer = FinancialAnalyzer()
    
    # Liste per raccogliere i dati per i CSV
    dati_principali = []
    dati_simulazioni = []
    
    try:
        # Connessione al database
        conn = pymysql.connect(
            host="localhost",
            user="asugamele",
            password="83Asugamele@",
            database="projectAI",
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # Calcolo soglia di reddito
        soglia_reddito = get_soglia(conn)
        if soglia_reddito is None:
            print("Impossibile calcolare la soglia di reddito")
            return
        
        analyzer.soglia_reddito = soglia_reddito
        print(f"Soglia reddito calcolata: {soglia_reddito}\n")
        print("=" * 80)
        
        # Recupero e analisi dei dati
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM model_data")
            rows = cursor.fetchall()
            
            for idx, row in enumerate(rows, start=1):
                # Estrazione dati
                pratica_id = row.get('id', idx)
                costo = float(row["costo_auto"])
                formula_nuova = not bool(row["nuovo_usato"])
                nr_rate = int(row['nr_rate'])
                tan = float(row['tan'])
                reddito = float(row['diff_reddito'])
                anticipo = float(row['anticipo'])
                nr_figli = int(row['nr_figli'])
                neo_patentato = not bool(row['neo_patentato'])
                
                # Calcoli
                importo_fin = get_importo_finanziato(formula_nuova, costo)
                rata = get_rata(nr_rate, tan, importo_fin)
                sostenibilita = get_sostenibilita(reddito, rata)
                coefficiente_k = get_k(sostenibilita)
                
                # Rating
                re = get_re(reddito, anticipo, formula_nuova, soglia_reddito)
                rs = get_rs(sostenibilita)
                rd = get_rd(nr_figli, neo_patentato)
                rt = get_rt(re, rs, rd, sostenibilita, formula_nuova)
                
                # Simulazione (solo se necessaria revisione o sostenibilità alta)
                simulazione = None
                if coefficiente_k > 0 and sostenibilita >= 0.21:
                    simulazione = analyzer.simulazione(
                        coefficiente_k, costo, formula_nuova, tan, nr_rate, reddito
                    )
                
                # Raccolta dati per CSV principale
                dati_principali.append({
                    'id': pratica_id,
                    'costo_auto': f"{costo:.2f}",
                    'tipo': 'Nuova' if formula_nuova else 'Usata',
                    'nr_rate': nr_rate,
                    'tan': f"{tan:.4f}",
                    'reddito': f"{reddito:.2f}",
                    'anticipo': f"{anticipo:.2f}",
                    'nr_figli': nr_figli,
                    'neo_patentato': 'Si' if neo_patentato else 'No',
                    'importo_finanziato': f"{importo_fin:.2f}",
                    'rata_mensile': f"{rata:.2f}",
                    'sostenibilita': f"{sostenibilita:.3f}",
                    'coefficiente_k': f"{coefficiente_k:.3f}",
                    'rating_economico': re,
                    'rating_sostenibilita': rs,
                    'rating_demografico': rd,
                    'esito': rt
                })
                
                # Raccolta dati per CSV simulazioni
                if simulazione:
                    sim_anticipo = simulazione.get('simulazione_anticipo_solo_auto_usata', {})
                    sim_rate = simulazione['simulazione_nr_rate']
                    
                    dati_simulazioni.append({
                        'id': pratica_id,
                        'ha_simulazione_anticipo': 'Si' if sim_anticipo else 'No',
                        'sim_antic_anticipo': sim_anticipo.get('anticipo', ''),
                        'sim_antic_importo_fin': sim_anticipo.get('importo_fin', ''),
                        'sim_antic_rata': sim_anticipo.get('importo_rata', ''),
                        'sim_antic_sostenibilita': sim_anticipo.get('sostenibilita', ''),
                        'sim_antic_decisione': sim_anticipo.get('decisione_finale', ''),
                        'sim_rate_nr_rate_originali': sim_rate['nr_rate_origin'],
                        'sim_rate_nr_rate_nuove': sim_rate['nr_rata_new'],
                        'sim_rate_rata': f"{sim_rate['importo_rata']:.2f}",
                        'sim_rate_sostenibilita': f"{sim_rate['sostenibilita']:.3f}",
                        'sim_rate_decisione': sim_rate['decisione_finale'],
                        'soluzione_consigliata': simulazione['soluzione_consigliata']
                    })
                
               
                
                # Output simulazione se presente
                if simulazione:
                    
                    if simulazione['simulazione_anticipo_solo_auto_usata']:
                        sim_a = simulazione['simulazione_anticipo_solo_auto_usata']
                       
                    
                    sim_b = simulazione['simulazione_nr_rate']
        
        # CREAZIONE CSV 1: Dati principali
        print("\n\n📄 Creazione CSV con dati principali...")
        csv_file_main = '../file/MODEL.csv'
        with open(csv_file_main, 'w', newline='', encoding='utf-8-sig') as f:
            if dati_principali:
                writer = csv.DictWriter(f, fieldnames=dati_principali[0].keys())
                writer.writeheader()
                writer.writerows(dati_principali)
                print(f"✓ File '{csv_file_main}' creato con successo ({len(dati_principali)} righe)")
        
        # CREAZIONE CSV 2: Simulazioni
        print(f"\n📄 Creazione CSV con simulazioni...")
        csv_file_sim = '../file/SIMULAZIONI.csv'
        with open(csv_file_sim, 'w', newline='', encoding='utf-8-sig') as f:
            if dati_simulazioni:
                writer = csv.DictWriter(f, fieldnames=dati_simulazioni[0].keys())
                writer.writeheader()
                writer.writerows(dati_simulazioni)
                print(f"✓ File '{csv_file_sim}' creato con successo ({len(dati_simulazioni)} righe)")
            else:
                print("⚠ Nessuna simulazione da salvare")
                
    except pymysql.Error as e:
        print(f"Errore database: {e}")
    except Exception as e:
        print(f"Errore generale: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()
            print("\n✓ Connessione chiusa.")


if __name__ == "__main__":
    main()
