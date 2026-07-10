import requests
import pandas as pd
import numpy as np
import time  

GECKO_IDS = {
    "USDT": "tether", "USDC": "usd-coin", "DAI": "dai", "BUSD": "binance-usd",
    "FDUSD": "first-digital-usd", "TUSD": "true-usd", "USDD": "usdd",
    "FRAX": "frax", "PYUSD": "paypal-usd", "USDE": "ethena-usde", "USDS": "stable-usd",
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

    MAX_SPAN = 500  # límite duro de la API
    SEGUNDOS_POR_PERIODO = 86400 if period == "1d" else 3600

    all_points = []
    current_start = start_ts
    remaining = span

    while remaining > 0:
            chunk_span = min(remaining, MAX_SPAN)
            params = {"start": current_start, "span": chunk_span, "period": period}
            response = requests.get(url, params=params)
            time.sleep(1)

            if response.status_code != 200:
                raise Exception(f"Error en DefiLlama coins ({nombre_coin}): {response.status_code} - {response.text}")

            data = response.json()

            if coin in data.get("coins", {}):                     
                puntos = data["coins"][coin].get("prices", [])
                all_points.extend(puntos)
            # si no encontramos datos para ese bloque c simplemente no añadimos nada y seguimos al siguiente bloque 

            remaining -= chunk_span
            current_start += chunk_span * SEGUNDOS_POR_PERIODO 

    if not all_points:
        return pd.DataFrame(columns=["price_real"])

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
    time.sleep(1)

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

    # Calculamos el span real en días naturales, no por longitud de filas
    start_ts = int(df.index.min().timestamp())
    span = (df.index.max() - df.index.min()).days + 1
    
    df_price = obtener_precio_real(nombre_coin, start_ts=start_ts, span=span, period="1d")

    # Unimos usando inner para asegurar que se alineen perfectamente por fecha
    df = df.join(df_price, how="inner")
    df.rename(columns={"price_real": "price"}, inplace=True)

    df.index.name = 'datetime'

    return df

def calcular_metricas_anomalidad(df):
    """
    Calcula features eliminando las distorsiones de los primeros registros históricos.
    """
    if df.empty:
        return df
        
    df_features = df.copy()
    
    df_features['price'] = pd.to_numeric(df_features['price']).astype(float)
    df_features['market_cap'] = pd.to_numeric(df_features['market_cap']).astype(float)
    
    # Filtro para evitar ruido de proyectos recién nacidos o sin liquidez
    df_features = df_features[df_features['market_cap'] > 100000] 
    
    # Asegurar orden cronológico antes de aplicar ventanas móviles
    df_features.sort_index(inplace=True)
    
    df_features['peg_deviation'] = (1.00 - df_features['price']).abs()
    df_features['supply_change_1d'] = df_features['market_cap'].pct_change(periods=1)
    df_features['supply_change_7d'] = df_features['market_cap'].pct_change(periods=7)
    df_features['price_volatility_3d'] = df_features['price'].rolling(window=3).std()
    
    df_features.dropna(inplace=True)
    
    df_features.index.name = 'datetime'
    
    return df_features