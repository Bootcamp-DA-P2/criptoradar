import requests
import pandas as pd
import numpy as np
import time  

GECKO_IDS = {
    "USDT": "tether", "USDC": "usd-coin", "DAI": "dai", "BUSD": "binance-usd",
    "FDUSD": "first-digital-usd", "TUSD": "true-usd", "USDD": "usdd",
    "FRAX": "frax", "PYUSD": "paypal-usd", "USDE": "ethena-usde",
}
def obtener_precio_real(nombre_coin, start_ts, span, period="1d"):
    """
    Descarga precio histórico real desde coins.llama.fi, paginando en bloques
    de máximo 500 puntos porque la API rechaza peticiones más grandes (error 400).
    """
    gecko_id = GECKO_IDS.get(nombre_coin)
    if gecko_id is None:
        raise ValueError(f"No tengo gecko_id mapeado para {nombre_coin}")

    coin = f"coingecko:{gecko_id}"
    url = f"https://coins.llama.fi/chart/{coin}"

    MAX_SPAN = 500  #límite duro de la API (1 coin x 500 timestamps)
    SEGUNDOS_POR_PERIODO = 86400 if period == "1d" else 3600  # soporta "1d"/"1h"

    all_points = []
    current_start = start_ts
    remaining = span

    while remaining > 0:  # bucle de paginación
        chunk_span = min(remaining, MAX_SPAN)
        params = {"start": current_start, "span": chunk_span, "period": period}
        response = requests.get(url, params=params)
        time.sleep(1)

        if response.status_code != 200:
            raise Exception(f"Error en DefiLlama coins ({nombre_coin}): {response.status_code} - {response.text}")

        data = response.json()
        puntos = data["coins"][coin]["prices"]
        all_points.extend(puntos)

        remaining -= chunk_span
        current_start += chunk_span * SEGUNDOS_POR_PERIODO  

    df_price = pd.DataFrame(all_points).drop_duplicates(subset="timestamp")  
    df_price["datetime"] = pd.to_datetime(df_price["timestamp"], unit="s").dt.normalize()
    df_price.set_index("datetime", inplace=True)
    return df_price[["price"]].rename(columns={"price": "price_real"})

def obtener_historico_defillama(stablecoin_id=2, nombre_coin=None):
    """
    Descarga supply (DefiLlama) y precio real (DefiLlama coins) y los une por fecha.
    """
    url = f"https://stablecoins.llama.fi/stablecoincharts/all?stablecoin={stablecoin_id}"
    print(f"Solicitando datos de suministro a DefiLlama para ID: {stablecoin_id}...")
    response = requests.get(url)
    time.sleep(1)  # <-- CAMBIO: pausa tras la llamada a stablecoins.llama.fi

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
        registros.append({'timestamp': fecha, 'market_cap': market_cap})

    if not registros:
        raise Exception("No se encontraron registros válidos.")

    df = pd.DataFrame(registros)
    df['timestamp'] = pd.to_numeric(df['timestamp']).astype(int)
    unidad = 's' if df['timestamp'].iloc[0] < 10000000000 else 'ms'
    df['datetime'] = pd.to_datetime(df['timestamp'], unit=unidad).dt.normalize()
    df.set_index('datetime', inplace=True)
    df.drop(columns=['timestamp'], inplace=True)

    start_ts = int(df.index.min().timestamp())
    span = len(df)
    df_price = obtener_precio_real(nombre_coin, start_ts=start_ts, span=span, period="1d")

    df = df.join(df_price, how="inner")
    df.rename(columns={"price_real": "price"}, inplace=True)

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