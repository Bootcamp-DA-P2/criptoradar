import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

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
FICHERO_SQL = os.getenv("FICHERO_SQL")

# Validar que no falte ningún parámetro clave en el entorno
if not all([DB_USER, DB_PASS, DB_HOST, DB_NAME, CARPETA_DATOS, FICHERO_SQL]):
    print("❌ Error: Faltan variables de entorno esenciales en tu archivo .env")
    sys.exit(1)


def crear_base_de_datos_si_not_exists():
    """Conecta al servidor MySQL base y comprueba si la base de datos ya existe.
    - Si existe: Se salta todo y NO exige el archivo SQL.
    - Si no existe: Busca el archivo SQL en la ruta configurada para levantarla desde cero.
    """
    try:
        # Nos conectamos al host sin indicar Base de Datos inicial
        engine_servidor = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/")
        
        # 1. Comprobar si la base de datos ya existe en el servidor MySQL
        with engine_servidor.connect() as conexion:
            resultado = conexion.execute(text("SHOW DATABASES;"))
            bases_de_datos = [fila[0] for fila in resultado]
        
        if DB_NAME in bases_de_datos:
            print(f"ℹ️  La base de datos '{DB_NAME}' ya existe en el servidor.")
            print(f"   👉 Se omite la validación y ejecución del fichero SQL ({FICHERO_SQL}).")
            return  # <--- SALIDA EXITOSA INMEDIATA (No comprueba ni exige el archivo local)
            
    except Exception as e:
        print(f"❌ Error al comprobar la existencia de la base de datos en el servidor: {e}")
        sys.exit(1)

    # 2. Si NO existe en el servidor, entonces SÍ es estrictamente necesario el archivo SQL
    ruta_sql = os.path.join(CARPETA_DATOS, FICHERO_SQL)
    
    if not os.path.exists(ruta_sql):
        print(f"❌ Error crítico: La base de datos '{DB_NAME}' no existe en el servidor ")
        print(f"   y tampoco se encuentra el archivo SQL de inicialización en la ruta: {ruta_sql}")
        sys.exit(1)
        
    print(f"🛠️  La base de datos no existe en el servidor. Inicializando esquema desde: {ruta_sql}")
    try:
        with open(ruta_sql, "r", encoding="utf-8") as f:
            # Separamos los comandos por punto y coma descartando bloques vacíos
            sentencias_sql = [s.strip() for s in f.read().split(";") if s.strip()]
            
        with engine_servidor.connect() as conexion:
            for sentencia in sentencias_sql:
                # Omitimos líneas de comentarios puros
                if not sentencia.startswith("--"):
                    conexion.execute(text(sentencia))
                    
        print("✅ Base de datos creada y tablas inicializadas con éxito.")
    except Exception as e:
        print(f"❌ Error crítico al crear la estructura de la base de datos: {e}")
        sys.exit(1)


def conectar_db():
    try:
        connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        print(f"❌ Error al conectar con MySQL: {e}")
        sys.exit(1)


def filtrar_duplicados(df, tabla, columnas_clave, engine):
    """Filtra el DataFrame para conservar solo las filas que no existen en la BD."""
    try:
        # Consultar solo las columnas clave de la base de datos para no saturar la memoria
        columnas_str = ", ".join(columnas_clave)
        query = f"SELECT {columnas_str} FROM {tabla}"
        df_existente = pd.read_sql(query, con=engine)
        
        if df_existente.empty:
            return df

        # Asegurar tipos de datos consistentes para el cruce (sobre todo con strings/IDs)
        for col in columnas_clave:
            df[col] = df[col].astype(df_existente[col].dtype)

        # Hacemos un merge left con indicador para quedarnos solo con lo que está 'left_only'
        enlace = df.merge(df_existente, on=columnas_clave, how='left', indicator=True)
        df_filtrado = enlace[enlace['_merge'] == 'left_only'].drop(columns=['_merge'])
        
        return df_filtrado
    except Exception:
        # Si la tabla está vacía o da error porque no existe, devolvemos todo el DF
        return df


def cargar_datos_desde_env():
    archivos = {
        "preprocesados": os.path.join(CARPETA_DATOS, "datos_preprocesados_clean.csv"),
        "sistema": os.path.join(CARPETA_DATOS, "alertas_sistema_final.csv"),
        "criticas": os.path.join(CARPETA_DATOS, "alertas_criticas_informe.csv"),
        "crypto": os.path.join(CARPETA_DATOS, "criptoradar_crypto_final_clean.csv")
    }
    
    for nombre, ruta in archivos.items():
        if not os.path.exists(ruta):
            print(f"❌ Error: No se encuentra el archivo de {nombre} en: {ruta}")
            sys.exit(1)

    engine = conectar_db()
    print(f"🔌 Conexión exitosa a MySQL en [{DB_HOST}]. Procesando archivos...\n")

    # ==========================================
    # PASO 1: TABLAS MAESTRAS (DIMENSIONES)
    # ==========================================
    print("📦 [1/2] Extrayendo y cargando tablas maestras...")
    
    # Dim_Stablecoins
    df_prep = pd.read_csv(archivos["preprocesados"])
    dim_stablecoins = df_prep[['stablecoin_id', 'stablecoin']].drop_duplicates()
    dim_stablecoins.columns = ['stablecoin_id', 'nombre_stablecoin']
    
    dim_stablecoins = filtrar_duplicados(dim_stablecoins, 'stablecoins', ['stablecoin_id'], engine)
    if not dim_stablecoins.empty:
        dim_stablecoins.to_sql('stablecoins', con=engine, if_exists='append', index=False)
        print(f"   ✅ Stablecoins: Se insertaron {len(dim_stablecoins)} nuevos registros.")
    else:
        print("   ℹ️ Stablecoins: Sin nuevos datos que añadir.")

    # Dim_Cryptos
    df_crypto = pd.read_csv(archivos["crypto"])
    dim_cryptos = pd.DataFrame(df_crypto['crypto_id'].unique(), columns=['crypto_id'])
    
    dim_cryptos = filtrar_duplicados(dim_cryptos, 'cryptos', ['crypto_id'], engine)
    if not dim_cryptos.empty:
        dim_cryptos.to_sql('cryptos', con=engine, if_exists='append', index=False)
        print(f"   ✅ Cryptos: Se insertaron {len(dim_cryptos)} nuevos registros.\n")
    else:
        print("   ℹ️ Cryptos: Sin nuevos datos que añadir.\n")

    # ==========================================
    # PASO 2: TABLAS DE HECHOS (MÉTRICAS COHERENTES)
    # ==========================================
    print("📊 [2/2] Procesando e insertando tablas de hechos...")

    # Fact_Preprocesados_Historico
    cols_prep = ['datetime', 'stablecoin_id', 'price', 'market_cap', 'peg_deviation', 
                'supply_change_1d', 'supply_change_7d', 'price_volatility_3d']
    df_prep_hechos = df_prep[cols_prep].drop_duplicates(subset=['datetime', 'stablecoin_id'])
    df_prep_hechos = filtrar_duplicados(df_prep_hechos, 'preprocesados_historico', ['datetime', 'stablecoin_id'], engine)
    
    if not df_prep_hechos.empty:
        df_prep_hechos.to_sql('preprocesados_historico', con=engine, if_exists='append', index=False)
        print(f"   🔹 Preprocesados_Historico: {len(df_prep_hechos)} filas nuevas añadidas.")
    else:
        print("   ℹ️ Preprocesados_Historico: Al día. No hay datos nuevos.")

    # Fact_Alertas_Sistema
    df_sys = pd.read_csv(archivos["sistema"])
    cols_sys = ['datetime', 'stablecoin_id', 'anomaly_score', 'is_anomaly_stablecoin', 
                'market_volatility', 'market_stress', 'nivel_alerta']
    df_sys_hechos = df_sys[cols_sys].drop_duplicates(subset=['datetime', 'stablecoin_id'])
    df_sys_hechos = filtrar_duplicados(df_sys_hechos, 'alertas_sistema', ['datetime', 'stablecoin_id'], engine)
    
    if not df_sys_hechos.empty:
        df_sys_hechos.to_sql('alertas_sistema', con=engine, if_exists='append', index=False)
        print(f"   🔹 Alertas_Sistema: {len(df_sys_hechos)} filas nuevas añadidas.")
    else:
        print("   ℹ️ Alertas_Sistema: Al día. No hay datos nuevos.")

    # Fact_Alertas_Criticas
    df_crit = pd.read_csv(archivos["criticas"])
    cols_crit = ['datetime', 'stablecoin_id', 'nivel_alerta', 'btc_return', 
                'eth_return', 'xrp_return', 'sol_return', 'narrativa_alerta']
    df_crit_hechos = df_crit[cols_crit].drop_duplicates(subset=['datetime', 'stablecoin_id'])
    df_crit_hechos = filtrar_duplicados(df_crit_hechos, 'alertas_criticas', ['datetime', 'stablecoin_id'], engine)
    
    if not df_crit_hechos.empty:
        df_crit_hechos.to_sql('alertas_criticas', con=engine, if_exists='append', index=False)
        print(f"   🔹 Alertas_Criticas: {len(df_crit_hechos)} filas nuevas añadidas.")
    else:
        print("   ℹ️ Alertas_Criticas: Al día. No hay datos nuevos.")

    # Fact_Crypto_Precios
    cols_crypto = ['datetime', 'crypto_id', 'open', 'high', 'low', 'close', 'volume']
    df_crypto_hechos = df_crypto[cols_crypto].drop_duplicates(subset=['datetime', 'crypto_id'])
    df_crypto_hechos = filtrar_duplicados(df_crypto_hechos, 'crypto_precios', ['datetime', 'crypto_id'], engine)

    if not df_crypto_hechos.empty:
        df_crypto_hechos.to_sql('crypto_precios', con=engine, if_exists='append', index=False)
        print(f"   🔹 Crypto_Precios: {len(df_crypto_hechos)} filas nuevas añadidas.")
    else:
        print("   ℹ️ Crypto_Precios: Al día. No hay datos nuevos.")

    print(f"\n🚀 Pipeline completado de forma incremental. Todos los datos nuevos están en MySQL.")


if __name__ == '__main__':
    # 1. Ejecutar inicialización de estructura SQL buscando el archivo en la carpeta de datos
    crear_base_de_datos_si_not_exists()
    
    # 2. Cargar los datos de los CSV de forma incremental
    cargar_datos_desde_env()