# test_cliente.py
import pandas as pd
import joblib
import pymysql
from calcoli import FinancialCalculator
from update import DatabaseUpdater  # Importa il nuovo modulo

class ClienteTester:
    """
    Classe per testare nuovi clienti e salvarli sul DB
    """
    
    def __init__(self):
        self.calculator = FinancialCalculator()
        self.db_updater = DatabaseUpdater()  # Aggiungi l'updater
        self.model = None
        self.label_encoders = None
        self.scaler = None
        
        # Configurazione DB
        self.db_config = {
            'host': "localhost",
            'user': "asugamele", 
            'password': "83Asugamele@",
            'database': "projectAI",
            'cursorclass': pymysql.cursors.DictCursor
        }
    
    def load_model(self, filename='car_predictor.pkl'):
        """Carica il modello addestrato"""
        try:
            model_data = joblib.load(filename)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoders = model_data['label_encoders']
            print("✅ Modello AI caricato")
            return True
        except Exception as e:
            print(f"❌ Errore caricamento modello: {e}")
            return False
    
    def get_id_from_table(self, table_name, testo):
        """Ottiene ID da una tabella lookup"""
        conn = pymysql.connect(**self.db_config)
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT id FROM {table_name} WHERE upper(testo) = upper(%s)", (testo.upper(),))
                result = cursor.fetchone()
                if not result:
                    # Crea una lista dei valori disponibili per aiutare il debug
                    cursor.execute(f"SELECT testo FROM {table_name}")
                    disponibili = [row['testo'] for row in cursor.fetchall()]
                    raise Exception(f"ID non trovato per '{testo}' in {table_name}. Valori disponibili: {disponibili}")
                return result['id']
        except Exception as e:
           raise e
        finally:
            conn.close()
    
    def salva_cliente_sul_db(self, dati_originali, calcoli, predizione_ai, simulazione):
        """Salva il nuovo cliente sul database"""
        conn = pymysql.connect(**self.db_config)
        try:
            with conn.cursor() as cursor:
                # Determina formula_acquisto_id in base alla decisione
                if predizione_ai['decisione_prevista'] == "Bonifico":
                    formula_acquisto = "totale con bonifico"
                elif predizione_ai['decisione_prevista'] == "Finanziamento a 3 anni auto nuova":
                    formula_acquisto = "finanziamento a 3 anni auto nuova"
                else:
                    formula_acquisto = "finanziamento classico auto usata"
                
                # Prepara i dati per l'inserimento
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
                    'is_simulation': 'S' if predizione_ai['decisione_prevista'] =='Revisione con simulazione' else 'N'
                }
                
                # Query di inserimento
                columns = ', '.join(insert_data.keys())
                placeholders = ', '.join(['%s'] * len(insert_data))
                query = f"INSERT INTO model ({columns}) VALUES ({placeholders})"
                
                cursor.execute(query, list(insert_data.values()))
                conn.commit()
                last_id = cursor.lastrowid
                
                # Salva le simulazioni se presenti
                if simulazione:
                    # Simulazione Anticipo (solo se presente)
                    if simulazione['simulazione_anticipo_solo_auto_usata']:
                        insert_sim_a = {
                            'model_id': last_id,
                            'simulation_type_id': 1,
                            'anticipo': simulazione['simulazione_anticipo_solo_auto_usata']['anticipo'],
                            'importo_finanziamento': simulazione['simulazione_anticipo_solo_auto_usata']['importo_fin'],
                            'importo_rata': simulazione['simulazione_anticipo_solo_auto_usata']['importo_rata'],
                            'sostenibilita': simulazione['simulazione_anticipo_solo_auto_usata']['sostenibilita'],
                            'decisione': simulazione['simulazione_anticipo_solo_auto_usata']['decisione_finale'],
                            'decision_AI': simulazione['soluzione_consigliata'] if simulazione['soluzione_consigliata'] else None,
                        }
                        columns_a = ', '.join(insert_sim_a.keys())
                        placeholders_a = ', '.join(['%s'] * len(insert_sim_a))
                        cursor.execute(f"INSERT INTO simulation ({columns_a}) VALUES ({placeholders_a})", list(insert_sim_a.values()))
                        conn.commit()
                    
                    # Simulazione Aumento Rate (sempre presente)
                    if simulazione['simulazione_nr_rate']:
                        insert_sim_b = {
                            'model_id': last_id,
                            'simulation_type_id': 2,
                            'nr_rata': simulazione['simulazione_nr_rate']['nr_rata_new'],
                            'rata': simulazione['simulazione_nr_rate']['importo_rata'],
                            'sostenibilita': simulazione['simulazione_nr_rate']['sostenibilita'],
                            'decisione': simulazione['simulazione_nr_rate']['decisione_finale'],
                            'decision_AI': simulazione['soluzione_consigliata'] if simulazione['soluzione_consigliata'] else None,
                        }
                        columns_b = ', '.join(insert_sim_b.keys())
                        placeholders_b = ', '.join(['%s'] * len(insert_sim_b))
                        cursor.execute(f"INSERT INTO simulation ({columns_b}) VALUES ({placeholders_b})", list(insert_sim_b.values()))
                        conn.commit()
                
                print("💾 Cliente salvato sul database!")
                return last_id
                
        except Exception as e:
            print(f"❌ Errore salvataggio DB: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def testa_nuovo_cliente(self, dati_cliente):
        """
        Testa un nuovo cliente completo:
        1. Calcola valori finanziari
        2. Prevede con AI
        3. Se revisione, calcola simulazione
        4. Salva sul DB
        5. Aggiorna i calcoli nel DB
        """
        calcoli = self.calculator.calcola_tutti_i_valori(dati_cliente)
        
        if not calcoli['calcoli_completati']:
            print("❌ Errore nei calcoli finanziari")
            return
    
        sim = None
        # 2. Mostra simulazione se presente
        if calcoli.get('simulazione'):
            sim = calcoli['simulazione']
            
            # Mostra dettagli simulazione
            if sim['simulazione_anticipo_solo_auto_usata']:
                print("   📊 Simulazione Anticipo (solo auto usata):")
                for k, v in sim['simulazione_anticipo_solo_auto_usata'].items():
                    print(f"      {k}: {v}")
            
            print("   📊 Simulazione Aumento Rate:")
            for k, v in sim['simulazione_nr_rate'].items():
                print(f"      {k}: {v}")
            
            print(f"   🎯 Soluzione Consigliata: {sim['soluzione_consigliata']}")
        
        # 3. Previsione AI (se il modello è caricato)
        predizione_ai = None
        if self.model is not None:
            print("\n🔮 PREVISIONE AI...")
            try:
                # Prepara dati per la predizione
                dati_predizione = {
                    **dati_cliente,
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
                print(f"✅ Decisione AI: {predizione_ai['decisione_prevista']}")
                print(f"📊 Probabilità: {predizione_ai['probabilita']:.1%}")
                
            except Exception as e:
                print(f"⚠️  Errore predizione AI: {e}")
                predizione_ai = {'decisione_prevista': calcoli['decisione_AI'], 'probabilita': 1.0}
        else:
            print("⚠️  Usando decisione calcolata (modello AI non caricato)")
            predizione_ai = {'decisione_prevista': calcoli['decisione_AI'], 'probabilita': 1.0}
        
        # 4. Salva sul database
        print("\n💾 SALVATAGGIO DATABASE...")
        id_inserito = self.salva_cliente_sul_db(dati_cliente, calcoli, predizione_ai, sim)
        
        if id_inserito:
            print(f"✅ Cliente salvato con ID: {id_inserito}")
            
            # 5. AGGIORNA I CALCOLI NEL DATABASE (NUOVO)
            print("\n🔄 AGGIORNAMENTO CALCOLI NEL DATABASE...")
            try:
                if self.db_updater.aggiorna_record(id_inserito):
                    print("✅ Calcoli aggiornati nel database")
                else:
                    print("⚠️  Impossibile aggiornare i calcoli nel database")
            except Exception as e:
                print(f"⚠️  Errore durante l'aggiornamento: {e}")
        
        return {
            'calcoli_finanziari': calcoli,
            'predizione_ai': predizione_ai,
            'id_database': id_inserito
        }
    
    def _predici_con_ai(self, dati_completi):
        """Previsione usando il modello AI"""
        # Converti in DataFrame
        df = pd.DataFrame([dati_completi])
        
        # Applica encoding come nel training
        for feature, encoder in self.label_encoders.items():
            if feature != 'target' and feature in df.columns:
                if df[feature].iloc[0] in encoder.classes_:
                    df[feature] = encoder.transform([df[feature].iloc[0]])[0]
                else:
                    df[feature] = 0  # Default
        
        # Seleziona features usate nel training
        feature_columns = self.label_encoders.get('feature_columns', [])
        if not feature_columns and hasattr(self, 'feature_importance'):
            feature_columns = self.feature_importance['feature'].tolist()
        
        available_columns = [col for col in feature_columns if col in df.columns]
        df_processed = df[available_columns]
        
        # Scaling e predizione
        df_scaled = self.scaler.transform(df_processed)
        prediction_encoded = self.model.predict(df_scaled)[0]
        prediction_proba = self.model.predict_proba(df_scaled)[0]
        
        # Decodifica
        prediction = self.label_encoders['target'].inverse_transform([prediction_encoded])[0]
        
        return {
            'decisione_prevista': prediction,
            'probabilita': max(prediction_proba),
            'tutte_probabilita': dict(zip(self.label_encoders['target'].classes_, prediction_proba))
        }
    
    def aggiorna_tutto_il_database(self):
        """
        Aggiorna tutti i record nel database (utility function)
        """
        print("\n🔄 AGGIORNAMENTO DI TUTTO IL DATABASE...")
        self.db_updater.aggiorna_tutti_i_record()

def main():
    """Test con un nuovo cliente di esempio"""
    tester = ClienteTester()
    
    # Prova a caricare il modello AI
    modello_caricato = tester.load_model('../../file/model.pkl')
    if not modello_caricato:
        print("ℹ️  Continuo senza modello AI (userò i calcoli diretti)")
    
    # DATI DEL NUOVO CLIENTE (puoi modificare questi valori)
    nuovo_cliente = {
        'eta': 35,
        'reddito_mensile': 2800,
        'altre_spese': 1200,
        'costo_auto': 25000,
        'tipologia_auto': 'suv',
        'nuovo_usato': 'Nuovo',  # 'Nuova' o 'Usata'
        'neo_patentato': 'No',
        'nr_figli': 2,
        'sesso': 'uomo',
        'zona': 'nord ovest',
        'nr_rate': 48,
        'tan': 5.0,
        'anticipo_perc': 30.0  # Solo per auto nuove tra il 25 e il 40%
    }
    
    print("🚗 TEST NUOVO CLIENTE")
    print("=" * 50)
    print("📋 DATI INSERITI:")
    for key, value in nuovo_cliente.items():
        print(f"   {key}: {value}")
    
    # Esegui test completo
    risultati = tester.testa_nuovo_cliente(nuovo_cliente)
    
    if risultati and risultati['id_database']:
        print("\n🎯 RISULTATO FINALE:")
        print(f"   Decisione: {risultati['predizione_ai']['decisione_prevista']}")
        print(f"   Probabilità: {risultati['predizione_ai']['probabilita']:.1%}")
        print(f"   ID Database: {risultati['id_database']}")
        
        # Opzione per aggiornare tutto il database
        aggiorna_tutto = input("\n🔄 Vuoi aggiornare tutti i record nel database? (s/n): ")
        if aggiorna_tutto.lower() == 's':
            tester.aggiorna_tutto_il_database()
    else:
        print("❌ Test fallito")

if __name__ == "__main__":
    main()
