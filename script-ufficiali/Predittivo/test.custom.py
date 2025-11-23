# test per verificare quanto capito fino ad adesso prendendo il mio modello
from querys import SELECT_ALL
from connection import Connection
from update import DatabaseUpdater
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from testing import TestingModel

class ModelCustom:

    def __init__(self):
        c =  Connection()
        self.classUpdate = DatabaseUpdater()
        self.conn = c.conn()
        self.df = pd.DataFrame
    
#todo costruire il mio modello secondo i test fatti in questa directory usando OneHotEncoder e Pipelines
    def getData(self):
        try:
            rows = None
            with self.conn.cursor() as cursor:
                cursor.execute(SELECT_ALL)
                rows = cursor.fetchall();
                if not rows:
                    raise ValueError("Nessun dato trovato")
                return rows
        except Exception as e:
            print(f"Eccezione:{e}")
            return None

    def create(self):
        try:
            df = pd.DataFrame(self.getData(),columns=[
                'cliente',
                'eta',
                'neo_patentato',
                'nr_figli',
                'reddito_mensile',
                'altre_spese',
                'sesso',
                'zona',
                'tipologia_auto',
                'nuovo_usato',
                'costo_auto',
                'eta_veicolo',
                'anticipo',
                'formula_acquisto',
                'nr_rate',
                'importo_finanziato',
                'rata',
                'sostenibilita',
                'coefficiente_k',
                're',
                'rs',
                'rd',
                'rt',
                'decisione_AI',
                'is_simulation'
            ])
            X = df[['eta','neo_patentato','nr_figli','reddito_mensile','altre_spese','sesso','zona','tipologia_auto','nuovo_usato','costo_auto','eta_veicolo','anticipo','formula_acquisto','nr_rate','importo_finanziato','rata','sostenibilita','coefficiente_k','re','rs','rd','rt','is_simulation']]        
            y_raw = df['decisione_AI']

            # ENCODER TARGET
            le = LabelEncoder()
            y = le.fit_transform(y_raw)
            self.label_encoder = le
           
            toConvert = ['neo_patentato','sesso','zona','tipologia_auto','nuovo_usato','formula_acquisto','is_simulation']
            process = ColumnTransformer(
               transformers=[
                   ("cat", OneHotEncoder(handle_unknown="ignore"), toConvert),
               ],
               remainder="passthrough"
            )

            X_train, X_test, y_train, y_test = train_test_split(
             X, 
             y, 
             test_size=0.2,       # 20% test
             random_state=42     # riproducibilità
            )
           
            model = Pipeline(steps=[
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
            ])

            model.fit(X, y)
            print("Modello addestrato con successo")

            #t = TestingModel(model,X,y)
            #t.main()

            #y_pred_int = model.predict(X_test)
#
            ##Test di predizione del modello
            #y_pred = le.inverse_transform(y_pred_int)
            #print("-"*30+"Test del modello:"+"-"*30)
            #print(y_pred[0])
            #print("-"*60+"\n\n")
            ##accuratezza
            #accuracy = accuracy_score(y_test, y_pred_int)
            #print(f"Accuracy: {accuracy:.2f}")
            #print("-"*60+"\n\n")
            ##dati di classificazione
            #cr  = classification_report(y_test, y_pred_int)
            #print("-"*30+"Classification Report:"+"-"*30)
            #print(cr)
            #print("-"*60+"\n\n")
            ##quali sono le feature più rilevanti
            #feature_importance = model.named_steps['xgb'].feature_importances_
            #columns = model.named_steps['preprocess'].get_feature_names_out()
            #feature_importance = pd.DataFrame({
            #    'feature': columns,
            #    'importance': feature_importance
            #})
            #feature_importance = feature_importance.sort_values(by='importance', ascending=True)
            #print("-"*30+"Feature Importance:"+"-"*30)
            #print(feature_importance)
            #print("-"*60+"\n\n")

            #grafico delle feature più rilevanti
            #import matplotlib.pyplot as plt
#
            #plt.figure(figsize=(10,6))
            #plt.barh(feature_importance['feature'], feature_importance['importance'])
            #plt.xlabel("Importance")
            #plt.ylabel("Feature")
            #plt.title("Feature importance - XGBoost")
            #plt.gca().invert_yaxis()  # mostra le feature più importanti in alto
            #plt.show()


            return model
            

        except Exception as e:
            print(f"Eccezione:{e}")
            return  None
        
    

if __name__ == "__main__":
    m = ModelCustom()   
    model = m.create()      