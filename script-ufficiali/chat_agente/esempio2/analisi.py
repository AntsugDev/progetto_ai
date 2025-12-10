from dataset import Dataset
import matplotlib.pyplot as plt
class Analyst:
    def __init__(self):
        self.dataset = Dataset()

    def analyze(self):
        try:
            df = self.dataset.create()
            # Statistiche descrittive
            print("\nStatistiche descrittive:")
            print(df.describe())

            # Correlazioni
            print("\nMatrice di correlazione:")
            print(df.corr())

            # Visualizzazioni semplici
            fig, axes = plt.subplots(1, 2, figsize=(12, 4))

            # Scatter plot: Metratura vs Prezzo
            axes[0].scatter(df['metratura'], df['prezzo'], alpha=0.6)
            axes[0].set_xlabel('Metratura (m²)')
            axes[0].set_ylabel('Prezzo (migliaia di €)')
            axes[0].set_title('Metratura vs Prezzo')
            axes[0].grid(True, alpha=0.3)

            # Scatter plot: Stanze vs Prezzo
            axes[1].scatter(df['stanze'], df['prezzo'], alpha=0.6, color='orange')
            axes[1].set_xlabel('Numero Stanze')
            axes[1].set_ylabel('Prezzo (migliaia di €)')
            axes[1].set_title('Stanze vs Prezzo')
            axes[1].grid(True, alpha=0.3)

            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"Errore durante l'analisi: {e}")            


if __name__ == "__main__":
    analyst = Analyst()
    analyst.analyze()