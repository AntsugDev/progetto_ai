from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

class Valutazione:
    def __init__(self, model, X, y):
        self.model = model
        self.X = X
        self.y = y
    
    def evaluate(self):
        # Predizioni
        y_pred = self.model.predict(self.X)
        
        # y_test è un DataFrame → lo trasformo in array
        y_test_array = self.y.values
        
        # Metriche per importo_rata (colonna 0)
        mae_rata = mean_absolute_error(y_test_array[:,0], y_pred[:,0])
        rmse_rata = np.sqrt(mean_squared_error(y_test_array[:,0], y_pred[:,0]))
        r2_rata = r2_score(y_test_array[:,0], y_pred[:,0])
        
        # Metriche per sostenibilita (colonna 1)
        mae_sost = mean_absolute_error(y_test_array[:,1], y_pred[:,1])
        rmse_sost = np.sqrt(mean_squared_error(y_test_array[:,1], y_pred[:,1]))
        r2_sost = r2_score(y_test_array[:,1], y_pred[:,1])
        
        print("\n==================== RISULTATI MODELLO ====================")
        print("📌 PREDIZIONE IMPORTO RATA")
        print(f" MAE  = {mae_rata:.4f}")
        print(f" RMSE = {rmse_rata:.4f}")
        print(f" R²   = {r2_rata:.4f}")
        print("\n📌 PREDIZIONE SOSTENIBILITÀ")
        print(f" MAE  = {mae_sost:.4f}")
        print(f" RMSE = {rmse_sost:.4f}")
        print(f" R²   = {r2_sost:.4f}")
        print("==========================================================\n")
