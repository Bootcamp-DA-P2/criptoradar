import os
import pandas as pd
# Importamos tus dos funciones limpias desde la carpeta Network
from Network.api import obtener_lista_stablecoins, obtener_historico_coingecko

if __name__ == "__main__":
    # 1. El director de orquesta prepara la carpeta en la raíz del proyecto
    carpeta_data = "Data"
    os.makedirs(carpeta_data, exist_ok=True)
    
    print("🚀 Iniciando el pipeline de CriptoRadar...")
    
    # 2. Llamamos a DefiLlama y guardamos su CSV
    print("Descargando datos actuales de DefiLlama...")
    df_llama = obtener_lista_stablecoins()
    ruta_llama = os.path.join(carpeta_data, "mercado_actual_llama.csv")
    df_llama.to_csv(ruta_llama, index=False)
    print(f"¡Guardado! -> {ruta_llama}")
    
    # 3. Llamamos a CoinGecko y guardamos su CSV
    print("Descargando histórico de Tether desde CoinGecko...")
    df_gecko = obtener_historico_coingecko(coin_id="tether", days=30)
    ruta_gecko = os.path.join(carpeta_data, "historico_tether.csv")
    df_gecko.to_csv(ruta_gecko, index=False)
    print(f"¡Guardado! -> {ruta_gecko}")
    
    print("\n🎉 ¡Proceso finalizado con éxito! Revisa la carpeta /Data en tu buscador de archivos.")