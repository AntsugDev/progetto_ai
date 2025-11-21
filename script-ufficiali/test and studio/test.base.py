# Il test serve per mostrare il risulrtato di un modello usando il Random Forest

from sklearn.ensemble import RandomForestClassifier
import numpy as np

# --- 1. Dataset molto semplice (fittizio) ---
# feature: [temperatura, umidità]
X = np.array([
    [30, 80],  # caldo + umido
    [22, 40],  # temperato + secco
    [15, 30],  # freddo + secco
    [35, 70],  # molto caldo
    [10, 90],  # freddo + umido
])

# etichette: 1 = esci, 0 = resta a casa
y = np.array([0, 1, 1, 0, 0])

# --- 2. Creazione del modello Random Forest ---
agent = RandomForestClassifier(n_estimators=10, random_state=42)
agent.fit(X, y)

# --- 3. Funzione "agente" ---
def agente_ai(temperatura, umidita):
    prediction = agent.predict([[temperatura, umidita]])[0]
    if prediction == 1:
        return "L'agente decide: ESCO 🚶‍♂️"
    else:
        return "L'agente decide: RESTO A CASA 🏠"

# --- 4. Test dell'agente ---
print(agente_ai(10 , 30))  # esempio
