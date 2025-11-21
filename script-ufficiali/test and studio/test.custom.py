# test per verificare quanto capito fino ad adesso prendendo il mio modello
from Predittivo.querys import SELECT_ALL
from Predittivo.connection import Connection
import pandas as pd
class ModelCustom:

    def __init__(self):
        self.conn = Connection()
        self.df = pd.DataFrame
    
#todo costruire il mio modello secondo i test fatti in questa directory usando OneHotEncoder e Pipelines
    def getData(self):
        try:
            rows = None
            with self.conn.cursor() as cursor:
                cursor.execute(SELECT_ALL)
                rows = cursor.fetchall();
                if rows: return rows
                else: raise ValueError("Nessun dato trovato")
        except Exception as e:
            raise e;

    def main(self):
        try:
            df = pd.DataFrame(self.getData())        
        except Exception as e:
            raise e;    

if __name__ == "__main__":
    m = ModelCustom()         