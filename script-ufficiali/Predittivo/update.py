# update_db.py
import pymysql
import pandas as pd
from calcoli import FinancialCalculator
from connection import Connection
from querys import INSERT_MODEL,INSERT_SIMULATION_A,INSERT_SIMULATION_B,SELECT_ID
import uuid

class DatabaseUpdater:
    """
    Classe per aggiornare i record nel database con i calcoli
    """
    
    def __init__(self):
            self.classCalcoli = FinancialCalculator()
            connection = Connection()
            self.conn  = connection.conn()

    def getId(self,table,value):
        try:
          with self.conn.cursor() as cursor:
            execute = SELECT_ID.replace(":table", table).replace(":value", value)
            cursor.execute(execute)
            row = cursor.fetchone()
            if(row): return row['id']
            else : raise ValueError(f"Id not found for the table {table} and value {value}")
        except Exception as e:
            print(f"Eccezione get id table:{table} value:{value} :{e}")
            raise e;

    def data_predizione_ai(self,data):
        try:
            calcola = self.classCalcoli.calcola_tutti_i_valori(data)
            if calcola : 
                return {
                        'cliente' : str(uuid.uuid4()),
                        'eta': int(data['eta'].iloc[0]),
                        'neo_patentato_id':self.getId('neo_patentato',data['neo_patentato'].iloc[0]),
                        'nr_figli': int(data['nr_figli'].iloc[0]),
                        'reddito_mensile': float(data['reddito_mensile'].iloc[0]),
                        'altre_spese': float(data['altre_spese'].iloc[0]),
                        'diff_reddito': float(calcola['diff_reddito']),
                        'sesso_id': self.getId('sesso',data['sesso'].iloc[0]),
                        'zona_id': self.getId('zona',data['zona'].iloc[0]),
                        'tipologia_auto_id': self.getId('tipologia_auto',data['tipologia_auto'].iloc[0]),
                        'nuovo_usato_id': self.getId('nuovo_usato',data['nuovo_usato'].iloc[0]),
                        'costo_auto': float(data['costo_auto'].iloc[0]),
                        'eta_veicolo': int(data['eta_veicolo'].iloc[0]),
                        'oneri_accessori': (data['costo_auto'].iloc[0]*0.01),
                        'anticipo': float(data['anticipo'].iloc[0]),
                        'tan': self.classCalcoli.getTan(data['nuovo_usato'].iloc[0]),
                        'formula_acquisto_id': self.getId('formula_acquisto',data['formula_acquisto'].iloc[0]),
                        'nr_rate': int(data['nr_rate'].iloc[0]),
                        'importo_finanziato': calcola['importo_finanziato'],
                        'rata': calcola['rata'],
                        'sostenibilita' : calcola['sostenibilita'],
                        'coefficiente_k': calcola['coefficiente_K'],
                        're': calcola['re'],
                        'rs': calcola['rs'],
                        'rd': calcola['rd'],
                        'rt': calcola['rt'],
                        'decisione_ai': calcola['decisione_AI'],
                        'is_simulation': 'S' if calcola['simulazione'] else 'N',
                        },calcola['simulazione']
            else: raise ValueError("Error calcoli");
        except Exception as e:                
            raise e;

    def create(self,data):
        try:
            calcola = self.data_predizione_ai(data)
            if calcola :
                with self.conn.cursor() as cursor:
                    cursor.execute(INSERT_MODEL, calcola)
                self.conn.commit()
                model_id = cursor.lastrowid
                if calcola['simulazione']:
                    if calcola['simulazione']['simulazione_anticipo_solo_auto_usata']:
                        simA = calcola['simulazione']['simulazione_anticipo_solo_auto_usata']
                        data_insert_sim_a={
                            'model_id': model_id,
                            'simulation_type_id': self.getId('simulation_type', 'Simulazione di anticipo per auto usata'),
                            'anticipo' : simA['anticipo'],
                            'importo_finanziamento': sim['importo_fin'],
                            'importo_rata': simA['importo_rata'],
                            'sosteibilita':simA['sostenibilita'],
                            'decisione': simA['decisione_finale'],
                            'decision_ai': calcola['simulazione']['soluzione_consigliata'] if calcola['simulazione']['soluzione_consigliata'] else NULL
                            
                            
                        }
                        cursor.execute(INSERT_SIMULATION_A, data_insert_sim_a)
                        self.conn.commit()
                    if calcola['simulazione']['simulazione_nr_rate']:
                        simB = calcola['simulazione']['simulazione_nr_rate']
                        data_insert_sim_b={
                            'model_id': model_id,
                            'simulation_type_id': self.getId('simulation_type', 'Simulazione di aumento numero di rate'),
                            'nr_rata' : simB['nr_rata_new'],
                            'rata': simB['importo_rata'],
                            'sosteibilita':simB['sostenibilita'],
                            'decisione': simB['decisione_finale'],
                            'decision_ai': calcola['simulazione']['soluzione_consigliata'] if calcola['simulazione']['soluzione_consigliata'] else NULL
                            
                            
                        }
                        cursor.execute(INSERT_SIMULATION_B, data_insert_sim_b)
                        self.conn.commit()

                   

        except Exception as e:
            raise e;
    
