from update import DatabaseUpdater
import joblib
import pandas as pd
from sklearn.preprocessing import  LabelEncoder

class Predict:
    def __init__(self):
        self.classUpdate = DatabaseUpdater()
        self.model = joblib.load("../../model/datamodel.pkl")
        self.label_encoder = joblib.load("../../model/label_encoder.pkl")

    def main(self):
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
            p = self.model.predict(df_pred)
            p_label = self.label_encoder.inverse_transform(p)
            print("-"*30+"Predizione:"+"-"*30)
            print(p_label[0])
            print("-"*60+"\n\n")
            if simulazione:
                print("-"*30+"Simulazione:"+"-"*30)
                print(simulazione)
                print("-"*60+"\n\n")
        
            status = self.classUpdate.create(data_tester)
            if not status:
                raise Exception("Errore durante la creazione del record")
            else : print("Record creato con successo")

        except Exception as e:
            print(f"Eccezione:{e}")
            return  None


if __name__ == '__main__':
    pr = Predict()
    pr.main()            