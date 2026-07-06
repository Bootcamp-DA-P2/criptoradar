import os
import time
import requests
import pandas as pd

# Mapeo de slugs internos -> par de trading en Bitget (siempre contra USDT = dólares)
SIMBOLOS_USDT = {
    "bitcoin": "BTCUSDT",
    "ethereum": "ETHUSDT",
    "solana": "SOLUSDT",
    "ripple": "XRPUSDT",
}

BASE_URL = "https://api.bitget.com/api/v2/spot/market/history-candles"


def _pedir_pagina(symbol, granularity, end_time_ms, limit=200, intentos=3):
    """Llama a la API de Bitget con reintentos básicos ante fallos de red/rate-limit."""
    params = {
        "symbol": symbol,
        "granularity": granularity,
        "endTime": end_time_ms,
        "limit": limit,
    }
    for intento in range(1, intentos + 1):
        try:
            resp = requests.get(BASE_URL, params=params, timeout=10)
            resp.raise_for_status()
            payload = resp.json()
            if payload.get("code") != "00000":
                raise ValueError(f"API respondió con error: {payload.get('msg')}")
            return payload.get("data", [])
        except Exception as e:
            print(f"   ⚠️ Intento {intento}/{intentos} falló ({e}). Reintentando...")
            time.sleep(1.5 * intento)
    raise RuntimeError(f"No se pudo obtener datos de Bitget para {symbol} tras {intentos} intentos.")


def descargar_historico_bitget(coin_id, carpeta_destino="data", granularity="1day", dias_historial=730):
    """
    Descarga el histórico OHLCV de una criptomoneda directamente desde la API
    pública de Bitget (contra USDT, es decir, en dólares) y lo guarda como Excel
    en `carpeta_destino`, con el mismo formato de columnas que espera el pipeline
    (timeClose, priceOpen, priceHigh, priceLow, priceClose, volume).

    No usa navegador ni Selenium, así que no hay riesgo de que la web muestre
    los precios en euros, ni de que cambie un botón de "exportar" en la interfaz.
    """
    if coin_id not in SIMBOLOS_USDT:
        raise ValueError(
            f"'{coin_id}' no está en el mapeo de símbolos. "
            f"Añádelo a SIMBOLOS_USDT con su par correspondiente (ej: 'BTCUSDT')."
        )

    symbol = SIMBOLOS_USDT[coin_id]
    print(f"🤖 [SCRAPER] Descargando histórico de {symbol} vía API pública de Bitget...")

    ahora_ms = int(time.time() * 1000)
    limite_antiguedad_ms = ahora_ms - dias_historial * 24 * 60 * 60 * 1000

    todas_las_velas = []
    end_time = ahora_ms
    pagina = 0

    while True:
        pagina += 1
        velas = _pedir_pagina(symbol, granularity, end_time_ms=end_time, limit=200)

        if not velas:
            break

        todas_las_velas.extend(velas)

        # La API devuelve velas en orden ascendente de tiempo; la más antigua es la primera
        timestamp_mas_antiguo = int(velas[0][0])

        print(f"   📄 Página {pagina}: {len(velas)} velas (hasta {pd.to_datetime(timestamp_mas_antiguo, unit='ms').date()})")

        if timestamp_mas_antiguo <= limite_antiguedad_ms or len(velas) < 200:
            break

        # Siguiente página: pedimos datos anteriores a la vela más antigua obtenida
        end_time = timestamp_mas_antiguo - 1
        time.sleep(0.15)  # margen de cortesía frente al rate-limit (20 req/s)

    if not todas_las_velas:
        raise RuntimeError(f"La API de Bitget no devolvió datos para {symbol}.")

    # Construcción del DataFrame con el formato que espera pipeline.py
    df = pd.DataFrame(
        todas_las_velas,
        columns=["timeClose", "priceOpen", "priceHigh", "priceLow", "priceClose",
                 "baseVol", "volume", "usdtVol"],
    )

    # Tipos correctos y eliminación de duplicados (por paginación solapada)
    df["timeClose"] = df["timeClose"].astype(int)
    for col in ["priceOpen", "priceHigh", "priceLow", "priceClose", "volume"]:
        df[col] = df[col].astype(float)

    df = df.drop_duplicates(subset="timeClose").sort_values("timeClose").reset_index(drop=True)
    df = df[["timeClose", "priceOpen", "priceHigh", "priceLow", "priceClose", "volume"]]

    os.makedirs(carpeta_destino, exist_ok=True)
    ruta_salida = os.path.join(carpeta_destino, f"{coin_id}_historico.xlsx")
    df.to_excel(ruta_salida, index=False)

    print(f"✨ [ÉXITO] {len(df)} registros guardados en {ruta_salida} (precios en USDT/USD).")
    return ruta_salida