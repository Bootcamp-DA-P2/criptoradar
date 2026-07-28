import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# ==================================
# CONFIGURACIÓN
# ==================================
st.set_page_config(layout="wide", page_title="Consultas SQL", page_icon="🗄️")

# ==================================
# CONEXIÓN A LA BASE DE DATOS (.env)
# ==================================
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

url_conexion = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
conn = st.connection("sql", type="sql", url=url_conexion)

# ==================================
# CARGAR DATOS GENERALES (Con Caché)
# ==================================

@st.cache_data(ttl=300)
def obtener_conteos():
    # Consultas rápidas para los KPIs
    conteo_crypto_precios = conn.query("SELECT COUNT(*) AS total FROM crypto_precios;").iloc[0]["total"]
    conteo_stable_preprocesados = conn.query("SELECT COUNT(*) AS total FROM preprocesados_historico;").iloc[0]["total"]
    total_cryptos = conn.query("SELECT COUNT(*) AS total FROM cryptos;").iloc[0]["total"]
    total_stables = conn.query("SELECT COUNT(*) AS total FROM stablecoins;").iloc[0]["total"]
    
    return conteo_crypto_precios, conteo_stable_preprocesados, total_cryptos, total_stables

# Cargar los contadores para los KPIs
reg_crypto, reg_stable, cant_cryptos, cant_stables = obtener_conteos()

# ==================================
# TÍTULO
# ==================================
st.title("🗄️ Base de Datos y Consultas SQL")

st.markdown("""
Esta sección muestra ejemplos de consultas SQL reales ejecutadas sobre la base de datos
relacional del proyecto **CriptoRadar**, mapeando el resultado directamente a DataFrames.
""")

st.divider()

# ==================================
# KPIs
# ==================================
c1, c2, c3, c4 = st.columns(4)

c1.metric("🪙 Registros Cripto Histórico", reg_crypto)
c2.metric("🛡 Registros Stablecoins Histórico", reg_stable)
c3.metric("📈 Criptomonedas Activas", cant_cryptos)
c4.metric("💵 Stablecoins Activas", cant_stables)

st.divider()

# ==================================
# CONSULTA 1: Precio promedio de criptos
# ==================================
st.subheader("Consulta 1: Precio promedio histórico de Criptomonedas")

query1 = """
SELECT 
    crypto_id, 
    AVG(close) AS precio_promedio 
FROM crypto_precios 
GROUP BY crypto_id;
"""

st.code(query1, language="sql")

# Ejecutar consulta en caliente
consulta1 = conn.query(query1)
st.dataframe(consulta1, use_container_width=True)


# ==================================
# CONSULTA 2: Desviación media de stablecoins
# ==================================
st.subheader("Consulta 2: Desviación media del Peg por Stablecoin")

query2 = """
SELECT 
    s.nombre_stablecoin AS stablecoin, 
    AVG(p.peg_deviation) AS desviacion_media 
FROM preprocesados_historico p
INNER JOIN stablecoins s ON p.stablecoin_id = s.stablecoin_id
GROUP BY s.nombre_stablecoin;
"""

st.code(query2, language="sql")

consulta2 = conn.query(query2)
st.dataframe(consulta2, use_container_width=True)


# ==================================
# CONSULTA 3: Máximos históricos de criptos
# ==================================
st.subheader("Consulta 3: Máximo valor histórico (High) registrado")

query3 = """
SELECT 
    crypto_id, 
    MAX(high) AS maximo_historico 
FROM crypto_precios 
GROUP BY crypto_id;
"""

st.code(query3, language="sql")

consulta3 = conn.query(query3)
st.dataframe(consulta3, use_container_width=True)


# ==================================
# CONSULTA 4: Market Cap máximo de stablecoins
# ==================================
st.subheader("Consulta 4: Capitalización de mercado máxima alcanzada")

query4 = """
SELECT 
    s.nombre_stablecoin AS stablecoin, 
    MAX(p.market_cap) AS market_cap_maximo 
FROM preprocesados_historico p
INNER JOIN stablecoins s ON p.stablecoin_id = s.stablecoin_id
GROUP BY s.nombre_stablecoin;
"""

st.code(query4, language="sql")

consulta4 = conn.query(query4)
st.dataframe(consulta4, use_container_width=True)

st.divider()

# ==================================
# MODELO RELACIONAL
# ==================================
st.subheader("📚 Modelo de Base de Datos")

st.info("""
La información obtenida desde las APIs se procesa mediante un pipeline ETL.

Posteriormente los datos limpios se almacenan en una base de datos MySQL,
desde donde pueden consultarse utilizando SQL para realizar análisis
estadísticos y alimentar dashboards como Streamlit.
""")