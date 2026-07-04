import pandas as pd
import os
from Network.api import extraer_stablecoins_con_desviacion, get_coingecko_data

def ejecutar_pipeline_datos():
    os.makedirs("Data", exist_ok=True)
    print("=== INICIANDO PIPELINE DE DATA EXTRACTION ===")
    
    # 1. Ejecutar las extracciones
    df_stables = extraer_stablecoins_con_desviacion()
    df_crypto = get_coingecko_data()
    
    # Validamos que ambas extracciones tengan registros
    if df_stables is not None and df_crypto is not None:
        print("\n=== COMBINANDO FUENTES DE DATOS ===")
        
        # ⚙️ Aseguramos que la columna 'fecha' sea exactamente del mismo tipo (texto) en ambos lados
        df_crypto['fecha'] = df_crypto['fecha'].astype(str)
        df_stables['fecha'] = df_stables['fecha'].astype(str)
        
        # 2. EL MERGE: Al unir un formato largo con el de stablecoins, Pandas asociará
        # los datos de las stablecoins a cada una de las filas de las 5 criptos para esa fecha.
        df_consolidado = pd.merge(df_crypto, df_stables, on="fecha", how="inner")
        
        # 3. Guardamos el dataset final listo para devorarlo en Power BI
        ruta_final = "criptoradar_dataset_final.csv"
        df_consolidado.to_csv(ruta_final, index=False)
        
        print(f"¡Pipeline completado con éxito!")
        print(f"Dataset unificado guardado en: {ruta_final}")
        print(f"Número total de registros generados: {len(df_consolidado)}")
        print("\nMuestra del dataset combinado (Formato Largo):")
        print(df_consolidado.head())
        
        return df_consolidado
    else:
        print("\n[ERROR] El pipeline falló porque una de las fuentes devolvió None.")
        return None

if __name__ == "__main__":
    # Esto asegura que el pipeline solo se ejecute si lanzas este archivo directamente
    ejecutar_pipeline_datos()