import pandas as pd
import numpy as np
import os
from sklearn.ensemble import IsolationForest

def ejecutar_pipeline_alertas():
    print("\n" + "="*50)
    print("🧠 INICIANDO MODELO DE ALERTAS Y ANOMALÍAS (ISOLATION FOREST)")
    print("="*50)

    # 1. CARGAR Y PREPARAR LOS DATOS
    ruta_cryptos = "data/criptoradar_crypto_final_clean.csv"
    ruta_stables = "data/datos_preprocesados_clean.csv"

    if not os.path.exists(ruta_cryptos) or not os.path.exists(ruta_stables):
        print("❌ [ERROR] No se encontraron los archivos necesarios en 'data/'. Ejecuta primero el pipeline de extracción.")
        return

    print("📁 Cargando datasets...")
    df_cryptos = pd.read_csv(ruta_cryptos)
    df_stables = pd.read_csv(ruta_stables)

    df_cryptos['datetime'] = pd.to_datetime(df_cryptos['datetime'])
    df_stables['datetime'] = pd.to_datetime(df_stables['datetime'])

    # 2. CALCULAR EL RETORNO DIARIO DE CADA CRIPTO
    print("📈 Calculando retornos diarios de criptomonedas...")
    df_cryptos = df_cryptos.sort_values(by=['crypto_id', 'datetime'])
    df_cryptos['daily_return'] = df_cryptos.groupby('crypto_id')['close'].pct_change() # porcentaje de cambio
    
    # Eliminar filas sin retorno (el primer día de historial de cada una)
    df_cryptos = df_cryptos.dropna(subset=['daily_return'])

    # 3. CONSTRUIR EL ÍNDICE AGREGADO DE VOLATILIDAD DE MERCADO
    print("📊 Calculando índice agregado de volatilidad de mercado...")
    # Calculamos el valor absoluto del retorno diario
    df_cryptos['abs_return'] = df_cryptos['daily_return'].abs()
    # Agrupamos por fecha y sacamos la media (un solo número por día que representa el movimiento promedio)
    df_mercado = df_cryptos.groupby('datetime')['abs_return'].mean().reset_index()
    df_mercado = df_mercado.rename(columns={'abs_return': 'market_volatility'})

    # 4. DEFINIR EL UMBRAL DE "MERCADO EN ESTRÉS"
    percentil = 90
    umbral_estres = np.percentile(df_mercado['market_volatility'], percentil)
    df_mercado['market_stress'] = df_mercado['market_volatility'] > umbral_estres
    print(f"⚖️ Umbral de estrés de mercado (Percentil {percentil}): {umbral_estres:.4f}")
    print(f"🔥 Días de mercado bajo estrés detectados: {df_mercado['market_stress'].sum()}")

    #---------ESTO SERÁ ELIMINADO UNIR CON EL MODELO DE MARIA------------------
    # 5. ENTRENAR EL ISOLATION FOREST POR STABLECOIN
    print("🤖 Entrenando Isolation Forest de forma independiente por Stablecoin...")
    features = ['peg_deviation', 'price_volatility_3d', 'supply_change_1d', 'supply_change_7d']
    
    lista_stables_con_anomalias = []
    
    # Agrupamos por stablecoin para que el modelo entienda el comportamiento único de cada una
    for nombre_stable, grupo in df_stables.groupby('stablecoin'):
        grupo = grupo.copy()
        
        # Inicializamos y entrenamos el modelo
        # contamination=0.05 asume que históricamente un 5% de los datos pueden ser anomalías
        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(grupo[features])
        
        # Guardamos métricas (-1 es anomalía, 1 es normal en scikit-learn)
        grupo['anomaly_score'] = model.decision_function(grupo[features])
        predicciones = model.predict(grupo[features])
        grupo['is_anomaly_stablecoin'] = predicciones == -1  # True si es anomalía
        
        lista_stables_con_anomalias.append(grupo)
        
    df_stables_anomalas = pd.concat(lista_stables_con_anomalias)
    

    # 6. UNIR LAS DOS SEÑALES POR FECHA
    print("🔗 Fusionando señales de Stablecoins y Estrés de Mercado...")
    df_alertas = pd.merge(df_stables_anomalas, df_mercado, on='datetime', how='inner')

    # 7. CALCULAR EL NIVEL DE ALERTA (Matriz de Decisiones)
    print("🚨 Evaluando niveles de alerta analíticos...")
    condiciones = [
        (df_alertas['is_anomaly_stablecoin'] == True) & (df_alertas['market_stress'] == True),
        (df_alertas['is_anomaly_stablecoin'] == True) & (df_alertas['market_stress'] == False)
    ]
    resultados = ['2_ALERTA_MERCADO', '1_VIGILANCIA_STABLECOIN']
    
    df_alertas['nivel_alerta'] = np.select(condiciones, resultados, default='0_normal')

    # 8. GUARDAR Y REVISAR TABLA GLOBAL DE ALERTAS
    ruta_alertas_csv = "data/alertas_sistema_final.csv"
    df_alertas.to_csv(ruta_alertas_csv, index=False)
    print(f"💾 Guardado resumen de alertas en: {ruta_alertas_csv}")
    print("\n📊 Resumen de filas por nivel de alerta:")
    print(df_alertas['nivel_alerta'].value_counts())

    # =====================================================================
    # DESGLOSE DE DETALLE POR CRIPTO (USANDO FORMATO ANCHO)
    # =====================================================================
    print("\n" + "-"*30)
    print("🔍 INICIANDO DESGLOSE DE DETALLE POR CRIPTO (OPCIÓN A)")
    print("-"*30)

    # 9. Reconstruir/pivotar los datos de criptomonedas para tener formato ancho por fecha
    # Esto pasará de formato largo a tener columnas: btc_return, eth_return, etc.
    df_cryptos_pivot = df_cryptos.pivot(index='datetime', columns='crypto_id', values='daily_return').reset_index()
    df_cryptos_pivot = df_cryptos_pivot.rename(columns={
        'bitcoin': 'btc_return',
        'ethereum': 'eth_return',
        'solana': 'sol_return',
        'ripple': 'xrp_return'
    })

    # 10. Unir el desglose de retornos a nuestra tabla de alertas
    df_alertas_detalladas = pd.merge(df_alertas, df_cryptos_pivot, on='datetime', how='left')

    # 11, 12 y 13. Filtrar y documentar de forma automática las alertas críticas
    df_criticas = df_alertas_detalladas[df_alertas_detalladas['nivel_alerta'] == '2_ALERTA_MERCADO'].copy()

    if not df_criticas.empty:
        print(f"📢 Generando narrativa automática para las {len(df_criticas)} alertas críticas encontradas...")
        
        frases_documentacion = []
        columnas_criptos = ['btc_return', 'eth_return', 'sol_return', 'xrp_return']
        nombres_limpios = {'btc_return': 'Bitcoin', 'eth_return': 'Ethereum', 'sol_return': 'Solana', 'xrp_return': 'Ripple'}

        for idx, fila in df_criticas.iterrows():
            # Encontrar cuál cripto tuvo el movimiento absoluto más brusco ese día
            valores_retornos = [abs(fila[col]) if pd.notnull(fila[col]) else 0 for col in columnas_criptos]
            indice_max = np.argmax(valores_retornos)
            col_max = columnas_criptos[indice_max]
            
            cripto_lider = nombres_limpios[col_max]
            retorno_lider_pct = fila[col_max] * 100

            fecha_str = fila['datetime'].strftime('%Y-%m-%d')
            frase = (f"El {fecha_str}, {fila['stablecoin']} se desvió {fila['peg_deviation']:.4f} de su paridad, "
                    f"coincidiendo con un mercado en estrés liderado por un movimiento en {cripto_lider} del {retorno_lider_pct:.2f}%.")
            frases_documentacion.append(frase)

        df_criticas['narrativa_alerta'] = frases_documentacion
        
        # Guardamos las alertas críticas con su explicación textual
        ruta_criticas_csv = "data/alertas_criticas_informe.csv"
        df_criticas.to_csv(ruta_criticas_csv, index=False)
        print(f"🎯 ¡Éxito! Informe con narrativas guardado en: {ruta_criticas_csv}")
        
        print("\n📝 EJEMPLOS DE ALERTAS CRÍTICAS DETECTADAS:")
        for ejemplo in frases_documentacion[:3]:
            print(f"👉 {ejemplo}")
    else:
        print("💡 No se detectaron alertas críticas de nivel '2_ALERTA_MERCADO' con la configuración actual.")

    print("\n" + "="*50)
    print("🏁 PIPELINE DE ANÁLISIS COMPLETADO")
    print("="*50)