# update_db.py
import pymysql
import pandas as pd
from calcoli import FinancialCalculator

class DatabaseUpdater:
    """
    Classe per aggiornare i record nel database con i calcoli
    """
    
    def __init__(self):
        self.calculator = FinancialCalculator()
        self.db_config = {
            'host': "localhost",
            'user': "asugamele", 
            'password': "83Asugamele@",
            'database': "projectAI",
            'cursorclass': pymysql.cursors.DictCursor
        }
    
    def get_id_from_table(self, table_name, testo):
        """Ottiene ID da una tabella lookup"""
        conn = pymysql.connect(**self.db_config)
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT id FROM {table_name} WHERE UPPER(testo) = UPPER(%s)", (testo.upper(),))
                result = cursor.fetchone()
                if not result:
                    raise Exception(f"ID non trovato per {testo} in {table_name}")
                return result['id']
        finally:
            conn.close()
    
    def aggiorna_record(self, record_id):
        """
        Aggiorna un singolo record nel database con tutti i calcoli
        """
        conn = pymysql.connect(**self.db_config)
        try:
            with conn.cursor() as cursor:
                # Carica il record
                cursor.execute("""
                    SELECT m.*, np.testo as neo_patentato, nu.testo as nuovo_usato
                    FROM model m
                    LEFT JOIN neo_patentato np ON m.neo_patentato_id = np.id
                    LEFT JOIN nuovo_usato nu ON m.nuovo_usato_id = nu.id
                    WHERE m.id = %s
                """, (record_id,))
                record = cursor.fetchone()
                
                if not record:
                    print(f"❌ Record {record_id} non trovato")
                    return False
                
                # Prepara dati per il calcolo
                dati_cliente = {
                    'reddito_mensile': float(record['reddito_mensie']),
                    'altre_spese': float(record['altre_spese']),
                    'costo_auto': float(record['costo_auto']),
                    'nuovo_usato': record['nuovo_usato'],
                    'nr_rate': int(record['nr_rate']),
                    'tan': float(record['tan']),
                    'anticipo_perc': float(record['anticipo']),
                    'nr_figli': int(record['nr_figli']),
                    'neo_patentato': record['neo_patentato']
                }
                
                # Calcola tutti i valori
                calcoli = self.calculator.calcola_tutti_i_valori(dati_cliente)
                
                if not calcoli['calcoli_completati']:
                    print(f"❌ Errore nei calcoli per record {record_id}")
                    return False
                
                # Aggiorna il record
                cursor.execute("""
                    UPDATE model SET 
                        importo_finanziato = %s,
                        rata = %s,
                        sostenibilita = %s,
                        coefficiente_K = %s,
                        re = %s,
                        rs = %s,
                        rd = %s,
                        rt = %s,
                        decisione_AI = %s,
                        is_simulation = %s
                    WHERE id = %s
                """, (
                    calcoli['importo_finanziato'],
                    calcoli['rata'],
                    calcoli['sostenibilita'],
                    calcoli['coefficiente_K'],
                    calcoli['re'],
                    calcoli['rs'],
                    calcoli['rd'],
                    calcoli['rt'],
                    calcoli['decisione_AI'],
                    'S' if calcoli['decisione_AI'] == 'Revisione con simulazione' else 'N',
                    record_id
                ))
                
                # Elimina simulazioni esistenti
                cursor.execute("DELETE FROM simulation WHERE model_id = %s", (record_id,))
                
                # Inserisci nuove simulazioni se necessario
                if calcoli.get('simulazione'):
                    simulazione = calcoli['simulazione']
                    
                    # Simulazione Anticipo (solo per auto usata)
                    if simulazione['simulazione_anticipo_solo_auto_usata']:
                        sim_a = simulazione['simulazione_anticipo_solo_auto_usata']
                        cursor.execute("""
                            INSERT INTO simulation 
                            (model_id, simulation_type_id, anticipo, importo_finanziamento, 
                             importo_rata, sostenibilita, decisione, decision_AI)
                            VALUES (%s, 1, %s, %s, %s, %s, %s, %s)
                        """, (
                            record_id,
                            sim_a['anticipo'],
                            sim_a['importo_fin'],
                            sim_a['importo_rata'],
                            sim_a['sostenibilita'],
                            sim_a['decisione_finale'],
                            simulazione['soluzione_consigliata']
                        ))
                    
                    # Simulazione Aumento Rate
                    sim_b = simulazione['simulazione_nr_rate']
                    cursor.execute("""
                        INSERT INTO simulation 
                        (model_id, simulation_type_id, nr_rata, rata, 
                         sostenibilita, decisione, decision_AI)
                        VALUES (%s, 2, %s, %s, %s, %s, %s)
                    """, (
                        record_id,
                        sim_b['nr_rata_new'],
                        sim_b['importo_rata'],
                        sim_b['sostenibilita'],
                        sim_b['decisione_finale'],
                        simulazione['soluzione_consigliata']
                    ))
                
                conn.commit()
                print(f"✅ Record {record_id} aggiornato con successo")
                return True
                
        except Exception as e:
            print(f"❌ Errore aggiornamento record {record_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def aggiorna_tutti_i_record(self):
        """
        Aggiorna tutti i record nel database che necessitano di calcoli
        """
        conn = pymysql.connect(**self.db_config)
        try:
            with conn.cursor() as cursor:
                # Trova record che non hanno decisione_AI o hanno valori nulli
                cursor.execute("""
                    SELECT id FROM model 
                    WHERE decisione_AI IS NULL 
                       OR importo_finanziato IS NULL 
                       OR rata IS NULL
                    ORDER BY id
                """)
                records = cursor.fetchall()
                
                if not records:
                    print("✅ Tutti i record sono già aggiornati")
                    return
                
                print(f"🔄 Trovati {len(records)} record da aggiornare...")
                
                success_count = 0
                for record in records:
                    if self.aggiorna_record(record['id']):
                        success_count += 1
                
                print(f"🎯 Aggiornamento completato: {success_count}/{len(records)} record aggiornati")
                
        except Exception as e:
            print(f"❌ Errore aggiornamento globale: {e}")
        finally:
            conn.close()