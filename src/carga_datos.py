import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import pymysql

# Cargar variables del entorno desde el .venv
load_dotenv()

# ==========================================
# CONFIGURACIÓN EXTRAÍDA DEL ENTORNO (.env)
# ==========================================
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
CARPETA_DATOS = os.getenv("CARPETA_DATOS")

# Validar que no falte ningún parámetro clave en el entorno
if not all([DB_USER, DB_PASS, DB_HOST, DB_NAME, CARPETA_DATOS]):
    print("❌ Error: Faltan variables de entorno esenciales en tu archivo .env")
    sys.exit(1)

def conectar_db():
    try:
        connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        print(f"❌ Error al conectar con MySQL: {e}")
        sys.exit(1)

def cargar_datos_desde_env():
    # Mapeo y construcción de rutas relativas usando la variable de entorno
    archivos = {
        "preprocesados": os.path.join(CARPETA_DATOS, "datos_preprocesados_clean.csv"),
        "sistema": os.path.join(CARPETA_DATOS, "alertas_sistema_final.csv"),
        "criticas": os.path.join(CARPETA_DATOS, "alertas_criticas_informe.csv"),
        "crypto": os.path.join(CARPETA_DATOS, "criptoradar_crypto_final_clean.csv")
    }
    
    # Comprobar que los archivos existan en el directorio configurado antes de operar
    for nombre, ruta in archivos.items():
        if not os.path.exists(ruta):
            print(f"❌ Error: No se encuentra el archivo de {nombre} en: {ruta}")
            sys.exit(1)

    engine = conectar_db()
    print(f"🔌 Conexión exitosa a MySQL en [{DB_HOST}]. Procesando archivos de '{CARPETA_DATOS}'...\n")

    # ==========================================
    # PASO 1: TABLAS MAESTRAS (DIMENSIONES)
    # ==========================================
    print("📦 [1/2] Extrayendo y cargando tablas maestras...")
    
    # Stablecoins
    df_prep = pd.read_csv(archivos["preprocesados"])
    dim_stablecoins = df_prep[['stablecoin_id', 'stablecoin']].drop_duplicates()
    dim_stablecoins.columns = ['stablecoin_id', 'nombre_stablecoin']
    dim_stablecoins.to_sql('Stablecoins', con=engine, if_exists='append', index=False)
    print("   ✅ Stablecoins sincronizada de forma correcta.")

    # Cryptos
    df_crypto = pd.read_csv(archivos["crypto"])
    dim_cryptos = pd.DataFrame(df_crypto['crypto_id'].unique(), columns=['crypto_id'])
    dim_cryptos.to_sql('Cryptos', con=engine, if_exists='append', index=False)
    print("   ✅ Cryptos sincronizada de forma correcta.\n")

    # ==========================================
    # PASO 2: TABLAS DE HECHOS (MÉTRICAS COHERENTES)
    # ==========================================
    print("📊 [2/2] Procesando e insertando tablas de hechos...")

    # Preprocesados_Historico
    cols_prep = ['datetime', 'stablecoin_id', 'price', 'market_cap', 'peg_deviation', 
                'supply_change_1d', 'supply_change_7d', 'price_volatility_3d']
    df_prep[cols_prep].to_sql('Preprocesados_Historico', con=engine, if_exists='append', index=False)
    print("   🔹 Preprocesados_Historico volcada.")

    # Alertas_Sistema
    df_sys = pd.read_csv(archivos["sistema"])
    cols_sys = ['datetime', 'stablecoin_id', 'anomaly_score', 'is_anomaly_stablecoin', 
                'market_volatility', 'market_stress', 'nivel_alerta']
    df_sys[cols_sys].to_sql('Alertas_Sistema', con=engine, if_exists='append', index=False)
    print("   🔹 Alertas_Sistema volcada.")

    # Fact_Alertas_Criticas
    df_crit = pd.read_csv(archivos["criticas"])
    cols_crit = ['datetime', 'stablecoin_id', 'nivel_alerta', 'btc_return', 
                'eth_return', 'xrp_return', 'sol_return', 'narrativa_alerta']
    df_crit[cols_crit].to_sql('Alertas_Criticas', con=engine, if_exists='append', index=False)
    print("   🔹 Alertas_Criticas volcada.")

    # Crypto_Precios
    cols_crypto = ['datetime', 'crypto_id', 'open', 'high', 'low', 'close', 'volume']
    df_crypto[cols_crypto].to_sql('Crypto_Precios', con=engine, if_exists='append', index=False)
    print("   🔹 Crypto_Precios volcada.")

    print(f"\n🚀 Pipeline completado. Todos los datos de '{CARPETA_DATOS}' están en MySQL.")

if __name__ == '__main__':
    cargar_datos_desde_env()