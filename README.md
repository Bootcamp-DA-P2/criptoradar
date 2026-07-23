# 📡 CriptoRadar

**Analítica de mercado cripto y vigilancia de stablecoins**

Proyecto Final — Data Analyst · Bootcamp FactoriaF5 · Madrid · 2026

🔗 Demo en producción: [criptoradar.up.railway.app](https://criptoradar.up.railway.app)

<img width="1575" height="831" alt="Captura de pantalla 2026-07-23 a las 12 35 49" src="https://github.com/user-attachments/assets/46bbad01-bd5c-41bd-933a-2675a6e016ec" />
<img width="1485" height="584" alt="Captura de pantalla 2026-07-23 a las 12 34 58" src="https://github.com/user-attachments/assets/2b274de7-cca3-430e-a064-f5d505eb4390" />
<img width="1438" height="572" alt="Captura de pantalla 2026-07-23 a las 12 37 02" src="https://github.com/user-attachments/assets/73e3ff78-a2c7-49a1-b620-d7e357fffaec" />


---

## 📖 Descripción general

CriptoRadar es una plataforma de analítica para criptoactivos que combina tres frentes con **datos abiertos**:

1. **Seguimiento del mercado cripto** — precios OHLCV, volatilidad y correlaciones entre los principales activos (Bitcoin, Ethereum, Ripple y Solana).
2. **Vigilancia de stablecoins** — detección de *depegs* (desviaciones del valor de referencia de 1$) mediante un sistema de detección de anomalías.
3. **Componente on-chain (opcional)** — análisis de gran volumen con SQL sobre datos públicos de blockchain (Google BigQuery).

El proyecto **no busca predecir el precio** —tarea poco fiable y de alto riesgo—, sino **vigilar el mercado, medir el riesgo y detectar comportamientos anómalos**. La idea clave: al vivir en la blockchain, estos datos son genuinamente abiertos.

> ⚠️ **Nota metodológica:** todos los análisis son descriptivos y exploratorios. CriptoRadar informa y vigila; **no emite recomendaciones de inversión ni predicciones de precio**.

---

## 🗂️ Índice

- [Arquitectura](#-arquitectura)
- [Fuentes de datos](#-fuentes-de-datos)
- [Stack tecnológico](#-stack-tecnológico)
- [Estructura de la base de datos](#-estructura-de-la-base-de-datos)
- [Sistema de detección de anomalías](#-sistema-de-detección-de-anomalías)
- [Principales hallazgos](#-principales-hallazgos-del-eda)
- [Modelado complementario (OLS vs. XGBoost)](#-modelado-complementario-ols-vs-xgboost)
- [Limitaciones](#-limitaciones)
- [Extensiones futuras](#-extensiones-futuras)
- [Referencias](#-referencias)

---

## 🏗️ Arquitectura

El flujo de datos sigue una arquitectura lineal:

```
Ingesta (Python: requests, pycoingecko)
        ↓
Almacenamiento y normalización (MySQL)
        ↓
Procesamiento (Pandas + scikit-learn, notebooks Jupyter)
        ↓
Presentación (App Streamlit desplegada en Railway)
```

**Alcance de datos monitorizados:**

| Métrica | Valor |
|---|---|
| Criptomonedas | 4 (BTC, ETH, XRP, SOL) |
| Stablecoins | 10 (USDT, USDC, DAI, USDE, PYUSD, FDUSD, USDD, FRAX, TUSD, BUSD) |
| Registros históricos | ~25.000 (2017–2026) |
| Niveles de alerta | 3 (Normal · Vigilancia · Mercado) |

---

## 🌐 Fuentes de datos

Datos abiertos y de acceso gratuito:

- **[CoinGecko API](https://docs.coingecko.com/)** (vía `pycoingecko`) — precios e históricos OHLCV, capitalización de mercado y metadatos de miles de criptoactivos.
- **[DefiLlama API](https://api-docs.defillama.com/)** (sin clave) — supply circulante de stablecoins, desviación del peg y TVL. Fuente central para la vigilancia de stablecoins.
- **[GeckoTerminal API](https://apiguide.geckoterminal.com/)** / Binance API pública — OHLCV de exchange y on-chain en tiempo casi real.
- **[Google BigQuery — Public Datasets](https://cloud.google.com/bigquery/public-data)** *(opcional / avanzado)* — datasets on-chain de Bitcoin y Ethereum (transacciones, gas, wallets). Requiere cuenta gratuita de Google Cloud.

---

## 🛠️ Stack tecnológico

- **Python** — Pandas, requests, pycoingecko
- **SQL** — series temporales de precios en MySQL; consultas on-chain opcionales en BigQuery
- **EDA** — análisis de retornos, volatilidad y correlaciones
- **Machine Learning** — Isolation Forest (detección de anomalías / depegs)
- **Modelado complementario** — regresión OLS y XGBoost Regressor
- **Pipeline** — ingesta programada por API
- **Excel** — KPIs e informes
- **Streamlit** — panel de mercado y monitor de stablecoins (desplegado en Railway)

---

## 🗃️ Estructura de la base de datos

Base de datos **MySQL** con las siguientes tablas principales:

- `Crypto_Precios`
- `Preprocesados_Historico`
- `Stablecoins`
- `Alertas_Sistema`
- `Alertas_Criticas`
- `Cryptos`

---

## 🚨 Sistema de detección de anomalías

El componente central del proyecto es el **sistema de alertas**, basado en un modelo **Isolation Forest** entrenado sobre las variables de comportamiento de cada stablecoin, cruzado con métricas de volatilidad del mercado cripto general.

### Niveles de alerta

| Nivel | Descripción |
|---|---|
| `0_normal` | Comportamiento dentro de parámetros históricos. Sin anomalía detectada y volatilidad de mercado baja. |
| `1_VIGILANCIA_STABLECOIN` | Anomalía detectada en la stablecoin individual, pero el mercado cripto general está tranquilo. Problema aislado. |
| `2_ALERTA_MERCADO` | Anomalía en la stablecoin **+** alta volatilidad de mercado. Señal de crisis sistémica. |

### Validación empírica

- La mediana de `peg_deviation` salta de ~10⁻³ (normal) a >10⁻² (vigilancia).
- `price_volatility_3d` se incrementa casi 100 veces entre estado normal y estados de alerta.
- El diferenciador clave entre niveles 1 y 2 es `market_volatility`: en Vigilancia el mercado está en calma (~0.02); en Alerta de Mercado se dispara (~0.07).

### Concentración de alertas por stablecoin

| Stablecoin | Vigilancia | Mercado | Total |
|---|---:|---:|---:|
| **BUSD** | 55 | 10 | **65** |
| USDE | 18 | 4 | 22 |
| FDUSD | 16 | 3 | 19 |
| PYUSD | 13 | 1 | 14 |
| USDD | 10 | 2 | 12 |
| FRAX | 6 | 1 | 7 |
| TUSD | 6 | 3 | 9 |
| USDC | 1 | 0 | 1 |
| **USDT** | 0 | 0 | **0** |

BUSD concentra casi el 50% de todas las alertas (su proceso de descontinuación explica la acumulación de señales), mientras que USDT presenta un historial impecable pese a ser el activo con mayor volumen transaccional.

---

## 📊 Principales hallazgos del EDA

- **El mercado cripto se mueve de forma correlacionada pero no homogénea.** Bitcoin–Ripple están casi sincronizados (r = 0.91), mientras que Ethereum–Ripple muestran independencia parcial (r = 0.36). La diversificación dentro de este universo tiene un efecto limitado en crisis sistémicas.
- **El tamaño de una stablecoin no garantiza su estabilidad.** PYUSD y USDE, con capitalizaciones menores, mantienen el peg con mayor precisión que monedas más grandes. El mecanismo de respaldo y la gestión del emisor son más determinantes que el market cap.
- **`peg_deviation` y `price_volatility_3d` son los dos ejes del riesgo de una stablecoin** (r = +0.55). Los desanclajes no son eventos puntuales: la volatilidad se sostiene en los días posteriores a la pérdida de paridad.
- **El sistema de alertas distingue con precisión** entre crisis aisladas (Vigilancia) y crisis sistémicas (Mercado), usando `market_volatility` como diferenciador clave.
- **BUSD es el caso de referencia de una descontinuación ordenada**: transición de estabilidad pre-anuncio a desviaciones sostenidas post-anuncio (picos de hasta el 12%), evidenciando cómo el mercado descuenta el riesgo de cierre de forma progresiva.

---

## 🔬 Modelado complementario: OLS vs. XGBoost

Análisis econométrico y de machine learning aplicado específicamente al riesgo de depeg de **USDT**, con variables rezagadas (`t-1`) para eliminar *look-ahead bias*.

| Métrica | OLS | XGBoost |
|---|---|---|
| R² ajustado / test | 0,366 | **0,53** |
| MAE (centavos) | 0,042 | **0,028** |
| Capacidad en extremos | Limitada | Alta |
| Interpretabilidad | Alta (coeficientes β) | Media (SHAP) |

**Conclusiones del modelado:**

- La **inercia del precio** (`D_t-1`) es el factor dominante en ambos modelos: el mercado necesita tiempo para arbitrar y devolver el precio a 1$.
- XGBoost captura un **efecto no lineal de la volatilidad de Bitcoin**: por debajo de cierto umbral no hay impacto, pero al cruzarlo el efecto sobre el depeg de USDT se dispara.
- La **liquidez interna** (`ln_vol_lag`) actúa como tercer factor, reflejando presión de los inversores por liquidez inmediata.
- El peg de USDT depende sobre todo de su propia inercia y liquidez interna, mostrándose mayoritariamente desvinculado de variables macroeconómicas tradicionales (tasas, DXY, VIX) en el periodo analizado.


---

## ⚠️ Limitaciones

- **Solapamiento temporal limitado**: el dataset de criptomonedas cubre 2024–2026, mientras que el de stablecoins arranca en 2017. DAI (activo desde 2017) no comparte días con el dataset cripto, impidiendo analizar su correlación con ETH (su colateral principal).
- **Rate limits de APIs gratuitas**: la ingesta histórica completa está condicionada por los límites de CoinGecko y DefiLlama sin clave de pago.
- **Calibración del Isolation Forest**: el umbral de anomalía se fijó sobre los datos disponibles; requiere reentrenamiento periódico.
- **Ausencia de datos on-chain**: el componente BigQuery queda como extensión futura, no forma parte del análisis actual.

---

## 🚀 Extensiones posibles

- Incorporar datos on-chain de Bitcoin y Ethereum vía Google BigQuery.
- Ampliar el universo de stablecoins (USDP, GUSD, crvUSD) y criptoactivos (BNB, ADA, MATIC).
- Modelo predictivo de depeg a 24–48h usando `supply_change` como señal adelantada.
- Análisis de sentimiento en redes sociales (Twitter/X, Reddit) correlacionado con las alertas del sistema.

---

## 📚 Referencias

- [CoinGecko API — Documentación](https://docs.coingecko.com/)
- [DefiLlama API](https://api-docs.defillama.com/)
- [GeckoTerminal API](https://apiguide.geckoterminal.com/)
- [pycoingecko (PyPI)](https://pypi.org/project/pycoingecko/)
- [scikit-learn — Detección de anomalías](https://scikit-learn.org/stable/modules/outlier_detection.html)
- [BigQuery Public Datasets](https://cloud.google.com/bigquery/public-data)
- [Streamlit — Documentación](https://docs.streamlit.io/)

