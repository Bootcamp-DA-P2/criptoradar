import pandas as pd
import os

from src.funciones_criptos import ejecutar_pipeline_criptomonedas
from src.funciones_stable_coins import obtener_historico_defillama, calcular_metricas_anomalidad
from src.analisis_alertas import ejecutar_pipeline_alertas
from utils.clean_function import ejecutar_pipeline_limpieza
from src.carga_datos import crear_base_de_datos_si_not_exists, cargar_datos_desde_env

# --- BLOQUE PRINCIPAL DE EJECUCIÓN ---
if __name__ == "__main__":
    try:
        # 1. Ejecutar el pipeline de criptomonedas (Bitget)
        ejecutar_pipeline_criptomonedas()

        stablecoins_radar = {
            1: "USDT", 2: "USDC", 3: "DAI", 4: "BUSD", 5: "FDUSD",
            6: "TUSD", 7: "USDD", 8: "FRAX", 9: "PYUSD", 10: "USDE"
        }
        
        datasets_procesados = []
        
        # 2. Ejecutar la extracción de Stablecoins (DefiLlama)
        for id_coin, nombre_coin in stablecoins_radar.items():
            print(f"\n=========================================")
            print(f"PROCESANDO: {nombre_coin} (ID: {id_coin})")
            print(f"=========================================")
            
            try:
                df_stable = obtener_historico_defillama(stablecoin_id=id_coin, nombre_coin=nombre_coin)
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

            # Mantenemos la copia en CSV como respaldo
            df_radar_completo.to_csv("data/datos_preprocesados.csv")
            print("[CSV] Respaldo exportado correctamente en 'data/datos_preprocesados.csv'")
            
            # Ejecucción limpieza 

            RUTA_CRYPTOS_RAW = "data/criptoradar_crypto_final.csv"
            RUTA_STABLES_RAW = "data/datos_preprocesados.csv"
            
            try:
                ejecutar_pipeline_limpieza(
                    ruta_cryptos_in=RUTA_CRYPTOS_RAW, 
                    ruta_stables_in=RUTA_STABLES_RAW,
                    carpeta_destino="data/clean"
                )
            except Exception as e:
                print(f"\n❌ Hubo un error durante la ejecución del pipeline: {e}")



            #Ejecución del sistema de alertas
            ejecutar_pipeline_alertas()

            # =================================================================
            # === NUEVO: PERSISTENCIA Y CREACIÓN DE ESQUEMA EN MYSQL ===
            # =================================================================
            print("\n=========================================")
            print("🗄️ INICIANDO EXPORTACIÓN A BASE DE DATOS RELACIONAL (MYSQL)")
            print("=========================================")
            try:
                # Lee tu creacion_database.sql (desde la carpeta configurada) y crea la DB si no existe
                crear_base_de_datos_si_not_exists()
                
                # Lee los CSV finales e inserta los datos respetando las claves foráneas
                cargar_datos_desde_env()
                print("=========================================\n")
            except Exception as mysql_err:
                print(f"❌ Error durante el volcado a MySQL: {mysql_err}")
                print("=========================================\n")
            
        else:
            print("[ALERTA] No se pudo procesar ninguna stablecoin. Se cancela el módulo de alertas.")
            
    except Exception as e:
        print(f"Ocurrió un error general en el flujo: {e}")