import streamlit as st

from src.view.icons import icon_heading, icon_md, icon_box

st.markdown(icon_heading("trending-up", "CriptoRadar", level=1), unsafe_allow_html=True)

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

    st.markdown(
        icon_box(
            "bar-chart",
            "**Dashboard Ejecutivo**\n\n"
            "Consulta indicadores generales del mercado:\n\n"
            "- KPIs principales\n"
            "- Evolución del precio\n"
            "- Volumen\n"
            "- Tendencias",
            kind="info",
        ),
        unsafe_allow_html=True,
    )

with col2:

    st.markdown(
        icon_box(
            "coin",
            "**Criptomonedas**\n\n"
            "Analiza:\n\n"
            "- Bitcoin\n"
            "- Ethereum\n"
            "- Ripple\n"
            "- Solana",
            kind="success",
        ),
        unsafe_allow_html=True,
    )

col3, col4 = st.columns(2)

with col3:

    st.markdown(
        icon_box(
            "shield",
            "**Stablecoins**\n\n"
            "Explora:\n\n"
            "- Peg\n"
            "- Market Cap\n"
            "- Supply\n"
            "- Volatilidad",
            kind="warning",
        ),
        unsafe_allow_html=True,
    )

with col4:

    st.markdown(
        icon_box(
            "alert",
            "**Alertas**\n\n"
            "Detecta automáticamente:\n\n"
            "- Pérdida del peg\n"
            "- Alta volatilidad\n"
            "- Cambios importantes",
            kind="error",
        ),
        unsafe_allow_html=True,
    )

st.divider()

st.markdown(icon_heading("tool", "Tecnologías utilizadas", level=3), unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

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

st.markdown(icon_heading("book", "Sobre el proyecto", level=3), unsafe_allow_html=True)

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
Desarrollado por:  **Rita Romero, Maria Bejarano, Ana Ganfornina , Miguel Angel Moreno**

Proyecto de Portfolio | Data Analytics Bootcamp | Python • SQL • Streamlit
"""
)