import os
import sys
from pathlib import Path
import yfinance as yf
import pandas as pd
import numpy as np
from dotenv import load_dotenv, find_dotenv

# Cargar variables de entorno
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# Carpeta de salida para los CSV generados
RAIZ_PROYECTO = Path(dotenv_path).resolve().parent if dotenv_path else Path.cwd()
CARPETA_DATOS_ENV = os.getenv("CARPETA_DATOS", "data/clean")
CARPETA_SALIDA = (RAIZ_PROYECTO / CARPETA_DATOS_ENV).resolve()
CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)

# =====================================================================
# 1. CONFIGURACIÓN DE PARÁMETROS Y TICKERS
# =====================================================================
fecha_inicio = "2021-01-01"
fecha_fin = "2026-07-15"

# Tickers de Yahoo Finance para todas las variables
tickers = {
    'stable': 'USDT-USD',
    'btc': 'BTC-USD',
    'treasury': '^IRX',
    'dxy': 'DX-Y.NYB',
    'vix': '^VIX'
}

def _normalizar_indice(obj, nombre_fuente=""):
    """Normaliza el índice de fechas (sin hora) y elimina duplicados conservando el último valor."""
    obj = obj.copy()
    obj.index = pd.to_datetime(obj.index).normalize()
    n_dup = int(obj.index.duplicated().sum())
    if n_dup > 0:
        print(f"⚠️  {nombre_fuente}: se encontraron {n_dup} fechas duplicadas, se conserva el último valor.")
        obj = obj[~obj.index.duplicated(keep='last')]
    return obj.sort_index()

# =====================================================================
# 2. EXTRAER DATOS DIRECTAMENTE DE YAHOO FINANCE
# =====================================================================
print("📥 Descargando todos los datos desde Yahoo Finance (yfinance)...")

datos_extraidos = {}

# A. Descarga de la Stablecoin (Precio de cierre y Volumen)
print(f"   - Descargando Stablecoin ({tickers['stable']})...")
df_stable = yf.download(tickers['stable'], start=fecha_inicio, end=fecha_fin, progress=False)
datos_extraidos['precio_stable'] = _normalizar_indice(df_stable['Close'].squeeze(), "precio_stable")
datos_extraidos['volumen_stable'] = _normalizar_indice(df_stable['Volume'].squeeze(), "volumen_stable")

# B. Descarga de Bitcoin y Variables Macroeconómicas
for clave, ticker in tickers.items():
    if clave == 'stable':
        continue
    print(f"   - Descargando {clave} ({ticker})...")
    df_temp = yf.download(ticker, start=fecha_inicio, end=fecha_fin, progress=False)
    datos_extraidos[clave] = _normalizar_indice(df_temp['Close'].squeeze(), clave)

# =====================================================================
# 3. UNIFICACIÓN Y TRATAMIENTO DE FALTANTES
# =====================================================================
print(" Unificando dataset y rellenando días no laborables...")
df = pd.DataFrame(datos_extraidos)

# Rellenar fines de semana / festivos para las series macroeconómicas
df = df.ffill()

# =====================================================================
# 4. CÁLCULO DE VARIABLES DEL MODELO ECONOMÉTRICO
# =====================================================================
print(" Calculando las variables de riesgo...")

# A. Variable Dependiente: Desviación absoluta del peg (D_t = |Precio - 1|)
df['D_t'] = (df['precio_stable'] - 1.0).abs()

# B. Riesgo de Mercado: Volatilidad histórica de Bitcoin a 30 días (Anualizada)
df['ret_btc'] = np.log(df['btc'] / df['btc'].shift(1))
df['riesgo_mercado_btc'] = df['ret_btc'].rolling(window=30).std() * np.sqrt(365)

# C. Riesgo de Liquidez: Logaritmo natural del volumen de la stablecoin
df['riesgo_liquidez_ln_vol'] = np.log(df['volumen_stable'])

# Renombrar columnas macroeconómicas
df = df.rename(columns={
    'treasury': 'tasas_eeuu',
    'dxy': 'indice_dolar',
    'vix': 'volatilidad_vix'
})

# =====================================================================
# 5. LIMPIEZA FINAL Y EXPORTACIÓN A CSV
# =====================================================================
columnas_finales = [
    'D_t',
    'riesgo_mercado_btc',
    'riesgo_liquidez_ln_vol',
    'tasas_eeuu',
    'indice_dolar',
    'volatilidad_vix'
]

df_modelo = df[columnas_finales].dropna().reset_index()
df_modelo = df_modelo.rename(columns={df_modelo.columns[0]: 'fecha'})

nombre_archivo = "dataset_stablecoins_macro_2021_2026.csv"
ruta_archivo = CARPETA_SALIDA / nombre_archivo

# Guardar en CSV
df_modelo.to_csv(ruta_archivo, index=False)

print("\n--- ¡Proceso Completado con Éxito! ---")
print(f"Rango de datos final: {df_modelo['fecha'].min().strftime('%Y-%m-%d')} a {df_modelo['fecha'].max().strftime('%Y-%m-%d')}")
print(f"Número total de observaciones (días): {len(df_modelo)}")
print(f"Archivo guardado como: '{ruta_archivo}'")

print("\nVista previa del dataset generado:")
print(df_modelo.tail())