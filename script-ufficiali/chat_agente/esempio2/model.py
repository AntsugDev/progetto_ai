from dataset import Dataset
from sklearn.model_selection import train_test_split
from datetime import datetime
import joblib
from sklearn.linear_model import LinearRegression
class Model:
    def __init__(self):
        self.dataset = Dataset()
    
    def train(self):
        try:
            df = self.dataset.create()
            X = df[['metratura', 'stanze']]
            # todo aggiungere i seguenti campi al modello:
                # - media della metratura
                # - media del prezzo
                # - media del numero di stanze
            y = df['prezzo']

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            print(f"Dimensioni training set: {X_train.shape}")
            print(f"Dimensioni test set: {X_test.shape}")
            #name_model = f"model_{datetime.now().strftime('%Y%m%d')}.pkl"
            name_model = "model_ai_chat.pkl"
            model = LinearRegression()
            model.fit(X_train, y_train)

            joblib.dump(model,f"./pkl/{name_model}")

            print("\nCoefficienti del modello:")
            print(f"Intercetta (bias): {model.intercept_:.2f}")
            print(f"Coefficiente metratura: {model.coef_[0]:.2f}")
            print(f"Coefficiente stanze: {model.coef_[1]:.2f}")

            # Interpretazione:
            # Prezzo = intercetta + (coeff_metratura × metratura) + (coeff_stanze × stanze)
            print(f"\nEquazione del modello:")
            print(f"Prezzo = {model.intercept_:.2f} + ({model.coef_[0]:.2f} × metratura) + ({model.coef_[1]:.2f} × stanze)")

            #from valutazione_model import ValutazioneModel
            #valutazioneModel = ValutazioneModel()
            #valutazioneModel.valutazione(model,X_test,y_test)

            #from predizione import Predizione
            #predizione = Predizione()
            #predizione.predizione(model)

            print("\nModello addestrato e salvato con successo.")


        except Exception as e:
            print(f"Errore durante il training: {e}")    

if __name__ == "__main__":
    model = Model()
    model.train()            