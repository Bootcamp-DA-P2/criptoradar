import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# =====================================================================
# 1. CONFIGURACIÓN DE PARÁMETROS
# =====================================================================
fecha_inicio = "2021-01-01"
fecha_fin = "2026-07-15"

# Definimos los tickers de Yahoo Finance
tickers = {
    'stable': 'USDT-USD',    # Stablecoin de estudio
    'btc': 'BTC-USD',        # Para volatilidad
    'treasury': '^IRX',      # Rendimiento del Bono del Tesoro a 3 meses (Macro)
    'dxy': 'DX-Y.NYB',       # Índice del Dólar (Macro)
    'vix': '^VIX'            # Índice de volatilidad de Wall Street (Macro)
}

print("Iniciando la extracción individual de variables de Yahoo Finance...")

# =====================================================================
# 2. EXTRACCIÓN INDIVIDUAL SEGURA
# =====================================================================
datos_extraidos = {}

for nombre, ticker in tickers.items():
    print(f"Descargando {nombre} ({ticker})...")
    # Descargamos los datos históricos individuales de forma limpia
    df_temp = yf.download(ticker, start=fecha_inicio, end=fecha_fin, progress=False)
    
    # yfinance puede devolver nombres de columna ligeramente distintos.
    # Buscamos 'Adj Close' y, si no existe, usamos 'Close' como respaldo.
    col_precio = 'Adj Close' if 'Adj Close' in df_temp.columns else 'Close'
    
    # Extraemos la columna correspondiente asegurando que sea unidimensional (.squeeze())
    datos_extraidos[f'precio_{nombre}'] = df_temp[col_precio].squeeze()
    
    # En el caso de la stablecoin, también necesitamos su volumen
    if nombre == 'stable':
        datos_extraidos['volumen_stable'] = df_temp['Volume'].squeeze()

# =====================================================================
# 3. UNIFICACIÓN Y TRATAMIENTO DE FINES DE SEMANA
# =====================================================================
print("Unificando el dataset y procesando días no laborables...")

# Creamos el DataFrame unificado uniendo las series por fecha
df = pd.DataFrame(datos_extraidos)

# Rellenamos los huecos de los fines de semana (sábados y domingos)
# para las variables macroeconómicas tradicionales (Treasury, DXY y VIX)
df = df.ffill()

# =====================================================================
# 4. CÁLCULO DE LAS VARIABLES DEL MODELO ECONOMÉTRICO
# =====================================================================
print("Calculando las variables de riesgo...")

# A. Variable Dependiente: Desviación absoluta del peg (D_t = |Precio - 1|)
df['D_t'] = (df['precio_stable'] - 1.0).abs()

# B. Riesgo de Mercado: Volatilidad histórica de Bitcoin a 30 días (Anualizada)
# Usamos el precio de BTC que descargamos
df['ret_btc'] = np.log(df['precio_btc'] / df['precio_btc'].shift(1))
df['riesgo_mercado_btc'] = df['ret_btc'].rolling(window=30).std() * np.sqrt(365)

# C. Riesgo de Liquidez: Logaritmo natural del volumen de la stablecoin
df['riesgo_liquidez_ln_vol'] = np.log(df['volumen_stable'])

# Renombramos las variables macroeconómicas para mayor claridad en el modelo
df = df.rename(columns={
    'precio_treasury': 'tasas_eeuu',  # Costo de oportunidad / colateral
    'precio_dxy': 'indice_dolar',     # Fuerza del USD
    'precio_vix': 'volatilidad_vix'   # Aversión al riesgo global
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

# Eliminamos los primeros 30 días vacíos causados por la volatilidad móvil de BTC
df_modelo = df[columnas_finales].dropna()

# Reseteamos el índice para que la fecha aparezca como columna estándar
df_modelo = df_modelo.reset_index().rename(columns={'Date': 'fecha'})

# Guardamos el archivo CSV final
nombre_archivo = PROJECT_ROOT / "dataset_stablecoins_macro_2021_2026.csv"
df_modelo.to_csv(nombre_archivo, index=False)

print("\n--- ¡Proceso Completado con Éxito! ---")
print(f"Rango de datos final: {df_modelo['fecha'].min().strftime('%Y-%m-%d')} a {df_modelo['fecha'].max().strftime('%Y-%m-%d')}")
print(f"Número total de observaciones (días): {len(df_modelo)}")
print(f"Archivo guardado como: '{nombre_archivo.name}'")

# Vista previa para comprobar el éxito del pipeline
print("\nVista previa del dataset generado:")
print(df_modelo.tail())