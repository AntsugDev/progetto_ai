import numpy as np
import pandas as pd
import joblib
from modelRevision import ModelRevision 
from calcoli import Calcoli 
from datetime import datetime
from connectionFe import ConnectionFe
from querys import INSERT_PREVISIONING

class Prediction:  
    def __init__(self):
        self.model = joblib.load('../../../model/model_fe.pkl')
        self.calcoli = Calcoli()
        c = ConnectionFe()
        self.conn = c.conn()
        self.cursor = self.conn.cursor()
       

    def new_predict(self):
        try:
            data = {
                'reddito': 1200,
                'altre_spese': 600,
                'request': 15000,
                'nr_rate': 25
            }
            diff_reddito, taeg = self.calcoli.calcola(data)
            data['diff_reddito'] = diff_reddito
            data['taeg'] = taeg
            
            new_df = pd.DataFrame([data],columns=['reddito', 'altre_spese', 'diff_reddito', 'request', 'taeg', 'nr_rate'])
            
            y_pred = self.model.predict(new_df)
            importo_rata = y_pred[:, 0]
            sostenibilita = y_pred[:, 1]
            
            result = {
                'data' : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'title': 'Predizione finanziara test',
                'reddito_netto':diff_reddito,
                'importo_da_fin': data['request'],
                'importo_rata' : float(round(importo_rata[0], 2)),
                'sostenibilita' : float(round(sostenibilita[0]*100, 2)),
                'decisione_ai' : self.calcoli.decisionAI(sostenibilita[0])
            }
            mr = ModelRevision(sostenibilita[0],data)
            revision, lastId = mr.migliore_scelta()
            print(revision)
            return None
            if revision:
                result['revision'] = {
                    'nr_rate': revision['nr_rate'],
                    'importo_rata': float(round(revision['importo_rata'], 2)),
                    'sostenibilita': float(round(revision['sostenibilita']*100, 2))
                }
            with self.cursor as cursor:
                revision_id = lastId if lastId  else None
                cursor.execute(INSERT_PREVISIONING, ( float(result['reddito_netto']), float(result['importo_da_fin']), float(result['importo_rata']), float(result['sostenibilita']), result['decisione_ai'], revision_id))
                self.conn.commit()

            print("Previsione terminata con successo")
            print("-"*60)
            for k,v in result.items():
                print(f"{k}: {v}")

        except Exception as e:
            print(f"Errore durante la previsione: {str(e)}")
            raise e
       

if __name__ == '__main__':
    f = Prediction() 
    f.new_predict()