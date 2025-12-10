import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import numpy as np

class ValutazioneModel:
    def __init__(self):
       pass
    
    def valutazione(self,model,X_test,y_test):
        try:
            y_pred = model.predict(X_test)

            # Metriche di valutazione
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)

            print("\nMetriche di valutazione sul Test Set:")
            print(f"MAE (Mean Absolute Error): {mae:.2f} mila €")
            print(f"MSE (Mean Squared Error): {mse:.2f}")
            print(f"RMSE (Root Mean Squared Error): {rmse:.2f} mila €")
            print(f"R² Score: {r2:.4f}")

            # Visualizzazione predizioni vs valori reali
            plt.figure(figsize=(8, 6))
            plt.scatter(y_test, y_pred, alpha=0.6)
            plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 
         'r--', lw=2, label='Linea perfetta')

            plt.xlabel('Prezzo Reale (migliaia di €)')
            plt.ylabel('Prezzo Predetto (migliaia di €)')
            plt.title('Predizioni vs Valori Reali')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.show()

            # Residui
            residui = y_test - y_pred
            plt.figure(figsize=(8, 4))
            plt.scatter(y_pred, residui, alpha=0.6)
            plt.axhline(y=0, color='r', linestyle='--')
            plt.xlabel('Predizioni')
            plt.ylabel('Residui (Reale - Predetto)')
            plt.title('Analisi dei Residui')
            plt.grid(True, alpha=0.3)
            plt.show()

        except Exception as e:
            print(f"Errore durante la valutazione: {e}")    

            