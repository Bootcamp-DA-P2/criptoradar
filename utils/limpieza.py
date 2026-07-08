import os
import pandas as pd
import numpy as np

def limpiar_criptomonedas(ruta_origen: str) -> pd.DataFrame:
    """
    Carga y limpia el dataset de criptomonedas tradicionales (Bitget).
    Realiza conversiones de formato, control de nulos, tipos de datos y ordenación.
    """
    if not os.path.exists(ruta_origen):
        raise FileNotFoundError(f"❌ No se encontró el archivo de criptomonedas en: {ruta_origen}")
        
    print("⏳ Iniciando limpieza de criptomonedas tradicionales...")
    df = pd.read_csv(ruta_origen)
    df_inicial = df.copy()
    
    # 1. Asegurar formato datetime y extraer solo la fecha limpia
    df['fecha'] = pd.to_datetime(df['fecha']).dt.date
    
    # 2. Control de tipos de datos numéricos (asegurar floats)
    cols_numericas = ['open', 'high', 'low', 'close', 'volume']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # 3. Tratamiento de nulos y duplicados (si existieran)
    df = df.dropna(subset=['fecha', 'crypto_id', 'close'])
    df = df.drop_duplicates(subset=['fecha', 'crypto_id'], keep='last')
    
    # 4. Ordenación lógica temporal por activo
    df = df.sort_values(by=['crypto_id', 'fecha']).reset_index(drop=True)
    
    print(f"✅ Criptomonedas procesadas con éxito. Dimensión final: {df.shape}")
    return df


def limpiar_stablecoins(ruta_origen: str) -> pd.DataFrame:
    """
    Carga y limpia el dataset de stablecoins (DefiLlama).
    Normaliza nombres de columnas clave, gestiona tipos de datos y limpia duplicados.
    """
    if not os.path.exists(ruta_origen):
        raise FileNotFoundError(f"❌ No se encontró el archivo de stablecoins en: {ruta_origen}")
        
    print("⏳ Iniciando limpieza de stablecoins...")
    df = pd.read_csv(ruta_origen)
    df_inicial = df.copy()
    
    # 1. Homologar la columna temporal a 'fecha' para permitir cruces posteriores
    if 'datetime' in df.columns:
        df = df.rename(columns={'datetime': 'fecha'})
        
    df['fecha'] = pd.to_datetime(df['fecha']).dt.date
    
    # 2. Control de tipos numéricos en métricas específicas de stablecoins
    cols_numericas = ['price', 'market_cap', 'peg_deviation', 'supply_change_1d', 
                      'supply_change_7d', 'price_volatility_3d']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # 3. Tratamiento de registros corruptos o vacíos
    df = df.dropna(subset=['fecha', 'stablecoin', 'price'])
    df = df.drop_duplicates(subset=['fecha', 'stablecoin'], keep='last')
    
    # 4. Ordenación lógica temporal por activo
    df = df.sort_values(by=['stablecoin', 'fecha']).reset_index(drop=True)
    
    print(f"✅ Stablecoins procesadas con éxito. Dimensión final: {df.shape}")
    return df


def ejecutar_pipeline_limpieza(ruta_cryptos_in: str, ruta_stables_in: str, carpeta_destino: str = "data"):
    """
    Función orquestadora que engloba los dos procesos de limpieza.
    Carga los archivos raw, ejecuta las limpiezas modulares y guarda los resultados limpios 
    listos para ser consumidos por el modelo analítico de alertas.
    """
    print("\n" + "="*60)
    print("🚀 INICIANDO PIPELINE CENTRAL DE LIMPIEZA Y DEPURACIÓN DE DATOS")
    print("="*60)
    
    # Crear la carpeta destino si no existe
    os.makedirs(carpeta_destino, exist_ok=True)
    
    # Ejecutar la limpieza de criptos
    df_cryptos_clean = limpiar_criptomonedas(ruta_cryptos_in)
    ruta_cryptos_out = os.path.join(carpeta_destino, "criptoradar_crypto_final_clean.csv")
    df_cryptos_clean.to_csv(ruta_cryptos_out, index=False)
    print(f"💾 Guardado dataset limpio de criptos en: {ruta_cryptos_out}\n")
    
    # Ejecutar la limpieza de stablecoins
    df_stables_clean = limpiar_stablecoins(ruta_stables_in)
    ruta_stables_out = os.path.join(carpeta_destino, "datos_preprocesados_clean.csv")
    df_stables_clean.to_csv(ruta_stables_out, index=False)
    print(f"💾 Guardado dataset limpio de stablecoins en: {ruta_stables_out}\n")
    
    print("="*60)
    print("🎉 ¡PIPELINE FINALIZADO CON ÉXITO! Tus datos están listos para el análisis.")
    print("="*60)