# Spiegazione Dettagliata dello Script - Agente Predittivo

## Panoramica Generale

Lo script implementa un **sistema di controllo predittivo** per mantenere la temperatura di una stanza a un valore target (22°C). È un esempio pratico di **Model Predictive Control (MPC)** semplificato.

---

## 1. Classe `AmbienteStanza` - Il Mondo Simulato

```python
class AmbienteStanza:
    def __init__(self, temp_iniziale=20, temp_esterna=10):
        self.temp_corrente = temp_iniziale
        self.temp_esterna = temp_esterna
        self.dispersione = 0.1
```

### Cosa fa
Simula la fisica termica di una stanza usando un modello semplificato.

### Parametri chiave
- **temp_corrente**: temperatura attuale della stanza
- **temp_esterna**: temperatura fuori dalla stanza (costante a 10°C)
- **dispersione**: coefficiente di dispersione termica (0.1 = 10% per step)

### Metodo `step(riscaldamento)`

```python
dispersione = (self.temp_corrente - self.temp_esterna) * self.dispersione
self.temp_corrente = self.temp_corrente - dispersione + riscaldamento
```

**Formula fisica applicata:**
```
ΔT = -k(T_interno - T_esterno) + P_riscaldamento + rumore
```

- Se la stanza è più calda dell'esterno → perde calore (dispersione)
- Il riscaldamento aggiunge calore
- Il rumore gaussiano simula variabilità del mondo reale

### Esempio pratico
```
Temp corrente = 25°C
Temp esterna = 10°C
Dispersione = (25 - 10) × 0.1 = 1.5°C persi
Riscaldamento = 2°C aggiunti
Nuova temp = 25 - 1.5 + 2 = 25.5°C (+ rumore)
```

---

## 2. Classe `AgentePredittivo` - Il Cervello del Sistema

### Struttura dati principale

```python
self.storia = deque(maxlen=20)  # Buffer circolare
```

**Deque** (double-ended queue): mantiene gli ultimi 20 stati osservati. Quando si raggiunge il limite, elimina automaticamente il dato più vecchio. Questo è cruciale per:
- Non sovraccaricare la memoria
- Dare più peso ai dati recenti
- Adattarsi a cambiamenti nell'ambiente

---

### Fase 1: Osservazione - `osserva(temp, azione)`

```python
def osserva(self, temp, azione):
    self.storia.append((temp, azione))
   
    if len(self.storia) >= 10 and not self.addestrato:
        self._addestra_modello()
```

**Cosa succede:**
1. Salva la coppia (temperatura, azione) nella storia
2. Quando ha raccolto almeno 10 campioni → addestra il modello
3. Questo è **apprendimento supervisionato** dai propri dati

**Perché 10 campioni?**
- Troppo pochi → modello instabile
- Troppi → lento ad adattarsi
- 10 è un buon compromesso per questo problema semplice

---

### Fase 2: Apprendimento - `_addestra_modello()`

```python
X = []  # [temp_corrente, azione]
y = []  # temp_prossima

for i in range(len(dati) - 1):
    temp_curr, azione = dati[i]
    temp_next = dati[i+1][0]
    X.append([temp_curr, azione])
    y.append(temp_next)

self.modello.fit(X, y)
```

**Cosa impara il modello:**
```
Funzione: f(temp_attuale, azione) → temp_futura
```

### Esempio di training
```
Dati raccolti:
Step 1: T=18°C, A=5 → T_next=20°C
Step 2: T=20°C, A=3 → T_next=21°C
Step 3: T=21°C, A=2 → T_next=21.5°C

Il modello impara la relazione:
"Se temperatura è X e applico riscaldamento Y,
la temperatura diventerà circa Z"
```

**Tipo di modello: LinearRegression**
```
temp_next = β₀ + β₁×temp_curr + β₂×azione
```

Esempio di coefficienti appresi:
```
temp_next = 2.0 + 0.85×temp_curr + 0.4×azione
```

Interpretazione:
- **β₁ = 0.85**: la temperatura tende a persistere (con un po' di dispersione)
- **β₂ = 0.4**: ogni unità di riscaldamento aggiunge ~0.4°C

---

### Fase 3: Predizione - `predici(temp_corrente, azione_proposta)`

```python
X_pred = np.array([[temp_corrente, azione_proposta]])
temp_predetta = self.modello.predict(X_pred)[0]
```

**Funzione:**
Dato lo stato attuale e un'azione ipotetica, predice quale sarà la temperatura al prossimo step.

**Esempio:**
```
Input: T=20°C, A=5
Output: T_predetta = 22.3°C

Calcolo interno (con coefficienti esempio):
2.0 + 0.85×20 + 0.4×5 = 2 + 17 + 2 = 21°C
```

---

### Fase 4: Decisione - `decidi_azione(temp_corrente)`

Questa è la parte più importante! Implementa **Model Predictive Control**.

#### Caso 1: Modello NON addestrato (primi 10 step)

```python
errore = self.target_temp - temp_corrente
azione = max(0, min(10, errore * 2))
```

**Controllo proporzionale semplice:**
- Se T=18°C e target=22°C → errore=4°C → azione=8
- Se T=23°C e target=22°C → errore=-1°C → azione=0 (min)

È un fallback robusto quando non ha ancora imparato.

#### Caso 2: Modello addestrato - MPC Semplificato

```python
azioni_possibili = np.linspace(0, 10, 20)  # 20 azioni da testare

for azione in azioni_possibili:
    temp_pred = self.predici(temp_corrente, azione)
    errore = abs(temp_pred - self.target_temp)
    costo_energia = 0.01 * (azione ** 2)
    costo_totale = errore + costo_energia
   
    if costo_totale < minimo_errore:
        migliore_azione = azione
```

**Algoritmo di ottimizzazione:**

1. **Genera candidati**: testa 20 possibili azioni (0, 0.5, 1, ..., 10)

2. **Predici risultato**: per ogni azione, predice la temperatura futura

3. **Calcola costo**:
   ```
   Costo = |T_predetta - T_target| + 0.01×(azione²)
   ```
  
   - **Termine 1**: errore di temperatura (quanto ci allontaniamo dal target)
   - **Termine 2**: penalità energetica (favorisce azioni moderate)

4. **Seleziona ottimo**: sceglie l'azione con costo minimo

### Esempio pratico di decisione

```
Stato: T_corrente = 20°C, Target = 22°C

Test azioni:
A=0  → T_pred=19.5°C → errore=2.5  → costo=2.50 + 0.00 = 2.50
A=2  → T_pred=20.5°C → errore=1.5  → costo=1.50 + 0.04 = 1.54
A=4  → T_pred=21.8°C → errore=0.2  → costo=0.20 + 0.16 = 0.36 ✓ MIGLIORE
A=6  → T_pred=23.0°C → errore=1.0  → costo=1.00 + 0.36 = 1.36
A=10 → T_pred=25.0°C → errore=3.0  → costo=3.00 + 1.00 = 4.00

Scelta: A=4 (equilibrio tra precisione ed efficienza)
```

---

## 3. Loop Principale - `esegui_simulazione()`

```python
for t in range(num_passi):
    temp_corrente = ambiente.temp_corrente
    azione = agente.decidi_azione(temp_corrente)     # 1. Pianifica
    nuova_temp = ambiente.step(azione)               # 2. Esegui
    agente.osserva(temp_corrente, azione)            # 3. Impara
```

### Ciclo Sense-Think-Act

```
┌─────────────┐
│  PERCEZIONE │ ← Legge temperatura
└──────┬──────┘
       │
┌──────▼──────┐
│  PREDIZIONE │ ← Simula mentalmente azioni possibili
└──────┬──────┘
       │
┌──────▼──────┐
│   AZIONE    │ ← Esegue l'azione scelta
└──────┬──────┘
       │
┌──────▼──────┐
│ APPRENDIMENTO│ ← Osserva risultato e aggiorna modello
└─────────────┘
```

---

## 4. Evoluzione del Comportamento nel Tempo

### Step 0-10: Fase di Esplorazione
```
Comportamento: Casuale/Proporzionale
Il controller usa controllo proporzionale grezzo
Raccoglie dati per l'apprendimento
```

### Step 10-30: Fase di Apprendimento
```
Comportamento: Inizia a usare predizioni
Il modello è addestrato ma ancora impreciso
Oscillazioni visibili mentre affina le predizioni
```

### Step 30+: Fase di Controllo Stabile
```
Comportamento: Controllo preciso
Il modello è accurato
Mantiene temperatura vicino al target con azioni moderate
```

---

## 5. Concetti Chiave Implementati

### Model-Based Reinforcement Learning
L'agente impara un **modello del mondo** (come la temperatura risponde) invece di imparare direttamente una policy.

**Vantaggio**: Può "simulare" azioni nella sua mente prima di eseguirle.

### Receding Horizon
Predice solo 1 step avanti (potrebbe essere esteso a N step).
Ricalcola la strategia ad ogni passo = adattamento continuo.

### Online Learning
Il modello continua a raccogliere dati durante l'esecuzione.
Può adattarsi a cambiamenti nell'ambiente (es. se la dispersione cambia).

### Trade-off Multi-Obiettivo
```
min: errore_temperatura + λ×costo_energia
```
Bilancia accuratezza e efficienza (parametro λ = 0.01).

---

## 6. Limitazioni e Possibili Miglioramenti

### Limitazioni attuali
- **Modello lineare**: potrebbe non catturare dinamiche complesse
- **Orizzonte corto**: predice solo 1 step avanti
- **No gestione incertezza**: non modellizza la varianza delle predizioni

### Miglioramenti possibili

1. **Modello più sofisticato**
   ```python
   from sklearn.neural_network import MLPRegressor
   self.modello = MLPRegressor(hidden_layer_sizes=(10,10))
   ```

2. **Orizzonte più lungo**
   ```python
   # Predici N step avanti e ottimizza sequenza di azioni
   for n in range(N):
       temp = predici(temp, azione[n])
   ```

3. **Gestione incertezza**
   ```python
   # Usa ensemble di modelli o Gaussian Process
   temp_pred, uncertainty = modello.predict_with_uncertainty(X)
   ```

4. **Adaptive learning rate**
   ```python
   # Re-addestra periodicamente per adattarsi
   if t % 50 == 0:
       self._addestra_modello()
   ```

---

## 7. Output dello Script

### Console
```
Passo 0: Temp=18.0°C, Azione=8.0, Target=22°C
✓ Modello addestrato con 10 campioni
Passo 20: Temp=21.8°C, Azione=3.2, Target=22°C
Passo 40: Temp=22.1°C, Azione=1.8, Target=22°C
```

### Grafico
- **Linea blu**: temperatura reale nel tempo
- **Linea rossa tratteggiata**: target (22°C)
- **Punti verdi**: predizioni dell'agente
- **Grafico inferiore**: potenza del riscaldamento usata

**Pattern tipico:**
1. Inizialmente: grandi oscillazioni
2. Dopo addestramento: convergenza rapida
3. A regime: piccole correzioni attorno al target

---

## Conclusioni

Questo script dimostra i principi fondamentali degli agenti predittivi:

✅ **Apprendimento da esperienza diretta**
✅ **Predizione degli effetti delle azioni**
✅ **Ottimizzazione basata su modello**
✅ **Adattamento continuo**

È un esempio minimalista ma completo di come costruire un sistema AI che impara a controllare un processo dinamico! 
