import pandas as pd
# Importamos las funciones desde el archivo donde las hayas guardado
# (Asumiendo que guardaste las funciones anteriores en un archivo llamado 'extractores.py')
from Network.api import extraer_stablecoins_con_desviacion, extraer_y_guardar_coingecko

def ejecutar_pipeline_datos():
    print("=== INICIANDO PIPELINE DE DATA EXTRACTION ===")
    
    # 1. Ejecutar las extracciones y guardar los CSVs individuales
    df_stables = extraer_stablecoins_con_desviacion()
    df_crypto = extraer_y_guardar_coingecko(coin_id="bitcoin", days="180", ruta_csv="data_bitcoin.csv")
    
    # Validamos que ambas extracciones hayan devuelto datos correctamente
    if df_stables is not None and df_crypto is not None:
        print("\n=== COMBINANDO FUENTES DE DATOS ===")
        
        # 2. EL TRUCO DEL MERGE: Unimos ambos DataFrames usando la 'fecha' como llave común.
        # Usamos 'inner' para asegurar que solo se queden los días que existen en ambas fuentes.
        df_consolidado = pd.merge(df_crypto, df_stables, on="fecha", how="inner")
        
        # 3. Guardamos el dataset final listo para el análisis o Power BI
        ruta_final = "criptoradar_dataset_final.csv"
        df_consolidado.to_csv(ruta_final, index=False)
        
        print(f"¡Pipeline completado con éxito!")
        print(f"Dataset unificado guardado en: {ruta_final}")
        print("\nMuestra del dataset combinado:")
        print(df_consolidado.head())
        
        return df_consolidado
    else:
        print("\n[ERROR] El pipeline falló porque una de las fuentes no devolvió datos.")
        return None

if __name__ == "__main__":
    # Esto asegura que el pipeline solo se ejecute si lanzas este archivo directamente
    ejecutar_pipeline_datos()