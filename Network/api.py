import requests
import pandas as pd
def extraer_stablecoins_con_desviacion(stablecoin_id="1", ruta_csv="Data/stablecoins_analisis.csv"):
    """
    Extrae datos de DefiLlama, desempaqueta los diccionarios,
    calcula el precio implícito y obtiene la desviación del peg.
    """
    url = f"https://stablecoins.llama.fi/stablecoincharts/all?stablecoin={stablecoin_id}"
    
    print(f"Solicitando paquete de datos a DefiLlama para la stablecoin ID {stablecoin_id}...")
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            
            # 1. Limpieza de fechas
            df['fecha'] = pd.to_datetime(df['date'], unit='s').dt.date
            
            # 2. DESEMPAQUETAR: Sacamos el número de dentro del diccionario {'peggedUSD': X}
            # Usamos .apply(lambda x: ...) para extraer el valor de forma segura
            df['supply_stablecoin'] = df['totalCirculating'].apply(lambda x: x.get('peggedUSD', 0) if isinstance(x, dict) else 0)
            df['valor_total_usd'] = df['totalCirculatingUSD'].apply(lambda x: x.get('peggedUSD', 0) if isinstance(x, dict) else 0)
            
            # Filtramos filas donde el supply sea 0 para evitar divisiones por cero imprevistas
            df = df[df['supply_stablecoin'] > 0].copy()
            
            # 3. CÁLCULO DEL PRECIO: Dividimos el valor total en USD entre la cantidad de monedas
            df['usd_price'] = df['valor_total_usd'] / df['supply_stablecoin']
            
            # 4. TU FÓRMULA: Calculamos la desviación restándole 1 al precio obtenido
            df['desviacion_peg'] = (1.0 - df['usd_price']).abs()
            
            # 5. Seleccionamos las columnas limpias de negocio
            df_final = df[['fecha', 'supply_stablecoin', 'usd_price', 'desviacion_peg']]
            
            # Guardamos en el CSV
            df_final.to_csv(ruta_csv, index=False)
            print(f"¡Éxito absoluto! Archivo guardado correctamente en: {ruta_csv}")
            print(df_final.head())
            
            return df_final
        else:
            print(f"Error en la API. Código: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Ocurrió un error inesperado al procesar: {e}")
        return None

def extraer_y_guardar_coingecko_con_key(coin_id="bitcoin", days="365", ruta_csv="Data/data_bitcoin.csv"):
    """
    Extrae el precio histórico Y EL VOLUMEN de CoinGecko usando la API Key.
    """
    print(f"Iniciando extracción de {coin_id} desde la API oficial de CoinGecko...")
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
    
    api_key_coingecko = "CG-cvz8muRDHdGNzrVAnqtktzo7"
    headers = {"accept": "application/json", "x-cg-demo-api-key": api_key_coingecko}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            # 1. Extraemos precios y volúmenes (ambos vienen en el mismo JSON)
            lista_precios = data['prices']
            lista_volumenes = data['total_volumes']
            
            # 2. Creamos los DataFrames individuales
            df_precios = pd.DataFrame(lista_precios, columns=['timestamp', 'precio_crypto'])
            df_volumenes = pd.DataFrame(lista_volumenes, columns=['timestamp', 'volumen_crypto'])
            
            # 3. Unimos precio y volumen por su timestamp
            df = pd.merge(df_precios, df_volumenes, on='timestamp')
            
            # 4. Limpiamos la fecha
            df['fecha'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date
            
            # 5. Agrupamos por día sacando la media de precio y volumen
            df_limpio = df.groupby('fecha').agg({
                'precio_crypto': 'mean',
                'volumen_crypto': 'mean'
            }).reset_index()
            
            df_limpio.to_csv(ruta_csv, index=False)
            return df_limpio
        else:
            print(f"Error en CoinGecko. Código: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    


def get_coingecko_data():
    """
    Extrae los datos de las 5 principales criptomonedas y las une
    en un único DataFrame de formato LARGO (ideal para Power BI).
    """
    # 1. Corregimos las llamadas con sus IDs y nombres de archivo correspondientes
    df_btc = extraer_y_guardar_coingecko_con_key(coin_id="bitcoin", days="365", ruta_csv="dData/ata_bitcoin.csv")
    df_eth = extraer_y_guardar_coingecko_con_key(coin_id="ethereum", days="365", ruta_csv="Data/data_ethereum.csv")
    df_bnb = extraer_y_guardar_coingecko_con_key(coin_id="binancecoin", days="365", ruta_csv="Data/data_binancecoin.csv")
    df_sol = extraer_y_guardar_coingecko_con_key(coin_id="solana", days="365", ruta_csv="Data/data_solana.csv")
    df_xrp = extraer_y_guardar_coingecko_con_key(coin_id="ripple", days="365", ruta_csv="Data/data_ripple.csv")
    
    # Lista para recolectar las tablas limpias
    listado_dfs = []
    
    # Diccionario para mapear cada DataFrame con su etiqueta de negocio
    mapeo_cryptos = {
        'bitcoin': df_btc,
        'ethereum': df_eth,
        'binancecoin': df_bnb,
        'solana': df_sol,
        'ripple': df_xrp
    }
    
    for nombre_id, df_individual in mapeo_cryptos.items():
        if df_individual is not None:
            df_temp = df_individual.copy()
            df_temp['crypto_id'] = nombre_id
            # Nos aseguramos de quedarnos con las columnas correctas incluyendo volumen
            df_temp = df_temp[['fecha', 'precio_crypto', 'volumen_crypto', 'crypto_id']]
            listado_dfs.append(df_temp)
            
    if len(listado_dfs) > 0:
        # Apilamos todos los DataFrames verticalmente
        df_crypto_largo = pd.concat(listado_dfs, ignore_index=True)
        return df_crypto_largo
    else:
        print("❌ Error: No se pudo extraer ninguna criptomoneda.")
        return None