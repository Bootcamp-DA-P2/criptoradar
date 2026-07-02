import requests
import pandas as pd

def obtener_lista_stablecoins():
    # Paso 1: Ir a buscar los datos a la API de DefiLlama
    url = "https://stablecoins.llama.fi/stablecoins"
    respuesta = requests.get(url)

    # Paso 2: Convertir los datos en un formato que Python entienda
    datos_json = respuesta.json()

    # Paso 3: Extraer la lista y meterla en un DataFrame
    lista_stablecoins = datos_json["peggedAssets"]
    df_stablecoins = pd.DataFrame(lista_stablecoins)

    # Paso 4: Devolver el DataFrame al director de orquesta (app.py)
    return df_stablecoins


def obtener_historico_coingecko(coin_id="tether", days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    
    respuesta = requests.get(url, params=params)
    datos = respuesta.json()
    
    # Trae una lista de listas en 'prices' -> [timestamp, precio]
    df_precios = pd.DataFrame(datos["prices"], columns=["timestamp", "precio"])
    
    # Convertimos el Timestamp Unix a fecha legible
    df_precios["fecha"] = pd.to_datetime(df_precios["timestamp"], unit="ms")
    
    return df_precios