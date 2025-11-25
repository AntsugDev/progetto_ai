from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import pandas as pd


class TestingModel:
    def __init__(self, model,X,y):
        self.model = model
        self.X = X
        self.y = y
    

    def train(self):
        X_train, X_test, y_train, y_test = train_test_split(
             self.X, 
             self.y, 
             test_size=0.2,       # 20% test
             random_state=42     # riproducibilità
            )
        return  X_train, X_test, y_train, y_test

    def predict(self):
        X_train, X_test, y_train, y_test = self.train()
        self.model.fit(X_train, y_train)
        y_pred_int = self.model.predict(X_test)
        #le = LabelEncoder()
        #y_pred = le.inverse_transform(y_pred_int)
        return y_pred_int,y_test    

    def accuracy(self):
        y_pred_int,y_test = self.predict()
        accuracy = accuracy_score(y_test, y_pred_int)
        return accuracy

    def classification_report(self):
        y_pred_int,y_test = self.predict()
        report = classification_report(y_test, y_pred_int)
        return report    

    def feature_importance(self):
        feature_importance = self.model.named_steps['xgb'].feature_importances_
        columns = self.model.named_steps['preprocess'].get_feature_names_out()
        feature_importance = pd.DataFrame({
                'feature': columns,
                'importance': feature_importance
            })
        feature_importance = feature_importance.sort_values(by='importance', ascending=True)
        return feature_importance

    def graphic(self,feature_importance):
        plt.figure(figsize=(10,6))
        plt.barh(feature_importance['feature'], feature_importance['importance'])
        plt.xlabel("Importance")
        plt.ylabel("Feature")
        plt.title("Feature importance - XGBoost")
        plt.gca().invert_yaxis()  # mostra le feature più importanti in alto
        plt.show()    

    def main(self):
        print("-"*30+"Predizione:"+"-"*30)                   
        print(self.predict())
        print("-"*60+"\n\n")
        print("-"*30+"Accuracy:"+"-"*30)                   
        print(self.accuracy())
        print("-"*60+"\n\n")
        print("-"*30+"Classification Report:"+"-"*30)
        print(self.classification_report())
        print("-"*60+"\n\n")
        print("-"*30+"Feature Importance:"+"-"*30)
        print(self.feature_importance())
        print("-"*60+"\n\n")
        self.graphic(self.feature_importance())       