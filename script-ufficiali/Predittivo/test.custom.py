# test per verificare quanto capito fino ad adesso prendendo il mio modello
from querys import SELECT_ALL
from connection import Connection
from update import DatabaseUpdater
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

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
            return []

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
            y = df['decisione_AI']
           
            toConvert = ['neo_patentato','sesso','zona','tipologia_auto','nuovo_usato','formula_acquisto','is_simulation']
            process = ColumnTransformer(
               transformers=[
                   ("cat", OneHotEncoder(handle_unknown="ignore"), toConvert),
               ],
               remainder="passthrough"
            )
           
            model = Pipeline(steps=[
               ("preprocess", process),
               ("rf", RandomForestClassifier())
            ])

            model.fit(X, y)
            print("Modello addestrato con successo")
            return model
            

        except Exception as e:
            print(f"Eccezione:{e}")
            return  []
        
    def predict(self,model):
        try:
            data_tester = pd.DataFrame({
                'eta': [30],
                'neo_patentato': ['si'],
                'nr_figli': [2],
                'reddito_mensile': [3000],
                'altre_spese': [500],
                'sesso': ['uomo'],
                'zona': ['centro'],
                'tipologia_auto': ['SUV'],
                'nuovo_usato': ['usato'],
                'costo_auto': [35000],
                'eta_veicolo': [2],
                'anticipo': [0],
                'formula_acquisto': ['finanziamento classico auto usata'],
                'nr_rate': [60]
            })
            record, simulazione = self.classUpdate.data_predizione_ai(data_tester)

            

            # colonne usate in training
            cols_training = ['eta','neo_patentato','nr_figli','reddito_mensile','altre_spese',
                         'sesso','zona','tipologia_auto','nuovo_usato','costo_auto',
                         'eta_veicolo','anticipo','formula_acquisto','nr_rate',
                         'importo_finanziato','rata','sostenibilita','coefficiente_k',
                         're','rs','rd','rt','is_simulation']

            # crea DataFrame con tutte le colonne
            importance = pd.DataFrame([{
                'diff_reddito': record.get('diff_reddito'),
                'rata' : record.get('rata'),
                'costo_auto': record.get('costo_auto'),
                'importo_finanziato': record.get('importo_finanziato'),
                'sostenibilita': record.get('sostenibilita'),
                'coefficiente_k':record.get('coefficiente_k'),
                're': record.get('re'),
                'rs':record.get('rs'),
                'rd': record.get('rd'),
                'rt':record.get('rt')
            }])
            print("-"*30+"Dati rilevanti:"+"-"*30)
            print(importance)
            print("-"*60+"\n\n")
            
            
            df_pred = pd.DataFrame(columns=cols_training)

            for col in df_pred.columns:
                if col in record:
                    df_pred.at[0, col] = record[col]
                else:
                    df_pred.at[0, col] = 0  # valore default per colonne mancanti

            # predizione
            p = model.predict(df_pred)
            print("-"*30+"Predizione:"+"-"*30)
            print(p[0])
            print("-"*60+"\n\n")
            if simulazione:
                print("-"*30+"Simulazione:"+"-"*30)
                print(simulazione)
                print("-"*60+"\n\n")
            
        except Exception as e:
            print(f"Eccezione:{e}")
            return  

if __name__ == "__main__":
    m = ModelCustom()   
    model = m.create()      
    m.predict(model)