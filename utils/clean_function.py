import os
import pandas as pd
import numpy as np

def limpiar_criptomonedas(ruta_origen: str) -> pd.DataFrame:
    """
    Carga y limpia el dataset de criptomonedas tradicionales (Bitget).
    """
    if not os.path.exists(ruta_origen):
        raise FileNotFoundError(f"❌ No se encontró el archivo de criptomonedas en: {ruta_origen}")
        
    print("⏳ Iniciando limpieza de criptomonedas tradicionales...")
    df = pd.read_csv(ruta_origen)
    
    # 1. CAMBIO AQUÍ: Convertimos a datetime y mantenemos el nombre 'datetime'
    df['datetime'] = pd.to_datetime(df['fecha'])
    # Si venía una columna vieja llamada 'fecha', la eliminamos para no duplicar
    if 'fecha' in df.columns and 'datetime' != 'fecha':
        df = df.drop(columns=['fecha'])
    
    # 2. Control de tipos de datos numéricos
    cols_numericas = ['open', 'high', 'low', 'close', 'volume']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # 3. Tratamiento de nulos y duplicados utilizando 'datetime'
    df = df.dropna(subset=['datetime', 'crypto_id', 'close'])
    df = df.drop_duplicates(subset=['datetime', 'crypto_id'], keep='last')
    
    # 4. Ordenación lógica temporal por activo
    df = df.sort_values(by=['crypto_id', 'datetime']).reset_index(drop=True)
    
    print(f"✅ Criptomonedas procesadas con éxito. Dimensión final: {df.shape}")
    return df


def limpiar_stablecoins(ruta_origen: str) -> pd.DataFrame:
    """
    Carga y limpia el dataset de stablecoins (DefiLlama).
    """
    if not os.path.exists(ruta_origen):
        raise FileNotFoundError(f"❌ No se encontró el archivo de stablecoins en: {ruta_origen}")
        
    print("⏳ Iniciando limpieza de stablecoins...")
    df = pd.read_csv(ruta_origen)
    
    # 1. CAMBIO AQUÍ: Aseguramos que se llame 'datetime' y que esté en formato correcto
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # 2. Control de tipos numéricos
    cols_numericas = ['price', 'market_cap', 'peg_deviation', 'supply_change_1d', 
                      'supply_change_7d', 'price_volatility_3d']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # 3. Tratamiento de registros corruptos o vacíos
    df = df.dropna(subset=['datetime', 'stablecoin', 'price'])
    df = df.drop_duplicates(subset=['datetime', 'stablecoin'], keep='last')
    
    # 4. Ordenación lógica temporal por activo
    df = df.sort_values(by=['stablecoin', 'datetime']).reset_index(drop=True)
    
    print(f"✅ Stablecoins procesadas con éxito. Dimensión final: {df.shape}")
    return df


def ejecutar_pipeline_limpieza(ruta_cryptos_in: str, ruta_stables_in: str, carpeta_destino: str = "data/clean"):
    """
    Función orquestadora que engloba los dos procesos de limpieza.
    """
    print("\n" + "="*60)
    print("🚀 INICIANDO PIPELINE CENTRAL DE LIMPIEZA Y DEPURACIÓN DE DATOS")
    print("="*60)
    
    # Crear la subcarpeta clean de forma segura si no existe
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
    print("🎉 ¡PIPELINE FINALIZADO CON ÉXITO! Tus datos están listos en la zona 'clean'.")
    print("="*60)