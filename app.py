import pandas as pd
import os

# IMPORTACIÓN MODULAR
from scrapers.bitget_scraper import descargar_historico_bitget


def ejecutar_pipeline_criptomonedas():
    """
    Orquestador del pipeline de criptomonedas.
    Descarga (vía API de Bitget), limpia y unifica verticalmente las monedas.
    Genera un CSV final con columnas: fecha, crypto_id, open, high, low, close, volume
    """
    print("\n" + "=" * 50)
    print("🚀 INICIANDO PIPELINE DE UNIFICACIÓN DE CRIPTOMONEDAS")
    print("=" * 50)

    os.makedirs("data", exist_ok=True)

    diccionario_cryptos = {
        'bitcoin': 'bitcoin',
        'ethereum': 'ethereum',
        'solana': 'solana',
        'ripple': 'ripple',
    }

    lista_dataframes_limpios = []

    for nombre_interno, slug_url in diccionario_cryptos.items():
        print(f"\n[PROCESANDO] -> {nombre_interno.upper()}")

        try:
            # A. El scraper descarga y devuelve la ruta exacta del archivo generado
            ruta_archivo = descargar_historico_bitget(coin_id=slug_url, carpeta_destino="data")

            print(f"📁 Leyendo y transformando: {ruta_archivo}")
            df_bruto = pd.read_excel(ruta_archivo)

            # B. Formatea la fecha a texto (YYYY-MM-DD)
            df_bruto['fecha'] = pd.to_datetime(df_bruto['timeClose'], unit='ms').dt.date.astype(str)

            # C. Renombra las columnas al estándar OHLC
            df_limpio = df_bruto.rename(columns={
                'priceOpen': 'open',
                'priceHigh': 'high',
                'priceLow': 'low',
                'priceClose': 'close',
                'volume': 'volume',  # ya viene con este nombre desde el scraper
            })

            # D. Asigna el nombre estándar como ID del registro
            df_limpio['crypto_id'] = nombre_interno

            # E. Filtra y ordena columnas: fecha, crypto_id, open, high, low, close, volume
            df_final_moneda = df_limpio[['fecha', 'crypto_id', 'open', 'high', 'low', 'close', 'volume']]

            lista_dataframes_limpios.append(df_final_moneda)
            print(f"✅ {nombre_interno} procesado correctamente ({len(df_final_moneda)} registros).")

            # Eliminamos el Excel temporal
            os.remove(ruta_archivo)

        except Exception as e:
            print(f"❌ [ERROR] Falló el procesamiento de {nombre_interno}: {e}")
            continue

    if len(lista_dataframes_limpios) > 0:
        print("\n[MÓDULO FINAL] Combinando las monedas en un único dataset...")
        df_todas_cryptos = pd.concat(lista_dataframes_limpios, ignore_index=True)

        ruta_resultado = "data/criptoradar_crypto_final.csv"
        df_todas_cryptos.to_csv(ruta_resultado, index=False)

        print("\n" + "=" * 50)
        print("¡PIPELINE COMPLETADO CON ÉXITO! 🏁")
        print(f"📍 Archivo final generado: {ruta_resultado}")
        print(f"📊 Total de filas acumuladas: {len(df_todas_cryptos)}")
        print("=" * 50)

        return df_todas_cryptos
    else:
        print("\n❌ [ERROR CRÍTICO] No se pudo unificar ninguna criptomoneda.")
        return None


if __name__ == "__main__":
    ejecutar_pipeline_criptomonedas()