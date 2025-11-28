from sklearn.model_selection import RandomizedSearchCV
import numpy as np
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor

class Tuning:
    def __init__(self):
        pass
    
    def tuning(self,X_train, y_train):
        # Base model
        xgb = XGBRegressor(objective="reg:squarederror", random_state=42)

        # Spazio dei parametri da cercare
        param_dist = {
             'estimator__n_estimators': [100, 200, 300, 500],
             'estimator__learning_rate': [0.01, 0.05, 0.1],
             'estimator__max_depth': [3, 4, 5, 6, 7],
             'estimator__subsample': [0.6, 0.7, 0.8, 1.0],
             'estimator__colsample_bytree': [0.6, 0.7, 0.8, 1.0],
             'estimator__gamma': [0, 0.1, 0.3, 1],
             'estimator__min_child_weight': [1, 3, 5, 7]
        }

        # Wrapper per multi-output
        multi_model = MultiOutputRegressor(xgb)

        search = RandomizedSearchCV(
            estimator=multi_model,
            param_distributions=param_dist,
            n_iter=20,                    # Numero combinazioni da provare
            scoring='neg_mean_squared_error',
            cv=3,                         # 3-fold cross validation
            random_state=42,
            n_jobs=-1                     # Usa tutti i core disponibili
        )

        print("\n🔍 Avvio tuning del modello... (20 combinazioni)")
        search.fit(X_train, y_train)
        return search.best_estimator_
        