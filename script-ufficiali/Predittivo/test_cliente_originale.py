# test_cliente.py
"""
🔮 TEST CLIENTE - SISTEMA COMPLETO DI TEST E PREDIZIONE AI
Questo file permette di testare nuovi clienti, calcolare valori finanziari,
prevedere con AI e salvare tutto nel database.
"""

import pandas as pd
import joblib
import pymysql
from calcoli import FinancialCalculator
from update_db import DatabaseUpdater

class ClienteTester:
    """
    🎯 CLASSE PRINCIPALE PER TESTARE NUOVI CLIENTI
    Combina calcoli finanziari, predizione AI e salvataggio database
    """
    
    def __init__(self):
        # Inizializza il calcolatore finanziario
        self.calculator = FinancialCalculator()
        
        # Inizializza l'aggiornatore del database
        self.db_updater = DatabaseUpdater()
        
        # Variabili per il modello AI (inizialmente vuote)
        self.model = None           # Modello Random Forest addestrato
        self.label_encoders = None  # Traduttori testo → numeri
        self.scaler = None          # Normalizzatore numeri
        
        # Configurazione connessione database MySQL
        self.db_config = {
            'host': "localhost",
            'user': "asugamele", 
            'password': "83Asugamele@",
            'database': "projectAI",
            'cursorclass': pymysql.cursors.DictCursor
        }
    
    def load_model(self, filename='car_predictor.pkl'):
        """
        📥 CARICA IL MODELLO AI ADDESTRATO
        Il file .pkl contiene tutto ciò che serve per fare predizioni
        """
        try:
            print(f"🔄 Caricamento modello AI da {filename}...")
            model_data = joblib.load(filename)
            
            # Estrai tutti i componenti dal file salvato
            self.model = model_data['model']           # Modello Random Forest
            self.scaler = model_data['scaler']         # Normalizzatore
            self.label_encoders = model_data['label_encoders']  # Traduttori
            self.feature_importance = model_data['feature_importance']  # Importanza features
            
            print("✅ Modello AI caricato correttamente")
            print(f"   - Decisioni possibili: {list(self.label_encoders['target'].classes_)}")
            print(f"   - Features utilizzate: {len(self.feature_importance)}")
            return True
            
        except Exception as e:
            print(f"❌ Errore caricamento modello: {e}")
            print("ℹ️  Il sistema userà solo i calcoli finanziari (senza AI)")
            return False
    
    def get_id_from_table(self, table_name, testo):
        """
        🔍 CERCA ID IN UNA TABELLA LOOKUP
        Converte valori come "Nuova", "Usata" negli ID del database
        """
        conn = pymysql.connect(**self.db_config)
        try:
            with conn.cursor() as cursor:
                # Cerca case-insensitive (NUOVA = Nuova = nuova)
                cursor.execute(f"SELECT id FROM {table_name} WHERE upper(testo) = upper(%s)", (testo.upper(),))
                result = cursor.fetchone()
                
                if not result:
                    # Se non trova, mostra i valori disponibili per aiutare il debug
                    cursor.execute(f"SELECT testo FROM {table_name}")
                    disponibili = [row['testo'] for row in cursor.fetchall()]
                    raise Exception(f"ID non trovato per '{testo}' in {table_name}. Valori disponibili: {disponibili}")
                
                return result['id']
        except Exception as e:
            raise e
        finally:
            conn.close()
    
    def _predici_con_ai(self, dati_completi):
        """
        🔮 FUNZIONE PRINCIPALE DI PREDIZIONE AI
        Prende i dati di un cliente e restituisce la decisione predetta
        """
        print("   🤖 Elaborazione dati per AI...")
        
        # 1. CONVERTI I DATI IN DATAFRAME
        # Il modello si aspetta una tabella, anche con una sola riga
        df = pd.DataFrame([dati_completi])
        
        # 2. APPLICA ENCODING ALLE FEATURES CATEGORICHE
        # Il modello capisce solo numeri, quindi convertiamo:
        # "Nuova" → 0, "Usata" → 1, "Si" → 0, "No" → 1, ecc.
        for feature, encoder in self.label_encoders.items():
            if feature != 'target' and feature in df.columns:
                try:
                    if df[feature].iloc[0] in encoder.classes_:
                        # Traduci il valore testo nel numero corrispondente
                        df[feature] = encoder.transform([df[feature].iloc[0]])[0]
                        print(f"      ✅ {feature} encoded: {df[feature].iloc[0]}")
                    else:
                        # Valore non visto durante il training, usa default
                        print(f"      ⚠️  {feature}: valore '{df[feature].iloc[0]}' non visto in training, uso default")
                        df[feature] = 0
                except Exception as e:
                    print(f"      ❌ Errore encoding {feature}: {e}")
                    df[feature] = 0
        
        # 3. SELEZIONA SOLO LE FEATURES USATE NEL TRAINING
        # Prende l'elenco delle colonne che il modello si aspetta
        feature_columns = self.feature_importance['feature'].tolist()
        available_columns = [col for col in feature_columns if col in df.columns]
        df_processed = df[available_columns]
        
        print(f"   📊 Features utilizzate: {len(available_columns)}/{len(feature_columns)}")
        
        # 4. APPLICA SCALING (NORMALIZZAZIONE)
        # Porta tutti i numeri sulla stessa scala (media=0, deviazione=1)
        df_scaled = self.scaler.transform(df_processed)
        
        # 5. FAI LA PREDIZIONE CON IL MODELLO
        print("   🎯 Consultazione modello AI...")
        prediction_encoded = self.model.predict(df_scaled)[0]  # Decisione come numero
        prediction_proba = self.model.predict_proba(df_scaled)[0]  # Probabilità per ogni decisione
        
        # 6. DECODIFICA LA RISPOSTA
        # Converti il numero nella decisione leggibile
        prediction = self.label_encoders['target'].inverse_transform([prediction_encoded])[0]
        
        # 7. PREPARA IL RISULTATO
        risultato = {
            'decisione_prevista': prediction,
            'probabilita': max(prediction_proba),  # Probabilità della decisione scelta
            'tutte_probabilita': dict(zip(
                self.label_encoders['target'].classes_,  # Nomi delle decisioni
                prediction_proba  # Probabilità per ogni decisione
            ))
        }
        
        print(f"   ✅ Decisione AI: {risultato['decisione_prevista']} ({risultato['probabilita']:.1%})")
        return risultato
    
    def salva_cliente_sul_db(self, dati_originali, calcoli, predizione_ai, simulazione):
        """
        💾 SALVA TUTTI I DATI NEL DATABASE
        Crea un nuovo record con tutti i calcoli e le predizioni
        """
        print("💾 Preparazione salvataggio database...")
        
        conn = pymysql.connect(**self.db_config)
        try:
            with conn.cursor() as cursor:
                # 🎯 DETERMINA LA FORMULA DI ACQUISTO IN BASE ALLA DECISIONE AI
                if predizione_ai['decisione_prevista'] == "Bonifico":
                    formula_acquisto = "totale con bonifico"
                elif predizione_ai['decisione_prevista'] == "Finanziamento a 3 anni auto nuova":
                    formula_acquisto = "finanziamento a 3 anni auto nuova"
                else:
                    formula_acquisto = "finanziamento classico auto usata"
                
                # 📝 PREPARA I DATI PER L'INSERIMENTO
                insert_data = {
                    'cliente': f"Cliente_Test_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}",
                    'eta': dati_originali.get('eta', 30),
                    'neo_patentato_id': self.get_id_from_table('neo_patentato', dati_originali.get('neo_patentato', 'No')),
                    'nr_figli': dati_originali.get('nr_figli', 0),
                    'reddito_mensie': float(dati_originali['reddito_mensile']),
                    'altre_spese': float(dati_originali['altre_spese']),
                    'diff_reddito': calcoli['diff_reddito'],
                    'sesso_id': self.get_id_from_table('sesso', dati_originali.get('sesso', 'uomo')),
                    'zona_id': self.get_id_from_table('zona', dati_originali.get('zona', 'nord ovest')),
                    'tipologia_auto_id': self.get_id_from_table('tipologia_auto', dati_originali['tipologia_auto']),
                    'nuovo_usato_id': self.get_id_from_table('nuovo_usato', dati_originali['nuovo_usato']),
                    'costo_auto': float(dati_originali['costo_auto']),
                    'eta_veicolo': 0,
                    'oneri_accessori': float(dati_originali['costo_auto']) * 0.001,  # 0.1% del costo auto
                    'anticipo': float(dati_originali.get('anticipo_perc', 0)),
                    'tan': float(dati_originali.get('tan', 5.0)),
                    'formula_acquisto_id': self.get_id_from_table('formula_acquisto', formula_acquisto),
                    'nr_rate': int(dati_originali.get('nr_rate', 36)),
                    'importo_finanziato': calcoli['importo_finanziato'],
                    'rata': calcoli['rata'],
                    'sostenibilita': calcoli['sostenibilita'],
                    'coefficiente_K': calcoli['coefficiente_K'],
                    're': calcoli['re'],
                    'rs': calcoli['rs'],
                    'rd': calcoli['rd'],
                    'rt': calcoli['rt'],
                    'decisione_AI': predizione_ai['decisione_prevista'],
                    'is_simulation': 'S' if predizione_ai['decisione_prevista'] == 'Revisione con simulazione' else 'N'
                }
                
                # 🗃️ INSERISCE IL CLIENTE NELLA TABELLA PRINCIPALE
                columns = ', '.join(insert_data.keys())
                placeholders = ', '.join(['%s'] * len(insert_data))
                query = f"INSERT INTO model ({columns}) VALUES ({placeholders})"
                
                cursor.execute(query, list(insert_data.values()))
                conn.commit()
                last_id = cursor.lastrowid
                print(f"✅ Cliente principale salvato con ID: {last_id}")
                
                # 🔄 SALVA LE SIMULAZIONI SE PRESENTI
                if simulazione:
                    print(f"   📊 Soluzione consigliata: {simulazione['soluzione_consigliata']}")
                    
                    # Simulazione Anticipo (solo per auto usata)
                    if simulazione['simulazione_anticipo_solo_auto_usata']:
                        insert_sim_a = {
                            'model_id': last_id,
                            'simulation_type_id': 1,
                            'anticipo': simulazione['simulazione_anticipo_solo_auto_usata']['anticipo'],
                            'importo_finanziamento': simulazione['simulazione_anticipo_solo_auto_usata']['importo_fin'],
                            'importo_rata': simulazione['simulazione_anticipo_solo_auto_usata']['importo_rata'],
                            'sostenibilita': simulazione['simulazione_anticipo_solo_auto_usata']['sostenibilita'],
                            'decisione': simulazione['simulazione_anticipo_solo_auto_usata']['decisione_finale'],
                            'decision_AI': simulazione['soluzione_consigliata'],
                        }
                        columns_a = ', '.join(insert_sim_a.keys())
                        placeholders_a = ', '.join(['%s'] * len(insert_sim_a))
                        cursor.execute(f"INSERT INTO simulation ({columns_a}) VALUES ({placeholders_a})", list(insert_sim_a.values()))
                        conn.commit()
                        print("   ✅ Simulazione anticipo salvata")
                    
                    # Simulazione Aumento Rate (sempre presente)
                    if simulazione['simulazione_nr_rate']:
                        insert_sim_b = {
                            'model_id': last_id,
                            'simulation_type_id': 2,
                            'nr_rata': simulazione['simulazione_nr_rate']['nr_rata_new'],
                            'rata': simulazione['simulazione_nr_rate']['importo_rata'],
                            'sostenibilita': simulazione['simulazione_nr_rate']['sostenibilita'],
                            'decisione': simulazione['simulazione_nr_rate']['decisione_finale'],
                            'decision_AI': simulazione['soluzione_consigliata'],
                        }
                        columns_b = ', '.join(insert_sim_b.keys())
                        placeholders_b = ', '.join(['%s'] * len(insert_sim_b))
                        cursor.execute(f"INSERT INTO simulation ({columns_b}) VALUES ({placeholders_b})", list(insert_sim_b.values()))
                        conn.commit()
                        print("   ✅ Simulazione aumento rate salvata")
                
                return last_id
                
        except Exception as e:
            print(f"❌ Errore salvataggio DB: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def testa_nuovo_cliente(self, dati_cliente):
        """
        🚀 FUNZIONE PRINCIPALE - TESTA UN NUOVO CLIENTE COMPLETO
        Combina calcoli finanziari, predizione AI e salvataggio database
        """
        print("\n" + "="*60)
        print("🚀 AVVIO TEST CLIENTE COMPLETO")
        print("="*60)
        
        # 1. 🧮 CALCOLI FINANZIARI
        print("\n📊 FASE 1: CALCOLI FINANZIARI")
        print("-" * 30)
        
        calcoli = self.calculator.calcola_tutti_i_valori(dati_cliente)
        
        if not calcoli['calcoli_completati']:
            print("❌ Errore nei calcoli finanziari")
            return None
        
        # Mostra i risultati dei calcoli
        print("✅ Calcoli completati:")
        risultati_principali = ['diff_reddito', 'importo_finanziato', 'rata', 
                               'sostenibilita', 'coefficiente_K', 're', 'rs', 'rd', 'rt', 'decisione_AI']
        for key in risultati_principali:
            if key in calcoli:
                print(f"   • {key}: {calcoli[key]}")
        
        # 2. 🔍 SIMULAZIONI (se necessarie)
        sim = None
        if calcoli.get('simulazione'):
            print("\n📈 FASE 2: SIMULAZIONI")
            print("-" * 30)
            sim = calcoli['simulazione']
            
            # Mostra dettagli simulazione
            if sim['simulazione_anticipo_solo_auto_usata']:
                print("   🎯 Simulazione Anticipo (auto usata):")
                for k, v in sim['simulazione_anticipo_solo_auto_usata'].items():
                    print(f"      {k}: {v}")
            
            if sim['simulazione_nr_rate']:
                print("   📅 Simulazione Aumento Rate:")
                for k, v in sim['simulazione_nr_rate'].items():
                    print(f"      {k}: {v}")
            
            print(f"   💡 Soluzione Consigliata: {sim['soluzione_consigliata']}")
        
        # 3. 🤖 PREDIZIONE AI (se modello disponibile)
        predizione_ai = None
        if self.model is not None:
            print("\n🧠 FASE 3: PREDIZIONE INTELLIGENZA ARTIFICIALE")
            print("-" * 30)
            
            try:
                # Prepara tutti i dati per la predizione
                dati_predizione = {
                    **dati_cliente,  # Dati originali del cliente
                    'diff_reddito': calcoli['diff_reddito'],
                    'importo_finanziato': calcoli['importo_finanziato'],
                    'rata': calcoli['rata'],
                    'sostenibilita': calcoli['sostenibilita'],
                    'coefficiente_K': calcoli['coefficiente_K'],
                    're': calcoli['re'],
                    'rs': calcoli['rs'],
                    'rd': calcoli['rd'],
                    'rt': calcoli['rt']
                }
                
                predizione_ai = self._predici_con_ai(dati_predizione)
                
                # Mostra tutte le probabilità
                print("   📈 Probabilità per ogni decisione:")
                for decisione, prob in predizione_ai['tutte_probabilita'].items():
                    print(f"      {decisione}: {prob:.2%}")
                    
            except Exception as e:
                print(f"❌ Errore predizione AI: {e}")
                predizione_ai = {'decisione_prevista': calcoli['decisione_AI'], 'probabilita': 1.0}
        else:
            print("\nℹ️  FASE 3: DECISIONE BASATA SU CALCOLI (AI non disponibile)")
            print("-" * 30)
            predizione_ai = {'decisione_prevista': calcoli['decisione_AI'], 'probabilita': 1.0}
            print(f"✅ Decisione: {predizione_ai['decisione_prevista']}")
        
        # 4. 💾 SALVATAGGIO DATABASE
        print("\n💾 FASE 4: SALVATAGGIO DATABASE")
        print("-" * 30)
        
        id_inserito = self.salva_cliente_sul_db(dati_cliente, calcoli, predizione_ai, sim)
        
        if id_inserito:
            print(f"✅ Cliente salvato con ID: {id_inserito}")
            
            # 5. 🔄 AGGIORNAMENTO AUTOMATICO (opzionale)
            print("\n🔄 FASE 5: AGGIORNAMENTO CALCOLI")
            print("-" * 30)
            try:
                if self.db_updater.aggiorna_record(id_inserito):
                    print("✅ Calcoli verificati e aggiornati")
                else:
                    print("⚠️  Impossibile verificare i calcoli")
            except Exception as e:
                print(f"⚠️  Errore durante l'aggiornamento: {e}")
        
        # 6. 📋 RISULTATO FINALE
        print("\n🎯 RISULTATO FINALE DEL TEST")
        print("=" * 40)
        if id_inserito:
            print(f"✅ SUCCESSO! Cliente processato correttamente")
            print(f"   📝 ID Database: {id_inserito}")
            print(f"   🎯 Decisione: {predizione_ai['decisione_prevista']}")
            print(f"   📊 Affidabilità: {predizione_ai['probabilita']:.1%}")
        else:
            print("❌ TEST FALLITO - Cliente non salvato")
        
        return {
            'calcoli_finanziari': calcoli,
            'predizione_ai': predizione_ai,
            'id_database': id_inserito
        }
    
    def aggiorna_tutto_il_database(self):
        """
        🗃️ AGGIORNA TUTTI I RECORD NEL DATABASE
        Utility per ricalcolare tutti i valori esistenti
        """
        print("\n🔄 AVVIO AGGIORNAMENTO COMPLETO DATABASE")
        print("=" * 50)
        self.db_updater.aggiorna_tutti_i_record()

def main():
    """
    🎯 FUNZIONE PRINCIPALE - ESEMPIO DI UTILIZZO
    Crea e testa un cliente di esempio
    """
    # Inizializza il tester
    tester = ClienteTester()
    
    print("🚗 SISTEMA DI TEST CLIENTI - AGENTE AI PREDITTIVO")
    print("=" * 55)
    
    # Prova a caricare il modello AI
    print("🔄 Caricamento risorse...")
    modello_caricato = tester.load_model('car_predictor.pkl')
    
    # DEFINIZIONE CLIENTE DI TEST
    # Puoi modificare questi valori per testare scenari diversi
    cliente_test = {
        'eta': 35,
        'reddito_mensile': 2500,
        'altre_spese': 400,
        'costo_auto': 28000,
        'tipologia_auto': 'suv',
        'nuovo_usato': 'Usata',  # Prova anche con 'Nuova'
        'neo_patentato': 'No',
        'nr_figli': 1,
        'sesso': 'uomo',
        'zona': 'nord ovest',
        'nr_rate': 60,
        'tan': 5.0,
        'anticipo_perc': 0  # Per auto usata non ha effetto in prima istanza
    }
    
    # Mostra i dati del cliente di test
    print("\n👤 CLIENTE DI TEST CONFIGURATO:")
    print("-" * 35)
    for key, value in cliente_test.items():
        print(f"   {key}: {value}")
    
    # ESEGUI IL TEST COMPLETO
    risultati = tester.testa_nuovo_cliente(cliente_test)
    
    # OPZIONE PER AGGIORNARE TUTTO IL DATABASE
    if risultati and risultati['id_database']:
        aggiorna_tutto = input("\n🔄 Vuoi aggiornare tutti i record nel database? (s/n): ")
        if aggiorna_tutto.lower() == 's':
            tester.aggiorna_tutto_il_database()
    
    print("\n" + "="*55)
    print("🎉 TEST COMPLETATO!")
    print("="*55)

# Esegui il test quando il file viene lanciato direttamente
if __name__ == "__main__":
    main()
