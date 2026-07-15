import streamlit as st
from PIL import Image

from src.view.styles import cargar_css
from src.view.cargar_streamlit import cargar_crypto, cargar_stable

# =====================================
# CONFIGURACIÓN
# =====================================

st.set_page_config(
    page_title="CriptoRadar",
    page_icon="📈",
    layout="wide"
)

cargar_css()

# =====================================
# DATOS
# =====================================

df_crypto = cargar_crypto()
df_stable = cargar_stable()

logo = Image.open("app/assets/logo.png")

# =====================================
# CABECERA
# =====================================

col1, col2 = st.columns([1, 5])

with col1:
    st.image(logo, width=180)

with col2:

    st.title("📈 CriptoRadar")

    st.markdown("""
### Sistema Inteligente de Monitorización del Mercado Cripto

Analiza la evolución histórica de criptomonedas y stablecoins mediante
indicadores financieros, visualizaciones interactivas y alertas automáticas.

""")

st.divider()

# =====================================
# KPIs
# =====================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "🪙 Criptomonedas",
        df_crypto["crypto_id"].nunique()
    )

with c2:
    st.metric(
        "🛡 Stablecoins",
        df_stable["stablecoin"].nunique()
    )

with c3:
    st.metric(
        "📅 Registros Crypto",
        f"{len(df_crypto):,}"
    )

with c4:
    st.metric(
        "📅 Registros Stable",
        f"{len(df_stable):,}"
    )

st.divider()

# =====================================
# DESCRIPCIÓN
# =====================================

st.subheader("🎯 Objetivo del proyecto")

st.write("""
CriptoRadar es una aplicación desarrollada para monitorizar la evolución
del mercado de criptomonedas y stablecoins utilizando datos obtenidos desde
las APIs de **Bitget** y **DefiLlama**.

El proyecto permite explorar precios históricos, volumen de negociación,
capitalización de mercado, estabilidad del peg de las stablecoins y generar
visualizaciones interactivas para apoyar el análisis financiero.
""")

st.divider()

# =====================================
# TECNOLOGÍAS
# =====================================

st.subheader("🛠 Tecnologías utilizadas")

col1, col2, col3 = st.columns(3)

with col1:
    st.success("""
🐍 Python

• Pandas

• NumPy

• Plotly

• Streamlit
""")

with col2:
    st.success("""
🗄 Bases de datos

• MySQL

• SQL

• BigQuery
""")

with col3:
    st.success("""
☁ APIs

• Bitget

• DefiLlama

• Power BI

• GitHub
""")

st.divider()

# =====================================
# FLUJO
# =====================================

st.subheader("🔄 Flujo del proyecto")

st.info("""
📡 APIs (Bitget / DefiLlama)

⬇

🐍 Python

⬇

🧹 Limpieza de datos

⬇

🗄 MySQL

⬇

📊 Power BI

⬇

🌐 Streamlit
""")

st.divider()

st.success("✅ Selecciona una página en el menú lateral para comenzar el análisis.")