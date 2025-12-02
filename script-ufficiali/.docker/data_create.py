import sys
import os

# Aggiungi la directory superiore al path di Python
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from calcoli import Calcoli
import pandas as pd

class DataCreate:
    def __init__(self,request):
        self.request = request
        self.calcoli = Calcoli()

    def get_data(self):
        try:
             diff_reddito, taeg = self.calcoli.calcola(self.request)
             self.request['diff_reddito'] = diff_reddito
             self.request['taeg'] = taeg
             self.request['nr_rate_year']= self.calcoli.rata_for_year(self.request['nr_rate'])
             self.request['sost_request_reddito'] = self.calcoli.sostenibilita_request(self.request['request'],self.request['diff_reddito'])
             self.request['rapporto_spese_reddito'] = self.calcoli.rapporto_spese_reddito(self.request['altre_spese'], self.request['reddito'])
             self.request['rischio'] = self.calcoli.rischio(self.request['taeg'],self.request['diff_reddito'],self.request['request'])
             self.request['rapp_reddito_rata'] = self.calcoli.rapp_reddito_rata(self.request['diff_reddito'], self.request['nr_rate'])
             self.request['fascia_reddito'] = self.calcoli.fascia_reddito(self.request['reddito'])
             self.request['importo_rata'] = 0
             self.request['sostenibilita'] = 0
             
             return pd.DataFrame([self.request],columns=['reddito', 'altre_spese', 'diff_reddito', 'request', 'taeg', 'nr_rate', 'rapporto_spese_reddito', 'importo_rata','sostenibilita','nr_rate_year','sost_request_reddito','rischio','rapp_reddito_rata','fascia_reddito'])
        except Exception as e:
            raise e  