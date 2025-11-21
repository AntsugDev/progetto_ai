from update import DatabaseUpdater
import joblib
import pandas as ps

class Predict:
    def __init__(self):
        self.api_data = {}
        self.update = DatabaseUpdater()
        self.model = None
        self.scaler = None
        self.label_encoders = None
        self.data_predizione = {}

    def carica_model(self,filename = '../../file/model.pkl'):
        try:
            model_data = joblib.load(filename)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoders = model_data['label_encoders']
            return True
        except Exception as e:
            raise e;    
    def predizione(self,data):
        df = ps.DataFrame([data])

    def main(self):
        try:
            self.carica_model(self)

            self.api_data = {
                'eta': 25,
                'neo_patentato': 'No',
                'nr_figli': 0,
                'reddito_mensile': 2450.0,
                'altre_spese': 350.67,
                'sesso': 'uomo',
                'zona': 'centro',
                'tipologia_auto': 'berlina',
                'nuovo_usato': 'nuovo',
                'costo_auto': 34678.98,
                'eta_veicolo': 0,
                'anticipo': 0.35,
                'formula_acquisto': 'finanziamento a 3 anni auto nuova',
                'nr_rate': 36
             }
            self.data_predizione = self.update.data_predizione_ai(self.api_data) 
            self.predizione(self, self.data_predizione)


if __name__ == '__main__':
    pr = Predict()
    pr.main()            