from connectionFe import ConnectionFe
from calcoli import Calcoli
import joblib
from decimal import Decimal
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor
from valutazione import Valutazione
from clearData import ClearData
import time
from tuning import Tuning
from querys import VERSION_MODEL
import json
import math
from verifiche_for_tuning import VerifyForTuning
import os

class ModelBase:
    def __init__(self):
        self.c = ConnectionFe()
        self.conn = self.c.conn()
        self.cursor = self.conn.cursor()
        self.calcoli = Calcoli()
        self.version = f"v{int(time.time())}"
        self.tuning = Tuning()

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
    
    def clean_params(self,params):
        del params['estimator']
        cleaned = {}
        for k, v in params.items():
            
            if isinstance(v, float) and math.isnan(v):
                params[k] = None
        return params

    def model(self):
        df = self.frame()

        clear = ClearData(df)
        X = clear.clear()
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
        #scores = cross_val_score(multi_model, X_train, y_train, cv=5, scoring='accuracy')
        #print(f"Accuracy media: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")

        #Tuning utile si, ma sempre da vedere se il modello migliora
        #multi_model = self.tuning.tuning(X_train, y_train)
        val = Valutazione(multi_model, X_test, y_test)
        mae_rata, rmse_rata, r2_rata, mae_sost, rmse_sost, r2_sost = val.evaluate()
        # dati per il versionamento
        #best_params = self.clean_params(multi_model.get_params())
        #json_best_params = json.dumps(best_params)
        model_name = f"model_fe_{self.version}.pkl"
        if not os.path.exists('model'):
            os.makedirs('model')
        joblib.dump(multi_model, f'model/{model_name}')

        with self.conn.cursor() as cursor:
           cursor.execute(VERSION_MODEL, (self.version, len(df), mae_rata, rmse_rata, r2_rata, mae_sost, rmse_sost, r2_sost, None, model_name))
        self.conn.commit()

           

if __name__ == '__main__':
    m = ModelBase()
    m.model()            
       