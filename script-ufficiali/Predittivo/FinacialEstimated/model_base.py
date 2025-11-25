from connection import ConnectionFe
from calcoli import Calcoli
import joblib
from decimal import Decimal
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor

class ModelBase:
    def __init__(self):
        self.c = ConnectionFe()
        self.conn = self.c.conn()
        self.cursor = self.conn.cursor()
        self.calcoli = Calcoli()

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


    def model(self):
        df = self.frame()
        X = df[['reddito', 'altre_spese', 'diff_reddito', 'request', 'taeg', 'nr_rate']]
        
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
        joblib.dump(multi_model, '../../../model/model_fe.pkl')
           

if __name__ == '__main__':
    m = ModelBase()
    m.model()            
       