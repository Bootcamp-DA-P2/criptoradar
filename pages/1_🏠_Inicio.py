import streamlit as st

st.title("📈 CriptoRadar")

st.subheader("Plataforma de análisis del mercado de criptomonedas y stablecoins")

st.markdown("""
Bienvenido a **CriptoRadar**, una aplicación desarrollada para analizar la evolución
del mercado de criptomonedas y stablecoins mediante indicadores financieros,
visualizaciones interactivas y sistemas de alertas.

El objetivo es facilitar el análisis del comportamiento del mercado y apoyar
la toma de decisiones basadas en datos.
""")

st.divider()

col1, col2 = st.columns(2)

with col1:

    st.info("""
### 📊 Dashboard Ejecutivo

Consulta indicadores generales del mercado:

- KPIs principales
- Evolución del precio
- Volumen
- Tendencias
""")

with col2:

    st.success("""
### 🪙 Criptomonedas

Analiza:

- Bitcoin
- Ethereum
- Ripple
- Solana
""")
    
col3, col4 = st.columns(2)

with col3:

    st.warning("""
### 🛡 Stablecoins

Explora:

- Peg
- Market Cap
- Supply
- Volatilidad
""")

with col4:

    st.error("""
### 🚨 Alertas

Detecta automáticamente:

- Pérdida del peg
- Alta volatilidad
- Cambios importantes
""")
    
st.divider()

st.subheader("🛠 Tecnologías utilizadas")

col1,col2,col3 = st.columns(3)

with col1:
    st.markdown("""
- Python
- Pandas
- NumPy
- Plotly
""")

with col2:
    st.markdown("""
- SQL
- MySQL
- Streamlit
- Git
""")

with col3:
    st.markdown("""
- APIs Bitget
- DefiLlama
- Visual Studio Code
- GitHub
""")
    
st.divider()

st.subheader("📚 Sobre el proyecto")

st.write("""
CriptoRadar fue desarrollado como proyecto de análisis de datos con el objetivo
de construir un dashboard interactivo para estudiar el comportamiento histórico
de criptomonedas y stablecoins.

La aplicación integra procesos ETL, análisis exploratorio de datos (EDA),
visualizaciones interactivas y un sistema de alertas basado en indicadores financieros.
""")

st.divider()

st.caption(
"""
Desarrollado por:  **Rita, Maria, Ana y Miguel**

Proyecto de Portfolio | Data Analytics Bootcamp | Python • SQL • Streamlit
"""
)
