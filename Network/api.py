import requests
import pandas as pd
def extraer_stablecoins_con_desviacion(stablecoin_id="1", ruta_csv="stablecoins_analisis.csv"):
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
            df['precio_moneda'] = df['valor_total_usd'] / df['supply_stablecoin']
            
            # 4. TU FÓRMULA: Calculamos la desviación restándole 1 al precio obtenido
            df['desviacion_peg'] = (1.0 - df['precio_moneda']).abs()
            
            # 5. Seleccionamos las columnas limpias de negocio
            df_final = df[['fecha', 'supply_stablecoin', 'precio_moneda', 'desviacion_peg']]
            
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

def extraer_y_guardar_coingecko(coin_id="bitcoin", vs_currency="usd", days="30", ruta_csv="precios_coingecko.csv"):
    """
    Extrae el histórico de precios de una criptomoneda desde CoinGecko,
    lo limpia, lo formatea por fecha y lo exporta a un CSV.
    """
    # Usamos los parámetros para construir la URL dinámica
    url_coingecko = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    
    # Parámetros que exige la API de CoinGecko
    params = {
        'vs_currency': vs_currency,
        'days': days,
        'interval': 'daily'  # Para que nos dé un dato por día y coincida con DefiLlama
    }
    
    print(f"Iniciando extracción de {coin_id} desde CoinGecko...")
    try:
        response = requests.get(url_coingecko, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # CoinGecko devuelve 'prices' como una lista de listas: [[timestamp, precio], [timestamp, precio]...]
            df = pd.DataFrame(data['prices'], columns=['timestamp', f'precio_{coin_id}'])
            
            # --- RETO DE LA FECHA RESUELTO ---
            # Como viene en milisegundos, usamos unit='ms'
            df['fecha'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date
            
            # Seleccionamos solo las columnas de negocio que nos interesan
            df_limpio = df[['fecha', f'precio_{coin_id}']]
            
            # Guardamos en CSV
            df_limpio.to_csv(ruta_csv, index=False)
            print(f"¡Éxito! Datos de {coin_id} guardados en: {ruta_csv}")
            
            return df_limpio
        else:
            print(f"Error en CoinGecko API. Código: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Ocurrió un error en CoinGecko: {e}")
        return None