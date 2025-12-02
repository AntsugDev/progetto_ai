from sklearn.metrics import accuracy_score
class VerifyForTuning:
    def __init__(self,model):
        self.is_tuning = 0;
        self.model = model
    
    def ctrl_accuracy(self, X, y):
        y_pred = self.model.predict(X)
        a = accuracy_score(y, y_pred)
        if(a < 0.85):
            print("Accuracy is too low, serve il tuning!")
            self.is_tuning += 1

    def ctrl_score(self, X_train, y_train, X_test, y_test):
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        if train_score > test_score + 0.1:  # Overfitting
            print("Necessario tuning - overfitting rilevato")
            self.is_tuning += 1
        elif train_score < 0.7:  # Underfitting
            print("Necessario tuning - underfitting rilevato")
            self.is_tuning += 1

    def ctrl_time(self, start,end):
        if(end - start > 60):
            print("Necessario tuning - tempo di training superiore a 60 secondi")
            self.is_tuning += 1
