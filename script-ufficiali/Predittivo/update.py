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
            cursor.execute(SELECT_ID, table,value.upper())
            row = cursor.fetchone()
            if(row): return row['ID']
            else : raise ValueError(f"Id not found for the table {table} and value {value}")
        except Exception as e:
            raise e;

    def data_predizione_ai(self,data):
        try:
            calcola = self.classCalcoli.calcola_tutti_i_valori(data)
            if calcola : 
                return {
                        'cliente' : str(uuid.uuid4()),
                        'eta': int(data['eta']),
                        'neo_patentato_id':self.getId('neo_patentato',data['neo_patentato']),
                        'nr_figli': int(data['nr_figli']),
                        'reddito_mensie': float(data['reddito_mensile']),
                        'altre_spese': float(data['altre_spese']),
                        'diff_reddito': float(calcola['diff_reddito']),
                        'sesso_id': self.getId('sesso',data['sesso']),
                        'zona_id': self.getId('zona',data['zona']),
                        'tipologia_auto_id': self.getId('tipologia_auto',data['tipologia_auto']),
                        'nuovo_usato_id': self.getId('nuovo_usato',data['nuovo_usato']),
                        'costo_auto': float(data['costo_auto']),
                        'eta_veicolo': int(data['eta_veicolo']),
                        'oneri_accessori': (data['costo_auto']*0.01),
                        'anticipo': float(data['anticipo']),
                        'tan': float(calcola.getTan(data['nuovo_usato'])),
                        'formula_acquisto_id': self.getId('formula_acquisto',data['formula_acquisto']),
                        'nr_rate': int(data['nr_rate']),
                        'sostenibilita' : calcola['sostenibilita'],
                        'coefficiente_k': calcola['coefficiente_k'],
                        're': calcola['re'],
                        'rs': calcola['rs'],
                        'rd': calcola['rd'],
                        'rt': calcola['rt'],
                        'decisione_ai': calcola['decisione_ai'],
                        'is_simulation': 'S' if calcola['simulazione'] else 'N',
                        }
            else: raise ValueError("Error calcoli");
        except Exception as e:                
            raise e;

    def create(self,data):
        try:
            calcola = self.data_predizione_ai(self,data)
            if calcola :
                with self.conn.cursor() as cursor:
                    data_insert = 
                    cursor.execute(INSERT_MODEL, data_insert)
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
    
