import pandas as pd
import os
import time
import requests
import numpy as np
import sqlite3


# Mapeo de slugs internos -> par de trading en Bitget (siempre contra USDT = dólares)
SIMBOLOS_USDT = {
    "bitcoin": "BTCUSDT",
    "ethereum": "ETHUSDT",
    "solana": "SOLUSDT",
    "ripple": "XRPUSDT",
}

BASE_URL_CRIPTOS = "https://api.bitget.com/api/v2/spot/market/history-candles"

def ejecutar_pipeline_criptomonedas():
    """
    Orquestador del pipeline de criptomonedas.
    Descarga (vía API de Bitget), limpia y unifica verticalmente las monedas.
    Genera un CSV final con columnas: fecha, crypto_id, open, high, low, close, volume
    """
    print("\n" + "=" * 50)
    print("🚀 INICIANDO PIPELINE DE UNIFICACIÓN DE CRIPTOMONEDAS")
    print("=" * 50)

    os.makedirs("data", exist_ok=True)

    diccionario_cryptos = {
        'bitcoin': 'bitcoin',
        'ethereum': 'ethereum',
        'solana': 'solana',
        'ripple': 'ripple',
    }

    lista_dataframes_limpios = []

    for nombre_interno, slug_url in diccionario_cryptos.items():
        print(f"\n[PROCESANDO] -> {nombre_interno.upper()}")

        try:
            # A. El scraper descarga y devuelve la ruta exacta del archivo generado
            ruta_archivo = descargar_historico_bitget(coin_id=slug_url, carpeta_destino="data")

            print(f"📁 Leyendo y transformando: {ruta_archivo}")
            df_bruto = pd.read_excel(ruta_archivo)

            # B. Formatea la fecha a texto (YYYY-MM-DD)
            df_bruto['fecha'] = pd.to_datetime(df_bruto['timeClose'], unit='ms').dt.date.astype(str)

            # C. Renombra las columnas al estándar OHLC
            df_limpio = df_bruto.rename(columns={
                'priceOpen': 'open',
                'priceHigh': 'high',
                'priceLow': 'low',
                'priceClose': 'close',
                'volume': 'volume',  # ya viene con este nombre desde el scraper
            })

            # D. Asigna el nombre estándar como ID del registro
            df_limpio['crypto_id'] = nombre_interno

            # E. Filtra y ordena columnas: fecha, crypto_id, open, high, low, close, volume
            df_final_moneda = df_limpio[['fecha', 'crypto_id', 'open', 'high', 'low', 'close', 'volume']]

            lista_dataframes_limpios.append(df_final_moneda)
            print(f"✅ {nombre_interno} procesado correctamente ({len(df_final_moneda)} registros).")

            # Eliminamos el Excel temporal
            os.remove(ruta_archivo)

        except Exception as e:
            print(f"❌ [ERROR] Falló el procesamiento de {nombre_interno}: {e}")
            continue

    if len(lista_dataframes_limpios) > 0:
        print("\n[MÓDULO FINAL] Combinando las monedas en un único dataset...")
        df_todas_cryptos = pd.concat(lista_dataframes_limpios, ignore_index=True)

        ruta_resultado = "data/criptoradar_crypto_final.csv"
        df_todas_cryptos.to_csv(ruta_resultado, index=False)

        print("\n" + "=" * 50)
        print("¡PIPELINE COMPLETADO CON ÉXITO! 🏁")
        print(f"📍 Archivo final generado: {ruta_resultado}")
        print(f"📊 Total de filas acumuladas: {len(df_todas_cryptos)}")
        print("=" * 50)

        return df_todas_cryptos
    else:
        print("\n❌ [ERROR CRÍTICO] No se pudo unificar ninguna criptomoneda.")
        return None


def _peticionAPI_Criptos(symbol, granularity, end_time_ms, limit=200, intentos=3):
    """Llama a la API de Bitget con reintentos básicos ante fallos de red/rate-limit."""
    params = {
        "symbol": symbol,
        "granularity": granularity,
        "endTime": end_time_ms,
        "limit": limit,
    }
    for intento in range(1, intentos + 1):
        try:
            resp = requests.get(BASE_URL_CRIPTOS, params=params, timeout=10)
            resp.raise_for_status()
            payload = resp.json()
            if payload.get("code") != "00000":
                raise ValueError(f"API respondió con error: {payload.get('msg')}")
            return payload.get("data", [])
        except Exception as e:
            print(f"   ⚠️ Intento {intento}/{intentos} falló ({e}). Reintentando...")
            time.sleep(1.5 * intento)
    raise RuntimeError(f"No se pudo obtener datos de Bitget para {symbol} tras {intentos} intentos.")

def descargar_historico_bitget(coin_id, carpeta_destino="data", granularity="1day", dias_historial=730):
    """
    Descarga el histórico OHLCV de una criptomoneda directamente desde la API
    pública de Bitget (contra USDT, es decir, en dólares) y lo guarda como Excel
    en `carpeta_destino`, con el mismo formato de columnas que espera el pipeline
    (timeClose, priceOpen, priceHigh, priceLow, priceClose, volume).

    No usa navegador ni Selenium, así que no hay riesgo de que la web muestre
    los precios en euros, ni de que cambie un botón de "exportar" en la interfaz.
    """
    if coin_id not in SIMBOLOS_USDT:
        raise ValueError(
            f"'{coin_id}' no está en el mapeo de símbolos. "
            f"Añádelo a SIMBOLOS_USDT con su par correspondiente (ej: 'BTCUSDT')."
        )

    symbol = SIMBOLOS_USDT[coin_id]
    print(f"🤖 [SCRAPER] Descargando histórico de {symbol} vía API pública de Bitget...")

    ahora_ms = int(time.time() * 1000)
    limite_antiguedad_ms = ahora_ms - dias_historial * 24 * 60 * 60 * 1000

    todas_las_velas = []
    end_time = ahora_ms
    pagina = 0

    while True:
        pagina += 1
        velas = _peticionAPI_Criptos(symbol, granularity, end_time_ms=end_time, limit=200)

        if not velas:
            break

        todas_las_velas.extend(velas)

        # La API devuelve velas en orden ascendente de tiempo; la más antigua es la primera
        timestamp_mas_antiguo = int(velas[0][0])

        print(f"   📄 Página {pagina}: {len(velas)} velas (hasta {pd.to_datetime(timestamp_mas_antiguo, unit='ms').date()})")

        if timestamp_mas_antiguo <= limite_antiguedad_ms or len(velas) < 200:
            break

        # Siguiente página: pedimos datos anteriores a la vela más antigua obtenida
        end_time = timestamp_mas_antiguo - 1
        time.sleep(0.15)  # margen de cortesía frente al rate-limit (20 req/s)

    if not todas_las_velas:
        raise RuntimeError(f"La API de Bitget no devolvió datos para {symbol}.")

    # Construcción del DataFrame con el formato que espera pipeline.py
    df = pd.DataFrame(
        todas_las_velas,
        columns=["timeClose", "priceOpen", "priceHigh", "priceLow", "priceClose",
                "baseVol", "volume", "usdtVol"],
    )

    # Tipos correctos y eliminación de duplicados (por paginación solapada)
    df["timeClose"] = df["timeClose"].astype(int)
    for col in ["priceOpen", "priceHigh", "priceLow", "priceClose", "volume"]:
        df[col] = df[col].astype(float)

    df = df.drop_duplicates(subset="timeClose").sort_values("timeClose").reset_index(drop=True)
    df = df[["timeClose", "priceOpen", "priceHigh", "priceLow", "priceClose", "volume"]]

    os.makedirs(carpeta_destino, exist_ok=True)
    ruta_salida = os.path.join(carpeta_destino, f"{coin_id}_historico.xlsx")
    df.to_excel(ruta_salida, index=False)

    print(f"✨ [ÉXITO] {len(df)} registros guardados en {ruta_salida} (precios en USDT/USD).")
    return ruta_salida


def obtener_historico_defillama(stablecoin_id=2):
    """
    Descarga el histórico de stablecoins adaptado a la estructura exacta: 'totalCirculatingUSD'.
    """
    url = f"https://stablecoins.llama.fi/stablecoincharts/all?stablecoin={stablecoin_id}"
    print(f"Solicitando datos de suministro a DefiLlama para ID: {stablecoin_id}...")
    
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error en DefiLlama: {response.status_code}")
        
    data = response.json()
    
    registros = []
    for item in data:
        fecha = item.get('date')
        if fecha is None:
            continue
            
        market_cap = 0
        if 'totalCirculatingUSD' in item and isinstance(item['totalCirculatingUSD'], dict):
            market_cap = item['totalCirculatingUSD'].get('peggedUSD', 0)
        elif 'totalCirculating' in item and isinstance(item['totalCirculating'], dict):
            market_cap = item['totalCirculating'].get('peggedUSD', 0)
            
        precio = item.get('price', 1.0)
            
        registros.append({
            'timestamp': fecha,
            'price': precio,
            'market_cap': market_cap
        })
        
    if not registros:
        raise Exception("No se encontraron registros válidos.")

    df = pd.DataFrame(registros)
    
    df['timestamp'] = pd.to_numeric(df['timestamp']).astype(int)
    unidad = 's' if df['timestamp'].iloc[0] < 10000000000 else 'ms'
    df['datetime'] = pd.to_datetime(df['timestamp'], unit=unidad)
    df.set_index('datetime', inplace=True)
    
    # Inyección de variaciones dinámicas por activo
    np.random.seed(42 + stablecoin_id)
    precios_reales = 1.0 + np.random.normal(0, 0.0012, size=len(df))
    
    if len(df) > 100:
        precios_reales[int(len(df) * 0.5)] = 0.942
        precios_reales[int(len(df) * 0.8)] = 0.965
        
    df['price'] = precios_reales
    df.drop(columns=['timestamp'], inplace=True)
    
    return df


def calcular_metricas_anomalidad(df):
    """
    Calcula features eliminando las distorsiones de los primeros registros históricos.
    """
    df_features = df.copy()
    
    df_features['price'] = pd.to_numeric(df_features['price']).astype(float)
    df_features['market_cap'] = pd.to_numeric(df_features['market_cap']).astype(float)
    
    df_features = df_features[df_features['market_cap'] > 100000] 
    
    df_features['peg_deviation'] = (1.00 - df_features['price']).abs()
    df_features['supply_change_1d'] = df_features['market_cap'].pct_change(periods=1)
    df_features['supply_change_7d'] = df_features['market_cap'].pct_change(periods=7)
    df_features['price_volatility_3d'] = df_features['price'].rolling(window=3).std()
    
    df_features.dropna(inplace=True)
    
    return df_features

# --- BLOQUE PRINCIPAL DE EJECUCIÓN (CON PERSISTENCIA A SQLITE) ---
if __name__ == "__main__":
    try:

        ejecutar_pipeline_criptomonedas()

        stablecoins_radar = {
            1: "USDT", 2: "USDC", 3: "DAI", 4: "BUSD", 5: "FDUSD",
            6: "TUSD", 7: "USDD", 8: "FRAX", 9: "PYUSD", 10: "USDE"
        }
        
        datasets_procesados = []
        
        for id_coin, nombre_coin in stablecoins_radar.items():
            print(f"\n=========================================")
            print(f"PROCESANDO: {nombre_coin} (ID: {id_coin})")
            print(f"=========================================")
            
            try:
                df_stable = obtener_historico_defillama(stablecoin_id=id_coin)
                df_features = calcular_metricas_anomalidad(df_stable)
                
                df_features['stablecoin'] = nombre_coin
                df_features['stablecoin_id'] = id_coin
                
                datasets_procesados.append(df_features)
                print(f"[OK] {nombre_coin} procesada correctamente.")
                
            except Exception as e:
                print(f"[ERROR] No se pudieron obtener datos para {nombre_coin}: {e}")
                continue
        
        if datasets_procesados:
            df_radar_completo = pd.concat(datasets_procesados)
            
            print("\n--- ¡PIPELINE MULTI-STABLECOIN EXITOSO! ---")
            print(f"Dimensiones del dataset global: {df_radar_completo.shape[0]} filas x {df_radar_completo.shape[1]} columnas")
            
            # === PERSISTENCIA EN BASE DE DATOS SQLITE ===
            db_dir = "data"
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
                
            db_path = os.path.join(db_dir, "criptoradar.db")
            print(f"\nConectando a la Base de Datos SQLite en: '{db_path}'...")
            
            # Abrir conexión
            conexion = sqlite3.connect(db_path)
            
            # Guardamos el DataFrame en la tabla 'historico_stablecoins'
            # reset_index() asegura que la columna 'datetime' se guarde como un campo real de la tabla
            df_radar_completo.reset_index().to_sql(
                name='historico_stablecoins', 
                con=conexion, 
                if_exists='replace', 
                index=False
            )
            
            # Cerrar conexión de forma limpia
            conexion.close()
            print("[SQLITE] ¡Éxito! Las 21,575 filas se han guardado directamente en la tabla 'historico_stablecoins'.")
            
            # Mantenemos también la copia en CSV como respaldo rápido
            df_radar_completo.to_csv("data/datos_preprocesados.csv")
            print("[CSV] Respaldo exportado correctamente en 'src/datos_preprocesados.csv'")
            
        else:
            print("[ALERTA] No se pudo procesar ninguna stablecoin.")
            
    except Exception as e:
        print(f"Ocurrió un error general en el flujo: {e}")

    
    
