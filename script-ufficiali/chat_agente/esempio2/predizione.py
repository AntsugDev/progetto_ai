import numpy as np

class Predizione:
    def __init__(self):
        pass
    
    def predizione(self,model):
        try:
            print("\n=== ESEMPI DI PREDIZIONE ===")

            # Esempio 1: Casa piccola
            casa_piccola = np.array([[70, 2]])  # 70 m², 2 stanze
            prezzo_predetto = model.predict(casa_piccola)[0]
            print(f"Casa di 70m² con 2 stanze: {prezzo_predetto:.2f} mila €")

            # Esempio 2: Casa media
            casa_media = np.array([[120, 3]])  # 120 m², 3 stanze
            prezzo_predetto = model.predict(casa_media)[0]
            print(f"Casa di 120m² con 3 stanze: {prezzo_predetto:.2f} mila €")

            # Esempio 3: Casa grande
            casa_grande = np.array([[180, 4]])  # 180 m², 4 stanze
            prezzo_predetto = model.predict(casa_grande)[0]
            print(f"Casa di 180m² con 4 stanze: {prezzo_predetto:.2f} mila €")

            # Predizione con valori personalizzati
            print("\nFai la tua predizione:")
            metratura_input = float(input("Inserisci metratura (m²): "))
            stanze_input = int(input("Inserisci numero di stanze: "))

            input_data = np.array([[metratura_input, stanze_input]])
            predizione = model.predict(input_data)[0]
            print(f"\nPrezzo stimato per {metratura_input}m² con {stanze_input} stanze: {predizione:.2f} mila €")

        except Exception as e:
            print(f"Errore durante la predizione: {e}")    