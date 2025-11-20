# calcoli.py
import numpy as np
import pandas as pd
import pymysql
from connection import Connection
from querys import SELECT_TAN

class FinancialCalculator:
    """
    Classe per calcolare tutti i valori finanziari basati sulle tue regole
    """
    
    class DBConfig:
        def __init__(self):
            self.host = "localhost"
            self.user = "asugamele"
            self.password = "83Asugamele@"
            self.database = "projectAI"
            self.cursorclass = pymysql.cursors.DictCursor
    
    def get_soglia_reddito(self):
        """Calcola la soglia reddito dinamica dal database"""
        db_config = self.DBConfig()
        conn = pymysql.connect(**db_config.__dict__)
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        AVG(CAST(diff_reddito AS DECIMAL(10, 2))) AS media,
                        MIN(CAST(diff_reddito AS DECIMAL(10, 2))) AS minimo,
                        MAX(CAST(diff_reddito AS DECIMAL(10, 2))) AS massimo
                    FROM model
                """)
                row = cursor.fetchone()
                
                if row and row['media']:
                    media = float(row['media'])
                    minimo = float(row['minimo'])
                    massimo = float(row['massimo'])
                    
                    soglia = media + (media * (minimo / massimo))
                    return round(soglia, 2) if soglia < 2000 else 2000.0
                else:
                    return 2000.0  
                    
        except Exception as e:
            print(f"❌ Errore calcolo soglia: {e}")
            return 2000.0
        finally:
            conn.close()
    
    def calcola_importo_finanziato(self, costo_auto, nuovo_usato, anticipo_perc=0):
        """
        Calcola l'importo finanziato secondo le tue regole CORRETTE:
        - Auto usata: nessun anticipo in prima istanza → importo = costo_auto
        - Auto nuova: con formula a 3 anni → importo = 10% del costo auto
        """
        if nuovo_usato == "Usata":
            # Auto usata: nessun anticipo in prima istanza
            return costo_auto
        else:
            # Auto nuova: finanziamento a 3 anni con 10% del costo auto
            return costo_auto * 0.10
    
    def calcola_rata(self, importo_finanziato, nr_rate, tan):
        """
        Calcola la rata mensile
        Formula: Rata = (Importo * TAN/12) / (1 - (1 + TAN/12)^(-nr_rate))
        """
        try:
            if nr_rate <= 0 or importo_finanziato <= 0:
                return 0.0
            
            tam = tan / 12 / 100  # TAN è in percentuale, convertiamo in decimale
            numeratore = importo_finanziato * tam
            denominatore = 1 - ((1 + tam) ** -nr_rate)
            
            if denominatore == 0:
                return 0.0
            
            return numeratore / denominatore
            
        except Exception as e:
            print(f"❌ Errore calcolo rata: {e}")
            return 0.0
    
    def calcola_sostenibilita(self, rata, reddito_disponibile):
        """
        Calcola la sostenibilità (rata/reddito)
        """
        if reddito_disponibile <= 0:
            return 1.0  # 100% insostenibile
        return rata / reddito_disponibile
    
    def calcola_coefficiente_K(self, sostenibilita):
        """
        Calcola il coefficiente K = sostenibilita / 0.20
        """
        return sostenibilita / 0.20
    
    # FUNZIONI DI RATING (dalle tue regole)
    def r_income(self, reddito, soglia):
        if reddito >= soglia: return 1
        if reddito >= soglia * 0.8: return 2
        if reddito >= soglia * 0.6: return 3
        if reddito >= soglia * 0.4: return 4
        return 5
    
    def r_anticipo(self, nuovo_usato, anticipo_perc):
        if nuovo_usato == "Nuova":  # Auto nuova non ha anticipo in prima istanza
            return 1
        if anticipo_perc >= 25: return 1
        if anticipo_perc >= 15: return 2
        if anticipo_perc >= 5: return 3
        return 4
    
    def calcola_re(self, reddito, anticipo_perc, nuovo_usato, soglia):
        """
        Calcola RE (Rating Economico)
        80% reddito + 20% anticipo
        """
        income_score = self.r_income(reddito, soglia)
        anticipo_score = self.r_anticipo(nuovo_usato, anticipo_perc)
        
        re = (0.8 * income_score) + (0.2 * anticipo_score)
        return min(round(re), 5)  # Massimo 5
    
    def calcola_rs(self, sostenibilita):
        """
        Calcola RS (Rating Sostenibilità)
        """
        if sostenibilita <= 0.15: return 1
        if sostenibilita <= 0.20: return 2
        if sostenibilita <= 0.29: return 3
        if sostenibilita <= 0.34: return 4
        return 5
    
    def calcola_rd(self, nr_figli, neo_patentato):
        """
        Calcola RD (Rating Altri Fattori)
        """
        base = min(nr_figli + 1, 4)  # 1-4 basato su nr_figli
        if neo_patentato == "Si":
            base += 1
        return min(base, 5)
    
    def calcola_rt(self, re, rs, rd, sostenibilita, nuovo_usato):
        """
        Calcola RT (Rating Totale) e decisione AI
        basato sulle tue regole esatte
        """
        rt = (0.5 * re) + (0.3 * rs) + (0.2 * rd)
        rt = round(rt, 2)
        
        # APPLICA LE TUE REGOLE ESATTE
        if sostenibilita >= 0.35:
            decisione = "Non concedibile"
        elif 0.21 <= sostenibilita <= 0.34:
            decisione = "Revisione con simulazione"
        elif rt <= 1.5:
            decisione = "Bonifico"
        elif 1.6 <= rt <= 4:
            if nuovo_usato == "Nuova":
                decisione = "Finanziamento a 3 anni auto nuova"
            else:
                decisione = "Finanziamento classico auto usata"
        elif 4 < rt < 5:
            decisione = "Revisione con simulazione"
        else:  # rt >= 5
            decisione = "Non concedibile"
        
        return rt, decisione
    
    def calcola_simulazione(self, k, costo_auto, nuovo_usato, tan, nr_rate, reddito):
        """
        Calcola la simulazione quando la decisione è "Revisione con simulazione"
        Basato sul tuo codice PHP
        """
        # Calcola Ic (Indice di intensità)
        Ic = k / 1.6
        
        risultato = {
            "simulazione_anticipo_solo_auto_usata": {},
            "simulazione_nr_rate": {},
            "soluzione_consigliata": ""
        }
        
        # SIMULAZIONE ANTICIPO (solo per auto usata)
        if nuovo_usato == "Usata":
            anticipo = 0.40 * Ic * costo_auto
            importo_fin_A = costo_auto - anticipo
            rata_A = self.calcola_rata(importo_fin_A, nr_rate, tan)
            sostenibilita_A = self.calcola_sostenibilita(rata_A, reddito)
            
            risultato["simulazione_anticipo_solo_auto_usata"] = {
                "anticipo": round(anticipo, 2),
                "importo_fin": round(importo_fin_A, 2),
                "importo_rata": round(rata_A, 2),
                "sostenibilita": round(sostenibilita_A, 3),
                "decisione_finale": "Accettabile" if sostenibilita_A <= 0.30 else "Non accettabile"
            }
        
        # SIMULAZIONE AUMENTO RATE
        nr_rate_nuove = round(nr_rate + (Ic * 0.40 * nr_rate))
        importo_fin_B = self.calcola_importo_finanziato(costo_auto, nuovo_usato)
        rata_B = self.calcola_rata(importo_fin_B, nr_rate_nuove, tan)
        sostenibilita_B = self.calcola_sostenibilita(rata_B, reddito)
        
        risultato["simulazione_nr_rate"] = {
            "nr_rate_origin": nr_rate,
            "nr_rata_new": nr_rate_nuove,
            "importo_rata": round(rata_B, 2),
            "sostenibilita": round(sostenibilita_B, 3),
            "decisione_finale": "Accettabile" if sostenibilita_B <= 0.30 else "Non accettabile"
        }
        
        
        if nuovo_usato == "Usata" and sostenibilita_A > 0:
            min_sostenibilita = min(sostenibilita_A, sostenibilita_B)

            if min_sostenibilita == sostenibilita_A:
                risultato["soluzione_consigliata"] = "Anticipo"
            else:
                risultato["soluzione_consigliata"] = "Aumentare la durata del finanziamento"
        else:
            risultato["soluzione_consigliata"] = "Aumentare la durata del finanziamento"
        
        return risultato
    
    def calcola_tutti_i_valori(self, dati_cliente):
        """
        Calcola tutti i valori per un nuovo cliente
        """
        # Estrai dati
        reddito_mensile = dati_cliente['reddito_mensile']
        altre_spese = dati_cliente['altre_spese']
        costo_auto = dati_cliente['costo_auto']
        nuovo_usato = dati_cliente['nuovo_usato']
        nr_rate = dati_cliente.get('nr_rate', 36)
        tan = dati_cliente.get('tan', 5.0)
        anticipo_perc = dati_cliente.get('anticipo_perc', 0)
        nr_figli = dati_cliente.get('nr_figli', 0)
        neo_patentato = dati_cliente.get('neo_patentato', 'No')
        
        # Calcoli sequenziali
        reddito_disponibile = reddito_mensile - altre_spese
        soglia_reddito = self.get_soglia_reddito()
        
        importo_finanziato = self.calcola_importo_finanziato(costo_auto, nuovo_usato, anticipo_perc)
        rata = self.calcola_rata(importo_finanziato, nr_rate, tan)
        sostenibilita = self.calcola_sostenibilita(rata, reddito_disponibile)
        coefficiente_k = self.calcola_coefficiente_K(sostenibilita)
        
        re = self.calcola_re(reddito_disponibile, anticipo_perc, nuovo_usato, soglia_reddito)
        rs = self.calcola_rs(sostenibilita)
        rd = self.calcola_rd(nr_figli, neo_patentato)
        rt, decisione_ai = self.calcola_rt(re, rs, rd, sostenibilita, nuovo_usato)
        
        # Calcola simulazione se necessario
        simulazione = None
        if decisione_ai == "Revisione con simulazione":
            simulazione = self.calcola_simulazione(
                coefficiente_k, costo_auto, nuovo_usato, tan, nr_rate, reddito_disponibile
            )
        
        # Ritorna tutti i valori calcolati
        return {
            'diff_reddito': reddito_disponibile,
            'importo_finanziato': round(importo_finanziato, 2),
            'rata': round(rata, 2),
            'sostenibilita': round(sostenibilita, 3),
            'coefficiente_K': round(coefficiente_k, 3),
            're': re,
            'rs': rs,
            'rd': rd,
            'rt': rt,
            'decisione_AI': decisione_ai,
            'simulazione': simulazione,
            'calcoli_completati': True
        }
        
    def getTan(formula):
       try:
            conn = Connection()
            with  conn.cursor() as cursor:
                cursor.execute(SELECT_TAN,(formula.upper()))
                row = cursor.fetchone()
                if row : return row['tan']
                else: raise ValueError(f"Tan not found for {formula}") 
       except Exception as e:
            raise e
