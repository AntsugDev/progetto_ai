 output_dir = '../../../data_result_predict/'
        os.makedirs(output_dir, exist_ok=True) 
        
        filename = f"predizione_fin.json"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w+', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Previsione terminata e salvata in: {filepath}")
        except Exception as e:
            print(f"Errore nel salvataggio del file: {e}")  