import pandas as pd
import numpy as np

def rewrite_df(df):
    # Convert columns to numeric
    df['diff_reddito'] = pd.to_numeric(df.get('diff_reddito', df.get('reddito_mensie', np.nan)), errors='coerce')
    df['costo_auto'] = pd.to_numeric(df.get('costo_auto', np.nan), errors='coerce')
    df['anticipo'] = pd.to_numeric(df.get('anticipo', 0.0), errors='coerce')
    df['tan'] = pd.to_numeric(df.get('tan', 0.0), errors='coerce')
    df['nr_rate'] = pd.to_numeric(df.get('nr_rate', 0), errors='coerce')
    df['nr_figli'] = pd.to_numeric(df.get('nr_figli', 0), errors='coerce')
    df['eta'] = pd.to_numeric(df.get('eta', np.nan), errors='coerce')
    df['eta_veicolo'] = pd.to_numeric(df.get('eta_veicolo', 0), errors='coerce')
    
    # Calculate importo_finanziato if missing
    if 'importo_finanziato' not in df.columns or df['importo_finanziato'].isnull().all():
        df['importo_finanziato'] = df.apply(
            lambda r: r['costo_auto'] * 0.10 if int(r.get('nuovo_usato_id', 1)) == 1 and False else r['costo_auto'],
            axis=1
        )
        df['importo_finanziato'] = df['importo_finanziato'].replace({0: np.nan})
        df['importo_finanziato'] = df['importo_finanziato'].fillna(df['costo_auto'])
    
    # Calculate rata if missing
    if 'rata' not in df.columns or df['rata'].isnull().all():
        # compute annuity monthly: use TAN stored as decimal (e.g. 0.05) or percent (5). Normalize later
        def compute_r(row):
            P = row['importo_finanziato'] if pd.notna(row['importo_finanziato']) else row['costo_auto']
            n = int(row['nr_rate']) if pd.notna(row['nr_rate']) and row['nr_rate'] > 0 else 0
            tan = float(row['tan']) if pd.notna(row['tan']) else 0.0
            
            if tan > 1:
                tan = tan / 100.0
            r = tan / 12.0
            
            if r == 0:
                return P / n if n > 0 else 0.0
                
            denom = 1 - (1 + r) ** (-n)
            if denom == 0:
                return 0.0
            return P * (r / denom)
        
        df['rata'] = df.apply(compute_r, axis=1)
    
    # Calculate sostenibilita if missing
    if 'sostenibilita' not in df.columns or df['sostenibilita'].isnull().all():
        df['sostenibilita'] = df.apply(
            lambda r: r['rata'] / r['diff_reddito'] if r['diff_reddito'] and r['diff_reddito'] > 0 else np.nan, 
            axis=1
        )
    
    # Calculate coefficiente_k if missing
    if 'coefficiente_k' not in df.columns or df['coefficiente_k'].isnull().all():
        df['coefficiente_k'] = df['sostenibilita'].apply(
            lambda s: s / 0.20 if pd.notna(s) else np.nan
        )
    
    # Handle decision columns
    df['decisione_AI'] = df.get('decisione_AI', df.get('Decisione_finale', np.nan))
    df['rt'] = pd.to_numeric(df.get('rt', df.get('RT', np.nan)), errors='coerce')
    
    # Categorical columns (IDs)
    cat_cols = [
        'nuovo_usato_id', 'tipologia_auto_id', 'sesso_id', 'zona_id', 
        'neo_patentato_id', 'formula_acquisto_id'
    ]
    for c in cat_cols:
        if c not in df.columns:
            df[c] = np.nan
    
    # Select final feature list
    features = [
        'diff_reddito', 'costo_auto', 'anticipo', 'tan', 'nr_rate', 'nr_figli', 
        'eta', 'eta_veicolo', 'importo_finanziato', 'rata', 'sostenibilita', 
        'coefficiente_k', 'nuovo_usato_id', 'tipologia_auto_id', 'sesso_id', 
        'zona_id', 'neo_patentato_id', 'formula_acquisto_id'
    ]
    
    # Keep target columns
    keep = features + ['decisione_AI', 'rt']
    df2 = df[keep].copy()
    
    # Drop rows with missing target
    df2 = df2[df2['decisione_AI'].notna() & df2['rt'].notna()]
    
    # Reset index
    df2 = df2.reset_index(drop=True)
    
    return df2
