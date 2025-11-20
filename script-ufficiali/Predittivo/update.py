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
        try
          with self.conn.cursor() as cursor:
            cursor.execute(SELECT_ID, table,value.upper())
            row = cursor.fetchone()
            if(row): return row['ID']
            else raise ValueError(f"Id not found for the table {table} and value {value}")
        except Exception as e:
            raise e;
        

    def create(self,data):
        try:
            calcola = self.classCalcoli.calcola_tutti_i_valori(data);
            if calcola :
                with self.conn.cursor() as cursor:
                    data_insert = {
                       'cliente' : str(uuid.uuid4()),
                       'eta': int(data['eta']),
                       'neo_patentato_id':self.getId(data['neo_patentato']),
                       'nr_figli': int(data['nr_figli']),
                       'reddito_mensie': float(data['reddito_mensile']),
                       'altre_spese': float(data['altre_spese']),
                       'diff_reddito': float(calcola['diff_reddito']),
                       'sesso_id': self.getId(data['sesso']),
                       'zona_id': self.getId(data['zona']),
                       'tipologia_auto_id': self.getId(data['tipologia_auto']),
                    cursor.execute(INSERT_MODEL, data_insert)
                self.conn.commit()



        except Exception as e:
            raise e;
    