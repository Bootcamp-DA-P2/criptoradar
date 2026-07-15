import streamlit as st
import pandas as pd

from src.cargar_streamlit import cargar_crypto, cargar_stable

# ==================================
# CONFIGURACIÓN
# ==================================

st.set_page_config(layout="wide")

# ==================================
# CARGAR DATOS
# ==================================

df_crypto = cargar_crypto()
df_stable = cargar_stable()

# ==================================
# TÍTULO
# ==================================

st.title("🗄️ Base de Datos y Consultas SQL")

st.markdown("""
Esta sección muestra ejemplos de consultas SQL que pueden realizarse sobre la base de datos
relacional creada para el proyecto **CriptoRadar**.
""")

st.divider()

# ==================================
# KPIs
# ==================================

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "🪙 Registros Cripto",
    len(df_crypto)
)

c2.metric(
    "🛡 Registros Stablecoins",
    len(df_stable)
)

c3.metric(
    "📈 Criptomonedas",
    df_crypto["crypto_id"].nunique()
)

c4.metric(
    "💵 Stablecoins",
    df_stable["stablecoin"].nunique()
)

st.divider()

# ==================================
# CONSULTA 1
# ==================================

st.subheader("Consulta 1")

st.code("""
SELECT
    crypto_id,
    AVG(close) AS precio_promedio
FROM cryptos
GROUP BY crypto_id;
""", language="sql")

consulta1 = (
    df_crypto
    .groupby("crypto_id")["close"]
    .mean()
    .reset_index()
)

st.dataframe(
    consulta1,
    use_container_width=True
)

# ==================================
# CONSULTA 2
# ==================================

st.subheader("Consulta 2")

st.code("""
SELECT
    stablecoin,
    AVG(peg_deviation) AS desviacion_media
FROM stablecoins
GROUP BY stablecoin;
""", language="sql")

consulta2 = (
    df_stable
    .groupby("stablecoin")["peg_deviation"]
    .mean()
    .reset_index()
)

st.dataframe(
    consulta2,
    use_container_width=True
)

# ==================================
# CONSULTA 3
# ==================================

st.subheader("Consulta 3")

st.code("""
SELECT
    crypto_id,
    MAX(high) AS maximo_historico
FROM cryptos
GROUP BY crypto_id;
""", language="sql")

consulta3 = (
    df_crypto
    .groupby("crypto_id")["high"]
    .max()
    .reset_index()
)

st.dataframe(
    consulta3,
    use_container_width=True
)

# ==================================
# CONSULTA 4
# ==================================

st.subheader("Consulta 4")

st.code("""
SELECT
    stablecoin,
    MAX(market_cap) AS market_cap_maximo
FROM stablecoins
GROUP BY stablecoin;
""", language="sql")

consulta4 = (
    df_stable
    .groupby("stablecoin")["market_cap"]
    .max()
    .reset_index()
)

st.dataframe(
    consulta4,
    use_container_width=True
)

st.divider()

# ==================================
# MODELO RELACIONAL
# ==================================

st.subheader("📚 Modelo de Base de Datos")

st.info("""
La información obtenida desde las APIs se procesa mediante un pipeline ETL.

Posteriormente los datos limpios se almacenan en una base de datos MySQL,
desde donde pueden consultarse utilizando SQL para realizar análisis
estadísticos y alimentar dashboards como Power BI y Streamlit.
""")