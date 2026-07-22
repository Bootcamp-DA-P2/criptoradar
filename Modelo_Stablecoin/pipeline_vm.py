import yfinance as yf
import pandas as pd
import numpy as np

# =====================================================================
# 1. CONFIGURACIÓN DE PARÁMETROS
# =====================================================================
fecha_inicio = "2021-01-01"
fecha_fin = "2026-07-15"

# Definimos los tickers de Yahoo Finance de forma explícita
tickers = {
    'stable': 'USDT-USD',    # Puedes cambiarlo a 'USDC-USD' o 'DAI-USD'
    'btc': 'BTC-USD',
    'treasury': '^IRX',      # Rendimiento del Bono del Tesoro a 3 meses (Macro)
    'dxy': 'DX-Y.NYB',       # Índice del Dólar (Macro)
    'vix': '^VIX'            # Índice de volatilidad de Wall Street (Macro)
}

print("Iniciando la extracción individual de variables de Yahoo Finance...")

# =====================================================================
# 2. EXTRACCIÓN INDIVIDUAL (Para evitar problemas de MultiIndex)
# =====================================================================
datos_extraidos = {}

for nombre, ticker in tickers.items():
    print(f"Descargando {nombre} ({ticker})...")
    # Descargamos los datos históricos
    df_temp = yf.download(ticker, start=fecha_inicio, end=fecha_fin, progress=False)
    
    # Nos aseguramos de extraer únicamente la columna 'Adj Close'
    # y la convertimos en una serie plana
    if nombre == 'stable':
        # Para la stablecoin también guardamos el volumen
        datos_extraidos['precio_stable'] = df_temp['Adj Close'].squeeze()
        datos_extraidos['volumen_stable'] = df_temp['Volume'].squeeze()
    else:
        datos_extraidos[nombre] = df_temp['Adj Close'].squeeze()

# =====================================================================
# 3. UNIFICACIÓN Y TRATAMIENTO DE FINES DE SEMANA
# =====================================================================
print("Unificando el dataset y procesando días no laborables...")

# Creamos el DataFrame unificado
df = pd.DataFrame(datos_extraidos)

# Muy importante: Rellenamos los huecos de los fines de semana (sábados y domingos)
# para las variables macroeconómicas tradicionales (Treasury, DXY y VIX)
# usando .ffill() para propagar el precio del viernes
df = df.ffill()

# =====================================================================
# 4. CÁLCULO DE LAS VARIABLES DEL MODELO ECONOMÉTRICO
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
    'treasury': 'tasas_eeuu',  # Costo de oportunidad / salud del colateral
    'dxy': 'indice_dolar',     # Fortaleza del dólar global
    'vix': 'volatilidad_vix'   # Aversión al riesgo global
})

# =====================================================================
# 5. LIMPIEZA FINAL Y EXPORTACIÓN A CSV
# =====================================================================
# Filtramos las columnas que necesitamos para el modelo final y eliminamos filas vacías
columnas_finales = [
    'D_t', 
    'riesgo_mercado_btc', 
    'riesgo_liquidez_ln_vol', 
    'tasas_eeuu', 
    'indice_dolar', 
    'volatilidad_vix'
]

# Eliminamos los primeros 30 días que no tienen volatilidad de BTC debido al cálculo móvil
df_modelo = df[columnas_finales].dropna()

# Convertimos el índice de fechas a una columna estándar del DataFrame
df_modelo = df_modelo.reset_index().rename(columns={'Date': 'fecha'})

# Guardamos el resultado en un archivo CSV
nombre_archivo = "dataset_stablecoins_macro_2021_2026.csv"
df_modelo.to_csv(nombre_archivo, index=False)

print("\n--- ¡Proceso Completado con Éxito! ---")
print(f"Rango de datos final: {df_modelo['fecha'].min().strftime('%Y-%m-%d')} a {df_modelo['fecha'].max().strftime('%Y-%m-%d')}")
print(f"Número total de observaciones (días): {len(df_modelo)}")
print(f"Archivo guardado como: '{nombre_archivo}'")

# Vista previa para verificar que las columnas macro tienen datos válidos
print("\nVista previa del dataset generado:")
print(df_modelo.tail())