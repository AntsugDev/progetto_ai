"""
Agente AI Predittivo - Esempio Semplice
Scenario: Un agente che predice e controlla la temperatura di una stanza
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from collections import deque

class AmbienteStanza:
    """Simula una stanza con dinamiche termiche semplici"""
    def __init__(self, temp_iniziale=20, temp_esterna=10):
        self.temp_corrente = temp_iniziale
        self.temp_esterna = temp_esterna
        self.dispersione = 0.1 # Quanto velocemente si raffredda
        
    def step(self, riscaldamento):
        """
        Simula un passo temporale
        riscaldamento: potenza del riscaldamento (0-10)
        """
        # Fisica semplificata: dispersione termica + riscaldamento
        dispersione = (self.temp_corrente - self.temp_esterna) * self.dispersione
        self.temp_corrente = self.temp_corrente - dispersione + riscaldamento
        
        # Aggiungi un po' di rumore
        self.temp_corrente += np.random.normal(0, 0.2)
        
        return self.temp_corrente


class AgentePredittivo:
    """Agente che predice e controlla la temperatura"""
    def __init__(self, target_temp=22):
        self.target_temp = target_temp
        self.modello = LinearRegression()
        self.storia = deque(maxlen=20) # Mantiene ultimi 20 stati
        self.addestrato = False
        
    def osserva(self, temp, azione):
        """Raccoglie dati per apprendere il modello"""
        self.storia.append((temp, azione))
        
        # Addestra il modello quando hai abbastanza dati
        if len(self.storia) >= 10 and not self.addestrato:
            self._addestra_modello()
            
    def _addestra_modello(self):
        """Apprende come la temperatura risponde alle azioni"""
        if len(self.storia) < 5:
            return
            
        X = [] # Features: [temp_corrente, azione]
        y = [] # Target: temp_prossima
        
        dati = list(self.storia)
        for i in range(len(dati) - 1):
            temp_curr, azione = dati[i]
            temp_next = dati[i+1][0]
            X.append([temp_curr, azione])
            y.append(temp_next)
            
        if len(X) > 0:
            self.modello.fit(X, y)
            self.addestrato = True
            print("✓ Modello addestrato con {} campioni".format(len(X)))
    
    def predici(self, temp_corrente, azione_proposta):
        """Predice la temperatura futura data un'azione"""
        if not self.addestrato:
            return temp_corrente # Fallback senza modello
            
        X_pred = np.array([[temp_corrente, azione_proposta]])
        temp_predetta = self.modello.predict(X_pred)[0]
        return temp_predetta
    
    def decidi_azione(self, temp_corrente):
        """
        Decide l'azione ottimale usando Model Predictive Control semplificato
        Prova diverse azioni e sceglie quella che avvicina di più al target
        """
        if not self.addestrato:
            # Controllo proporzionale semplice prima dell'addestramento
            errore = self.target_temp - temp_corrente
            azione = max(0, min(10, errore * 2))
            return azione
        
        # Prova diverse azioni e scegli la migliore
        azioni_possibili = np.linspace(0, 10, 20)
        migliore_azione = 0
        minimo_errore = float('inf')
        
        for azione in azioni_possibili:
            # Predici temperatura futura
            temp_pred = self.predici(temp_corrente, azione)
            
            # Calcola errore rispetto al target
            errore = abs(temp_pred - self.target_temp)
            
            # Penalizza azioni estreme (efficienza energetica)
            costo_energia = 0.01 * (azione ** 2)
            costo_totale = errore + costo_energia
            
            if costo_totale < minimo_errore:
                minimo_errore = costo_totale
                migliore_azione = azione
                
        return migliore_azione


def esegui_simulazione(num_passi=100):
    """Esegue la simulazione completa"""
    # Inizializza ambiente e agente
    ambiente = AmbienteStanza(temp_iniziale=18, temp_esterna=10)
    agente = AgentePredittivo(target_temp=22)
    
    # Traccia per visualizzazione
    temperature = []
    azioni = []
    predizioni = []
    
    print("Inizio simulazione...\n")
    
    for t in range(num_passi):
        temp_corrente = ambiente.temp_corrente
        
        # Agente decide azione
        azione = agente.decidi_azione(temp_corrente)
        
        # Agente fa predizione (se addestrato)
        if agente.addestrato:
            predizione = agente.predici(temp_corrente, azione)
            predizioni.append(predizione)
        else:
            predizioni.append(None)
        
        # Esegui azione nell'ambiente
        nuova_temp = ambiente.step(azione)
        
        # Agente osserva risultato
        agente.osserva(temp_corrente, azione)
        
        # Salva dati
        temperature.append(temp_corrente)
        azioni.append(azione)
        
        # Stampa progresso ogni 20 passi
        if t % 20 == 0:
            print(f"Passo {t}: Temp={temp_corrente:.1f}°C, Azione={azione:.1f}, Target=22°C")
    
    # Visualizza risultati
    visualizza_risultati(temperature, azioni, predizioni, agente.target_temp)


def visualizza_risultati(temperature, azioni, predizioni, target):
    """Crea grafici dei risultati"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    passi = range(len(temperature))
    
    # Grafico temperatura
    ax1.plot(passi, temperature, 'b-', label='Temperatura Reale', linewidth=2)
    ax1.axhline(y=target, color='r', linestyle='--', label='Target', linewidth=2)
    
    # Aggiungi predizioni (dove disponibili)
    pred_valide = [(i, p) for i, p in enumerate(predizioni) if p is not None]
    if pred_valide:
        idx_pred, val_pred = zip(*pred_valide)
        ax1.plot(idx_pred, val_pred, 'g.', label='Predizioni', alpha=0.5)
    
    ax1.set_xlabel('Tempo (passi)')
    ax1.set_ylabel('Temperatura (°C)')
    ax1.set_title('Controllo Temperatura tramite Agente Predittivo')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Grafico azioni
    ax2.plot(passi, azioni, 'orange', linewidth=2)
    ax2.set_xlabel('Tempo (passi)')
    ax2.set_ylabel('Potenza Riscaldamento (0-10)')
    ax2.set_title('Azioni del Controller')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('agente_predittivo_risultati.png', dpi=150)
    print("\n✓ Grafici salvati in 'agente_predittivo_risultati.png'")
    plt.show()


if __name__ == "__main__":
    print("=" * 60)
    print("AGENTE AI PREDITTIVO - DEMO")
    print("Scenario: Controllo temperatura di una stanza")
    print("=" * 60 + "\n")
    
    esegui_simulazione(num_passi=100)
    
    print("\n" + "=" * 60)
    print("COME FUNZIONA:")
    print("1. L'agente inizia senza conoscenza del sistema")
    print("2. Raccoglie dati osservando temperatura e azioni")
    print("3. Apprende un modello predittivo (regressione lineare)")
    print("4. Usa il modello per predire effetti delle azioni")
    print("5. Sceglie l'azione che minimizza l'errore futuro")
    print("=" * 60)
