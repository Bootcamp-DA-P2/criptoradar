import pandas as pd
import numpy as np
import sqlite3
import os
import joblib  # Librería para exportar archivos binarios .pkl
from sklearn.ensemble import IsolationForest

def entrenar_detector_anomalias():
    print("==================================================")
    db_path = "data/criptoradar.db"
    
    # Rutas para guardar los archivos PKL para tu interfaz de Streamlit
    models_dir = "models"
    model_pkl_path = os.path.join(models_dir, "isolation_forest_model.pkl")
    alertas_pkl_path = os.path.join(models_dir, "dataset_alertas.pkl")
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"No se encontró la base de datos en '{db_path}'. Ejecuta primero el pipeline de ingesta.")
    
    # Crear la carpeta 'models' si no existe
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        print(f"[+] Directorio '{models_dir}' creado para los archivos PKL.")
    
    # 1. Leer datos desde SQLite
    print(f"[1/4] Conectando a SQLite ('{db_path}') y extrayendo histórico...")
    conexion = sqlite3.connect(db_path)
    
    query = "SELECT * FROM historico_stablecoins"
    df = pd.read_sql_query(query, conexion, parse_dates=['datetime'])
    df.set_index('datetime', inplace=True)
    
    # 2. Seleccionar características puras del activo
    features = ['price', 'peg_deviation', 'supply_change_1d', 'price_volatility_3d']
    X = df[features]
    
    # 3. Configurar y entrenar Isolation Forest
    print(f"[2/4] Entrenando Isolation Forest sobre {X.shape[0]} registros...")
    model = IsolationForest(n_estimators=100, contamination=0.015, random_state=42)
    
    df['anomaly_score'] = model.fit_predict(X)
    df['anomaly_score_clean'] = model.decision_function(X)
    
    anomalias = df[df['anomaly_score'] == -1]
    normales = df[df['anomaly_score'] == 1]
    
    print("\n--- ¡PROCESO DE MACHINE LEARNING COMPLETADO! ---")
    print(f"✅ Registros estables / normales: {normales.shape[0]}")
    print(f"🚨 Alertas de anomalías/depegs detectadas: {anomalias.shape[0]}")
    
    # =========================================================================
    # NUEVO: EXPORTACIÓN DE LOS DOS ARCHIVOS PKL PARA STREAMLIT
    # =========================================================================
    print(f"\n[3/4] Exportando archivos .pkl para la aplicación de Streamlit...")
    
    # 1. Guardamos el modelo para evaluar nuevos registros en la App
    joblib.dump(model, model_pkl_path)
    print(f"      -> [OK] Modelo serializado en: {model_pkl_path}")
    
    # 2. Guardamos el DataFrame completo etiquetado (para tus gráficos de Streamlit)
    df_reset = df.reset_index()
    joblib.dump(df_reset, alertas_pkl_path)
    print(f"      -> [OK] Historial de alertas serializado en: {alertas_pkl_path}")
    # =========================================================================
    
    if not anomalias.empty:
        print("\nMuestra de las alertas más críticas detectadas por el radar:")
        columnas_muestra = ['stablecoin', 'price', 'market_cap', 'peg_deviation']
        print(anomalias[columnas_muestra].sort_values(by='peg_deviation', ascending=False).head(5))
    
    # 4. Persistir resultados en Base de Datos
    print(f"\n[4/4] Guardando los datos etiquetados en la base de datos...")
    df_reset.to_sql(
        name='alertas_criptoradar', 
        con=conexion, 
        if_exists='replace', 
        index=False
    )
    
    conexion.close()
    print("[SQLITE] ¡Éxito! Nueva tabla 'alertas_criptoradar' creada con el etiquetado de anomalías.")
    print("==================================================")

if __name__ == "__main__":
    try:
        entrenar_detector_anomalias()
    except Exception as e:
        print(f"[ERROR] No se pudo completar el modelado: {e}")