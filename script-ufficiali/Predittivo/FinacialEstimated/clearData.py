import numpy as np
from calcoli import Calcoli
import pandas as pd

class ClearData:
    def __init__(self,data):
        self.data = data
        self.calcoli = Calcoli()
    
    def clear(self):
        df = self.data.copy()
        df.fillna(0, inplace=True)
        df['diff_reddito']  = df['diff_reddito'].clip(lower=0)
        df['altre_spese']   = df['altre_spese'].clip(lower=0, upper=df['reddito'])
        #--miglioramenti--
        df['nr_rate_year'] = df.apply(lambda row: self.calcoli.rata_for_year(row['nr_rate']),axis=1)
        df['sost_request_reddito'] = df.apply(lambda row: self.calcoli.sostenibilita_request(row['request'],row['diff_reddito']),axis=1)
        df['rapporto_spese_reddito'] = df.apply(
            lambda row: self.calcoli.rapporto_spese_reddito(
                row['altre_spese'], row['reddito']
            ), 
            axis=1
        )
        df['rischio'] = df.apply(lambda row: self.calcoli.rischio(row['taeg'],row['diff_reddito'],row['request']),axis=1)
        df['rapp_reddito_rata'] = df.apply(lambda row: self.calcoli.rapp_reddito_rata(row['diff_reddito'], row['nr_rate']),axis=1)
        df['fascia_reddito'] = df.apply(lambda row: self.calcoli.fascia_reddito(row['reddito']),axis=1) 
        #---------------
        df['importo_rata'] = df.apply(
            lambda row: self.calcoli.calcola_rata(
                row['taeg'], row['request'], row['nr_rate']
            ), 
            axis=1
        )
        df['sostenibilita'] = df.apply(
            lambda row: self.calcoli.calcola_sostenibilita(
                row['importo_rata'], row['diff_reddito']
            ), 
            axis=1
        )

        X = df[['reddito', 'altre_spese', 'diff_reddito', 'request', 'taeg', 'nr_rate', 'rapporto_spese_reddito', 'importo_rata','sostenibilita','nr_rate_year','sost_request_reddito','rischio','rapp_reddito_rata','fascia_reddito']]
        
        return X