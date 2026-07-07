import pandas as pd
import os
import sqlite3

from src.funciones_criptos import ejecutar_pipeline_criptomonedas
from src.funciones_stable_coins import obtener_historico_defillama, calcular_metricas_anomalidad

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
            print("[CSV] Respaldo exportado correctamente en 'data/datos_preprocesados.csv'")
            
        else:
            print("[ALERTA] No se pudo procesar ninguna stablecoin.")
            
    except Exception as e:
        print(f"Ocurrió un error general en el flujo: {e}")

    
    
