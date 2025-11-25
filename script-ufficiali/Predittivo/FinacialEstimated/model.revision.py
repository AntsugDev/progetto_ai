import joblib
import pandas as pd
from connection import Connection
from querys import INSERT_PREVISIONING

class ModelRevision:
    def __init__(self,sostenibilita,data):
        self.sostenibilita = sostenibilita
        self.data = data
        c = Connection()
        self.conn = c.conn
        self.cursor = self.conn.cursor()

    def revision(self):
        revision = []
        if(self.sostenibilita >= 0.35):
           
            for i in range(int(self.data['nr_rate'])+1, MAX_RATE):
                data_cp = self.data.copy()
                diff_reddito, taeg = self.calcola(data_cp)

                importo_rata = self.calcola_rata(taeg, data_cp['request'], i)
                sostenibilita = self.calcola_sostenibilita(importo_rata, diff_reddito)

                            
                if(sostenibilita <= 0.35):
                    revision.append({
                    'reddito': diff_reddito,
                    'importo_fin': data_cp['request'],
                    'nr_rate': i,
                    'importo_rata': importo_rata,
                    'sostenibilita': sostenibilita,
                    'prevision': 'Accettabile' if sostenibilita <= 0.35 else 'Non accettabile'
                })
        if len(revision) == 0:
            return None
        
        return revision

    def migliore_scelta(self):
        revision = self.revision()
        self.model(revision)
        if revision:
            solution = min(revision, key=lambda x: x['sostenibilita'])
            with self.cursor as cursor:
                cursor.execute(INSERT_PREVISIONING, (solution['reddito'], solution['importo_fin'], solution['nr_rate'], solution['importo_rata'], solution['sostenibilita'], solution['prevision']))
                self.conn.commit()  
            return solution

        return None
    def get_sostenibilita(self,sostenibilita):
        return 'Accettabile' if sostenibilita <= 0.35 else 'Non accettabile'    

    def model(self,revision):
        data = pd.DataFrame([revision],columns=['reddito','importo_fin','nr_rate','importo_rata','sostenibilita','prevision'])
        X = data[['reddito','importo_fin','nr_rate','importo_rata','sostenibilita']]
        data['prevision'] = data['prevision'].apply(lambda x: self.get_sostenibilita(x['sostenibilita']),axis=1)
        y = data['prevision']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
        model.fit(X_train, y_train)
        joblib.dump(model, '../../model/model_revision.pkl')
        return model