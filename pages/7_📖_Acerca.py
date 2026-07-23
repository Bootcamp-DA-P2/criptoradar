import streamlit as st
from PIL import Image

from src.view.cargar_streamlit import cargar_crypto, cargar_stable
from src.view.icons import icon_heading, icon_box, metric_html

# =====================================
# CONFIGURACIÓN
# =====================================

st.set_page_config(
    page_title="Acerca del Proyecto",
    layout="wide"
)

# =====================================
# CARGAR DATOS
# =====================================

df_crypto = cargar_crypto()
df_stable = cargar_stable()

logo = Image.open("app/assets/logo.png")

# =====================================
# CABECERA
# =====================================

col1, col2 = st.columns([1,4])

with col1:
    st.image(logo, width=170)

with col2:

    st.markdown(icon_heading("book-open", "Acerca del Proyecto", level=1), unsafe_allow_html=True)

    st.subheader("CriptoRadar")

    st.write(
        "Sistema de monitorización y análisis del mercado de criptomonedas y stablecoins."
    )

st.divider()

# =====================================
# RESUMEN DEL PROYECTO
# =====================================

st.markdown(icon_heading("bar-chart", "Resumen del Proyecto", level=2), unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(metric_html("coin", "Criptomonedas", str(df_crypto["crypto_id"].nunique())), unsafe_allow_html=True)

with c2:
    st.markdown(metric_html("shield", "Stablecoins", str(df_stable["stablecoin"].nunique())), unsafe_allow_html=True)

with c3:
    st.markdown(metric_html("document", "Registros Crypto", f"{len(df_crypto):,}"), unsafe_allow_html=True)

with c4:
    st.markdown(metric_html("document", "Registros Stable", f"{len(df_stable):,}"), unsafe_allow_html=True)

st.divider()

# =====================================
# OBJETIVO
# =====================================

st.markdown(icon_heading("target", "Objetivo", level=2), unsafe_allow_html=True)

st.write("""
CriptoRadar es una aplicación desarrollada para monitorizar el comportamiento
del mercado de criptomonedas y stablecoins mediante la extracción automática
de datos desde APIs públicas, su procesamiento, almacenamiento y
visualización interactiva.

El proyecto permite analizar la evolución histórica de los activos digitales,
identificar tendencias, detectar desviaciones del peg en stablecoins y
facilitar la toma de decisiones mediante dashboards dinámicos.
""")

st.divider()

# =====================================
# ARQUITECTURA
# =====================================

st.markdown(icon_heading("link", "Arquitectura del Proyecto", level=2), unsafe_allow_html=True)

st.code("""
             APIs
   Bitget              DefiLlama
       │                   │
       └─────────┬─────────┘
                 ▼
          Extracción de datos
                 ▼
         Limpieza y Transformación
                 ▼
              Python ETL
                 ▼
               MySQL
                 ▼
             Streamlit
""")

st.divider()

# =====================================
# TECNOLOGÍAS
# =====================================

st.markdown(icon_heading("tool", "Tecnologías Utilizadas", level=2), unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        icon_box(
            "laptop",
            "**Python**\n\n• Pandas\n\n• NumPy\n\n• Plotly\n\n• Streamlit",
            kind="success",
        ),
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        icon_box(
            "database",
            "**Bases de Datos**\n\n• SQL\n\n• MySQL",
            kind="success",
        ),
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        icon_box(
            "cloud",
            "**Herramientas**\n\n• Git\n\n• GitHub\n\n• APIs REST",
            kind="success",
        ),
        unsafe_allow_html=True,
    )

st.divider()

# =====================================
# FUNCIONALIDADES
# =====================================

st.markdown(icon_heading("check-circle", "Funcionalidades", level=2), unsafe_allow_html=True)

funcionalidades = [
    "Extracción automática desde la API de Bitget.",
    "Extracción automática desde la API de DefiLlama.",
    "Pipeline ETL desarrollado en Python.",
    "Limpieza y transformación de datos.",
    "Base de datos relacional en MySQL.",
    "Aplicación web desarrollada con Streamlit.",
    "Sistema automático de alertas.",
    "Consultas SQL para análisis.",
    "Análisis Exploratorio de Datos (EDA).",
]

for f in funcionalidades:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:0.5em;margin:0.25em 0;">'
        f'{icon("check", size=16, color="#2ecc71")}<span>{f}</span></div>',
        unsafe_allow_html=True,
    )

st.divider()

# =====================================
# RESULTADOS
# =====================================

st.markdown(icon_heading("trophy", "Resultados del Proyecto", level=2), unsafe_allow_html=True)

st.markdown(
    icon_box(
        "check",
        "Integración de múltiples fuentes de datos.\n\n"
        "Automatización del proceso ETL.\n\n"
        "Almacenamiento en MySQL.\n\n"
        "Dashboard profesional en Streamlit.\n\n"
        "Proyecto preparado para despliegue en la nube.",
        kind="success",
    ),
    unsafe_allow_html=True,
)

st.divider()

# =====================================
# APRENDIZAJES
# =====================================

st.markdown(icon_heading("book", "Competencias Desarrolladas", level=2), unsafe_allow_html=True)

st.markdown("""
Durante el desarrollo de CriptoRadar se aplicaron conocimientos relacionados con:

- Extracción de datos mediante APIs REST.
- Procesos ETL.
- Limpieza y transformación de datos.
- Análisis Exploratorio de Datos (EDA).
- Modelado de bases de datos relacionales.
- Consultas SQL.
- Visualización interactiva con Plotly.
- Desarrollo de aplicaciones con Streamlit.
- Control de versiones con Git y GitHub.
""")

st.divider()

# =====================================
# AUTORA
# =====================================

st.markdown(icon_heading("user", "Autores", level=2), unsafe_allow_html=True)

st.write("""
**Rita Romero, Ana Ganfornina, Maria Bejarano y Miguel Angel Moreno**

Data Analyst Junior

Proyecto desarrollado como portfolio para demostrar habilidades en
extracción, procesamiento, análisis y visualización de datos utilizando
Python, SQL, MySQL y Streamlit.
""")

# st.divider()

# =====================================
# CONTACTO
# =====================================

# st.header("Contacto")

# st.info("""
# LinkedIn: (Añadir enlace)
#
# GitHub: (Añadir enlace)
#
# Email: (Añadir correo profesional)
# """)

# st.divider()

# st.success("Gracias por visitar CriptoRadar. ¡Espero que disfrutes explorando el proyecto!")