import numpy as np
import pandas as pd
import pymysql
from decimal import Decimal
from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

MAX_RATE = 72

class FinancialEstimated:  # Corretto il nome
    def __init__(self):
        self.db_config = {
            'host': "localhost",
            'user': "asugamele", 
            'password': "83Asugamele@",
            'database': "finacial_estimated",
            'cursorclass': pymysql.cursors.DictCursor
        }
        self.conn = pymysql.connect(**self.db_config)

    def data(self):
        with self.conn.cursor() as cursor:
            sql = "SELECT * FROM model_fe"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def convert(self, data):
        return [
            {k: float(v) if isinstance(v, Decimal) else v for k, v in row.items()}
            for row in data
        ]

    def frame(self):
        data = self.convert(self.data())
        return pd.DataFrame(data)

    def calcola(self, dataTest):
        diff_reddito = dataTest['reddito'] - dataTest['altre_spese']
        taeg = float((8.33/100)) if dataTest['request'] >= 5000 else float((10.33/100))
        return diff_reddito, taeg

    def decisionAI(self, sostenibilita):
        if sostenibilita <= 0.35:
            return "Accettato"
        else:
            return "Condizioni da rivedere, perchè si è superato la soglia di rischio"        

    def revision(self,data,sostenibilita):
        if(sostenibilita >= 0.35):
           
            revision = []    
            for i in range(int(data['nr_rate'])+1, MAX_RATE):
                data_cp = data.copy()
                data_cp['nr_rate'] = i
                diff_reddito, taeg = self.calcola(data_cp)
                data_cp['diff_reddito'] = diff_reddito
                data_cp['taeg'] = taeg
            
                model = self.model()
                p = model.predict(pd.DataFrame([data_cp],columns=['reddito', 'altre_spese', 'diff_reddito', 'request', 'taeg', 'nr_rate']))
                importo_rata = p[:, 0]
                sostenibilita = p[:, 1]
                if(sostenibilita[0] <= 0.35):
                    revision.append({
                    'nr_rate': i,
                    'importo_rata': importo_rata[0],
                    'sostenibilita': sostenibilita[0]
                })
            if len(revision) == 0:
                return None
        return min(revision, key=lambda x: x['sostenibilita'])    


    def model(self):
        df = self.frame()
        X = df[['reddito', 'altre_spese', 'diff_reddito', 'request', 'taeg', 'nr_rate']]
        y = df[['importo_rata', 'sostenibilita']]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        multi_model = MultiOutputRegressor(
            XGBRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        )

        multi_model.fit(X_train, y_train)
        return multi_model

    def new_predict(self):
        model = self.model()
        data = {
            'reddito': 1500,
            'altre_spese': 600,
            'request': 10000,
            'nr_rate': 25
        }
        diff_reddito, taeg = self.calcola(data)
        data['diff_reddito'] = diff_reddito
        data['taeg'] = taeg
        
        new_df = pd.DataFrame([data],columns=['reddito', 'altre_spese', 'diff_reddito', 'request', 'taeg', 'nr_rate'])
        
        y_pred = model.predict(new_df)
        importo_rata = y_pred[:, 0]
        sostenibilita = y_pred[:, 1]
        
        print("-" * 30 + "New Predizione" + "-" * 30)
        print(f"Importo Rata:   {round(importo_rata[0], 2)} €")
        print(f"Sostenibilità:   {round(sostenibilita[0]*100, 2)} %")
        print(f"Decisione AI:    {self.decisionAI(sostenibilita[0])}")
        if sostenibilita[0] >= 0.35 :
            print("Revisione in corso attendere ... \n\n")
        
        revision = self.revision(data, sostenibilita[0])
        if revision:
            print("-" * 30 + "Revisione" + "-" * 30)
            print(f"Rate originali:{data['nr_rate']}")
            print(pd.DataFrame([revision]))
        

if __name__ == '__main__':
    f = FinancialEstimated()  # Corretto il nome
    f.new_predict()