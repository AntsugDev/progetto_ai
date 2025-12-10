import numpy as np
import pandas as pd

class Dataset:
    def __init__(self):
        pass

    def create(self):
        # Generiamo dati casuali ma realistici
        np.random.seed(42)  # Per risultati riproducibili

        # Numero di campioni
        n_samples = 200

        # 1. Metratura (in m²) - variabile principale
        metratura = np.random.randint(50, 200, n_samples)

        # 2. Numero di stanze - variabile secondaria
        stanze = np.random.randint(1, 5, n_samples)

        # 3. Prezzo target (in migliaia di euro)
        # Formula: base 100k + 2k per m² + 20k per stanza + rumore casuale
        prezzo = 100 + 2 * metratura + 20 * stanze + np.random.normal(0, 30, n_samples)

        # Creiamo un DataFrame
        df = pd.DataFrame({
            'metratura': metratura,
            'stanze': stanze,
            'prezzo': prezzo
            })

        return df