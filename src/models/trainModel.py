import os
import sys
import yfinance as yf
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# =====================================================================
# 1. CONFIGURACIÓN DE PARÁMETROS
# =====================================================================
fecha_inicio = "2021-01-01"
fecha_fin = "2026-07-15"

# Nombre de la stablecoin en tu tabla 'stablecoins' (ver mapeo en app.py)
NOMBRE_STABLE = os.getenv("MODELO_MACRO_STABLE", "USDT")
CRYPTO_ID_BTC = "bitcoin"  # tal y como está guardado en tu tabla 'cryptos'

# Tickers de Yahoo Finance que SÍ seguimos necesitando:
# - 'stable': solo para el VOLUMEN (tu BD no guarda volumen de trading, solo market_cap)
# - 'btc': solo para rellenar el histórico ANTERIOR al que ya tienes en tu BD
# - 'treasury', 'dxy', 'vix': variables macro que no existen en tu proyecto, siempre vía yfinance
tickers = {
    'stable': 'USDT-USD',
    'btc': 'BTC-USD',
    'treasury': '^IRX',
    'dxy': 'DX-Y.NYB',
    'vix': '^VIX'
}

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

required = {"DB_USER": DB_USER, "DB_PASS": DB_PASS, "DB_HOST": DB_HOST, "DB_NAME": DB_NAME}
missing = [k for k, v in required.items() if not v]
if missing:
    print("❌ Faltan variables de entorno para conectar a MySQL:")
    for var in missing:
        print(f"   - {var}")
    sys.exit(1)


def conectar_db():
    connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
    return create_engine(connection_string)


def _normalizar_indice(obj, nombre_fuente=""):
    """Normaliza el índice de fechas (sin hora) y elimina duplicados, avisando si los hubo."""
    obj = obj.copy()
    obj.index = pd.to_datetime(obj.index).normalize()
    n_dup = int(obj.index.duplicated().sum())
    if n_dup > 0:
        print(f"⚠️  {nombre_fuente}: se encontraron {n_dup} fechas duplicadas, se conserva el último valor de cada una.")
        obj = obj[~obj.index.duplicated(keep='last')]
    return obj.sort_index()


def obtener_stablecoin_id(engine, nombre_stable):
    """Busca el stablecoin_id correspondiente al nombre en la tabla maestra 'stablecoins'."""
    with engine.connect() as conexion:
        resultado = conexion.execute(
            text("SELECT stablecoin_id FROM stablecoins WHERE nombre_stablecoin = :nombre"),
            {"nombre": nombre_stable}
        ).fetchone()
    if resultado is None:
        print(f"❌ No se encontró '{nombre_stable}' en la tabla 'stablecoins'. "
              f"Ejecuta antes app.py para poblar la base de datos.")
        sys.exit(1)
    return resultado[0]


def filtrar_duplicados(df, tabla, columnas_clave, engine):
    """Filtra el DataFrame para conservar solo las filas que no existen ya en la tabla de la BD."""
    try:
        columnas_str = ", ".join(columnas_clave)
        df_existente = pd.read_sql(f"SELECT {columnas_str} FROM {tabla}", con=engine)
        if df_existente.empty:
            return df
        for col in columnas_clave:
            df[col] = df[col].astype(df_existente[col].dtype)
        enlace = df.merge(df_existente, on=columnas_clave, how='left', indicator=True)
        return enlace[enlace['_merge'] == 'left_only'].drop(columns=['_merge'])
    except Exception:
        # Si la tabla aún no existe, no hay nada que filtrar todavía
        return df


def guardar_modelo_macro_bd(engine, df_modelo, stablecoin_id):
    """Guarda el dataset del modelo econométrico en la tabla 'modelo_riesgo_macro'."""
    print("\n🗄️  Guardando el modelo de riesgo macro en MySQL (modelo_riesgo_macro)...")
    df_bd = df_modelo.rename(columns={'D_t': 'peg_deviation'}).copy()
    df_bd['datetime'] = pd.to_datetime(df_bd['fecha']).dt.date
    df_bd['stablecoin_id'] = stablecoin_id

    columnas_bd = [
        'datetime', 'stablecoin_id', 'peg_deviation', 'riesgo_mercado_btc',
        'riesgo_liquidez_ln_vol', 'tasas_eeuu', 'indice_dolar', 'volatilidad_vix'
    ]
    df_bd = df_bd[columnas_bd].drop_duplicates(subset=['datetime', 'stablecoin_id'])
    df_bd = filtrar_duplicados(df_bd, 'modelo_riesgo_macro', ['datetime', 'stablecoin_id'], engine)

    if not df_bd.empty:
        df_bd.to_sql('modelo_riesgo_macro', con=engine, if_exists='append', index=False)
        print(f"✅ modelo_riesgo_macro: {len(df_bd)} filas nuevas añadidas.")
    else:
        print("ℹ️  modelo_riesgo_macro: Al día. No hay datos nuevos.")


# =====================================================================
# 2A. PRECIO DE LA STABLECOIN — 100% DESDE TU BASE DE DATOS
# =====================================================================
def obtener_precio_stable_bd(engine):
    print(f"📥 Obteniendo precio histórico de '{NOMBRE_STABLE}' desde MySQL (preprocesados_historico)...")
    query = text("""
        SELECT ph.datetime, ph.price
        FROM preprocesados_historico ph
        JOIN stablecoins s ON s.stablecoin_id = ph.stablecoin_id
        WHERE s.nombre_stablecoin = :nombre
        ORDER BY ph.datetime
    """)
    df = pd.read_sql(query, con=engine, params={"nombre": NOMBRE_STABLE})
    if df.empty:
        print(f"❌ No hay datos de '{NOMBRE_STABLE}' en preprocesados_historico. "
              f"Ejecuta antes app.py para poblar la base de datos.")
        sys.exit(1)
    df['datetime'] = pd.to_datetime(df['datetime'])
    serie = df.set_index('datetime')['price'].rename('precio_stable')
    return _normalizar_indice(serie, "precio_stable (BD)")


# =====================================================================
# 2B. PRECIO DE BTC — HÍBRIDO (BD para lo reciente, yfinance para rellenar el histórico)
# =====================================================================
def obtener_btc_hibrido(engine):
    print("📥 Obteniendo histórico reciente de BTC desde MySQL (crypto_precios)...")
    query = text("""
        SELECT datetime, close
        FROM crypto_precios
        WHERE crypto_id = :crypto_id
        ORDER BY datetime
    """)
    df_bd = pd.read_sql(query, con=engine, params={"crypto_id": CRYPTO_ID_BTC})
    df_bd['datetime'] = pd.to_datetime(df_bd['datetime'])
    serie_bd = df_bd.set_index('datetime')['close']
    serie_bd = _normalizar_indice(serie_bd, "btc (BD)")

    if serie_bd.empty:
        print("⚠️  No hay datos de BTC en crypto_precios, se usará yfinance para todo el rango.")
        fecha_corte = pd.to_datetime(fecha_inicio)
    else:
        fecha_corte = serie_bd.index.min()
        print(f"   BD cubre BTC desde {fecha_corte.date()}. "
              f"Se rellenará {fecha_inicio} → {fecha_corte.date()} con yfinance.")

    # Rellenamos SOLO el tramo anterior al que ya tenemos en la BD
    fecha_fin_relleno = (fecha_corte - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    if pd.to_datetime(fecha_inicio) < fecha_corte:
        print(f"Descargando btc ({tickers['btc']}) de yfinance para el histórico antiguo...")
        df_yf = yf.download(tickers['btc'], start=fecha_inicio, end=fecha_fin_relleno, progress=False)
        serie_yf = df_yf['Close'].squeeze()
        serie_yf = _normalizar_indice(serie_yf, "btc (yfinance)")
    else:
        serie_yf = pd.Series(dtype=float)

    serie_completa = pd.concat([serie_yf, serie_bd])
    serie_completa = _normalizar_indice(serie_completa, "btc (combinado)")
    return serie_completa.rename('btc')


# =====================================================================
# 2C. VOLUMEN DE LA STABLECOIN Y VARIABLES MACRO — SIGUEN VINIENDO DE YFINANCE
# =====================================================================
def obtener_volumen_y_macro_yf():
    datos_extraidos = {}
    for nombre in ('stable', 'treasury', 'dxy', 'vix'):
        ticker = tickers[nombre]
        print(f"Descargando {nombre} ({ticker}) de yfinance...")
        df_temp = yf.download(ticker, start=fecha_inicio, end=fecha_fin, progress=False)
        if nombre == 'stable':
            # Del ticker de la stablecoin en yfinance solo nos quedamos con el VOLUMEN;
            # el precio ya viene de tu base de datos (más fiable y consistente con el resto del proyecto)
            serie = df_temp['Volume'].squeeze()
            datos_extraidos['volumen_stable'] = _normalizar_indice(serie, "volumen_stable (yfinance)")
        else:
            serie = df_temp['Close'].squeeze()
            datos_extraidos[nombre] = _normalizar_indice(serie, f"{nombre} (yfinance)")
    df = pd.DataFrame(datos_extraidos)
    return df


# =====================================================================
# 3. UNIFICACIÓN
# =====================================================================
print("Iniciando extracción híbrida (MySQL + yfinance)...")
engine = conectar_db()

precio_stable = obtener_precio_stable_bd(engine)
btc = obtener_btc_hibrido(engine)
df_macro_yf = obtener_volumen_y_macro_yf()

print("Unificando el dataset y procesando días no laborables...")
precio_stable = _normalizar_indice(precio_stable, "precio_stable (final)")
btc = _normalizar_indice(btc, "btc (final)")
df_macro_yf = df_macro_yf[~df_macro_yf.index.duplicated(keep='last')].sort_index()

df = pd.concat([precio_stable, btc, df_macro_yf], axis=1)

# Rellenamos huecos de fines de semana / días sin dato (fin de semana en macro, o solapes de fuentes)
df = df.ffill()

# =====================================================================
# 4. CÁLCULO DE LAS VARIABLES DEL MODELO ECONOMÉTRICO (sin cambios respecto al original)
# =====================================================================
print("Calculando las variables de riesgo...")

# A. Variable Dependiente: Desviación absoluta del peg (D_t = |Precio - 1|)
df['D_t'] = (df['precio_stable'] - 1.0).abs()

# B. Riesgo de Mercado: Volatilidad histórica de Bitcoin a 30 días (Anualizada)
df['ret_btc'] = np.log(df['btc'] / df['btc'].shift(1))
df['riesgo_mercado_btc'] = df['ret_btc'].rolling(window=30).std() * np.sqrt(365)

# C. Riesgo de Liquidez: Logaritmo natural del volumen de la stablecoin
df['riesgo_liquidez_ln_vol'] = np.log(df['volumen_stable'])

# Renombramos las variables macroeconómicas para que queden claras en tu modelo
df = df.rename(columns={
    'treasury': 'tasas_eeuu',
    'dxy': 'indice_dolar',
    'vix': 'volatilidad_vix'
})

# =====================================================================
# 5. LIMPIEZA FINAL Y EXPORTACIÓN A CSV (sin cambios respecto al original)
# =====================================================================
columnas_finales = [
    'D_t',
    'riesgo_mercado_btc',
    'riesgo_liquidez_ln_vol',
    'tasas_eeuu',
    'indice_dolar',
    'volatilidad_vix'
]

df_modelo = df[columnas_finales].dropna()
df_modelo = df_modelo.reset_index()
df_modelo = df_modelo.rename(columns={df_modelo.columns[0]: 'fecha'})

nombre_archivo = "dataset_stablecoins_macro_2021_2026.csv"
df_modelo.to_csv(nombre_archivo, index=False)

print("\n--- ¡Proceso Completado con Éxito! ---")
print(f"Rango de datos final: {df_modelo['fecha'].min()} a {df_modelo['fecha'].max()}")
print(f"Número total de observaciones (días): {len(df_modelo)}")
print(f"Archivo guardado como: '{nombre_archivo}'")

print("\nVista previa del dataset generado:")
print(df_modelo.tail())

# =====================================================================
# 6. GUARDADO EN MYSQL (tabla 'modelo_riesgo_macro')
# =====================================================================
stablecoin_id = obtener_stablecoin_id(engine, NOMBRE_STABLE)
guardar_modelo_macro_bd(engine, df_modelo, stablecoin_id)
