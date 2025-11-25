import joblib
import pandas as pd
from connectionFe import ConnectionFe
from querys import INSERT_REVISION
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from calcoli import Calcoli

MAX_RATE = 72

class ModelRevision:
    def __init__(self,sostenibilita,data):
        self.sostenibilita = sostenibilita
        self.data = data
        c = ConnectionFe()
        self.conn = c.conn()
        self.cursor = self.conn.cursor()
        self.calcoli = Calcoli()

    def revision(self):
        revision = []
       
        if(self.sostenibilita >= 0.35):
            print(f"sostenibilita: {self.sostenibilita}")
            exit()
            for i in range(int(self.data['nr_rate'])+1, MAX_RATE):
                data_cp = self.data.copy()
                diff_reddito, taeg = self.calcoli.calcola(data_cp)

                importo_rata = self.calcoli.calcola_rata(taeg, data_cp['request'], i)
                sostenibilita = self.calcoli.calcola_sostenibilita(importo_rata, diff_reddito)

                            
                if(sostenibilita <= 0.35):
                    revision.append({
                    'reddito': diff_reddito,
                    'importo_fin': data_cp['request'],
                    'nr_rate': i,
                    'importo_rata': importo_rata,
                    'sostenibilita': sostenibilita,
                    'prevision': 'Accettabile' if sostenibilita <= 0.35 else 'Non accettabile',
                    'is_accetable': None
                })
        if len(revision) == 0:
            return None
        
        return revision

    def migliore_scelta(self):
        revision = self.revision()
        print(revision)
        exit()
        #self.model(revision)
        if revision:
            solution = min(revision, key=lambda x: x['sostenibilita'])
            with self.cursor as cursor:
                cursor.execute(INSERT_REVISION, (int(solution['nr_rate']), float(solution['importo_rata']), float(solution['sostenibilita'])))
                self.conn.commit()  
            return solution, cursor.lastrowid

        return [],None
    def get_sostenibilita(self,sostenibilita):
        return 'Accettabile' if sostenibilita <= 0.35 else 'Non accettabile'    

    def model(self,revision):
        data = pd.DataFrame([revision])
        X = data[['reddito','importo_fin','nr_rate','importo_rata','sostenibilita','prevision']]
        process = ColumnTransformer(
            transformers=[
                ('rs', OneHotEncoder(handle_unknown="ignore"), ['prevision']),
                
            ],
            remainder="passthrough"
        )

        y = data['is_accetable']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = Pipeline(
            steps=[
               ("preprocess", process),
               ("xgb", XGBClassifier(
                            n_estimators=300,
                            learning_rate=0.05,
                            max_depth=5,
                            subsample=0.9,
                            colsample_bytree=0.9,
                            eval_metric="logloss"
                )
            )
            ]
        )
        model.fit(X_train, y_train)
        joblib.dump(model, '../../model/model_revision.pkl')
        return model