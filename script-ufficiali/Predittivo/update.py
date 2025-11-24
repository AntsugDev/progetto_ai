# update_db.py
import pymysql
import pandas as pd
from calcoli import FinancialCalculator
from connection import Connection
from querys import INSERT_MODEL,INSERT_SIMULATION_A,INSERT_SIMULATION_B,SELECT_ID
import uuid
import numpy as np

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

    def convert_numpy_types(self,data_dict):
        """Converte i tipi numpy in tipi Python nativi"""
        converted = {}
        for key, value in data_dict.items():
            if value is None:
                converted[key] = None
            elif hasattr(value, 'item'):  # Per tipi numpy
                converted[key] = value.item()
            elif isinstance(value, (np.integer, np.floating)):
                converted[key] = value.item()
            else:
                converted[key] = value
        return converted        

    def create(self,data):
        try:
            calcola,simulazione = self.data_predizione_ai(data)
            
            if calcola :
                with self.conn.cursor() as cursor:
                    record_values = self.convert_numpy_types(calcola)
                    cursor.execute(INSERT_MODEL, (
                    record_values['cliente'],
                    record_values['eta'],
                    record_values['neo_patentato_id'],
                    record_values['nr_figli'],
                    record_values['reddito_mensile'],
                    record_values['altre_spese'],
                    record_values['diff_reddito'],
                    record_values['sesso_id'],
                    record_values['zona_id'],
                    record_values['tipologia_auto_id'],
                    record_values['nuovo_usato_id'],
                    record_values['costo_auto'],
                    record_values['eta_veicolo'],
                    record_values['oneri_accessori'],
                    record_values['anticipo'],
                    record_values['tan'],
                    record_values['formula_acquisto_id'],
                    record_values['nr_rate'],
                    record_values['importo_finanziato'],
                    record_values['rata'],
                    record_values['sostenibilita'],
                    record_values['coefficiente_k'],
                    record_values['re'],
                    record_values['rs'],
                    record_values['rd'],
                    record_values['rt'],
                    record_values['decisione_ai'],
                    record_values['is_simulation']
                ))
                    self.conn.commit()
                    model_id = cursor.lastrowid

                    if simulazione:
                        simulation_covert = self.convert_numpy_types(simulazione)
                        if simulation_covert['simulazione_anticipo_solo_auto_usata']:
                            simA = simulation_covert['simulazione_anticipo_solo_auto_usata']
                            data_insert_sim_a=(
                                 model_id,
                                 self.getId('simulation_type', 'Simulazione di anticipo per auto usata'),
                                 simA['anticipo'],
                                 simA['importo_fin'],
                                 simA['importo_rata'],
                                 simA['sostenibilita'],
                                 simA['decisione_finale'],
                                 simulation_covert['soluzione_consigliata'] if simulation_covert['soluzione_consigliata'] else None
                            )
                            cursor.execute(INSERT_SIMULATION_A, data_insert_sim_a)
                            self.conn.commit()
                        if simulation_covert['simulazione_nr_rate']:   
                            simB = simulation_covert['simulazione_nr_rate']
                            data_insert_sim_b=(
                                 model_id,
                                 self.getId('simulation_type', 'Simulazione di aumento numero di rate'),
                                 simB['nr_rata_new'].iloc[0] if isinstance(simB['nr_rata_new'], pd.Series) else simB['nr_rata_new'] ,
                                 simB['importo_rata'],
                                 simB['sostenibilita'],
                                 simB['decisione_finale'],
                                simulation_covert['soluzione_consigliata'] if simulation_covert['soluzione_consigliata'] else None
                        )
                        cursor.execute(INSERT_SIMULATION_B, data_insert_sim_b)
                        self.conn.commit()

                return True;
            else:
                raise ValueError("Error create")    

        except Exception as e:
            print(f"Eccezione create fn:{e}")
            self.conn.rollback() 
            return False;
    
