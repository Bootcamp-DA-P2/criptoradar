import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def entrenar_detector_anomalias():
    print("=== INICIANDO ENTRENAMIENTO CORREGIDO: CRIPTORADAR DETECTOR ===\n")
    
    try:
        df = pd.read_csv('dataset_maestro_criptoradar.csv')
        print(f"📊 Dataset cargado correctamente. Total de registros originales: {len(df)} filas.")
    except FileNotFoundError:
        print("❌ Error: No se encontró 'dataset_maestro_criptoradar.csv'.")
        return

    # 🛠️ FILTRO HIGIÉNICO (Sanity Check): Eliminamos anomalías corruptas de la API (precios imposibles > 2 USD o < 0.5 USD)
    filtro_corrupcion = (df['price'] > 2.0) | (df['price'] < 0.5)
    total_corruptos = filtro_corrupcion.sum()
    
    if total_corruptos > 0:
        print(f"🧹 Eliminando {total_corruptos} registros corruptos detectados en los datos de origen (ej. falsos precios de miles de dólares)...")
        df = df[~filtro_corrupcion].reset_index(drop=True)
        print(f"📉 Dataset limpio para el modelo: {len(df)} filas.")

    # Ingeniería de variables
    df['price_deviation'] = (df['price'] - 1.0).abs()
    df['log_volume'] = np.log1p(df['total_volume_usd'])

    # Selección de variables numéricas clave para el Isolation Forest
    features = ['price_deviation', 'log_volume', 'circulating_supply_usd']
    X = df[features]
    
    print(f"⚙️ Entrenando Isolation Forest usando las variables: {features}")
    
    # Entrenar el modelo con contaminación ajustada al 1%
    model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
    df['anomaly_score'] = model.fit_predict(X)
    
    df['is_anomaly'] = df['anomaly_score'].apply(lambda x: 1 if x == -1 else 0)
    
    total_anomalias = df['is_anomaly'].sum()
    print(f"🚨 ¡Entrenamiento completado! Se han detectado {total_anomalias} anomalías reales y lógicas.")
    
    if total_anomalias > 0:
        print("\n🔍 Nueva muestra de alertas detectadas (Eventos reales de depeg o volumen extremo):")
        alertas = df[df['is_anomaly'] == 1].sort_values(by='price_deviation', ascending=False)
        print(alertas[['date', 'stablecoin_name', 'price', 'total_volume_usd', 'price_deviation']].head(10))
    
    df.to_csv('dataset_anomalias_detectadas.csv', index=False)
    print("\n💾 Resultados limpios guardados en 'dataset_anomalias_detectadas.csv'.")

if __name__ == "__main__":
    entrenar_detector_anomalias()