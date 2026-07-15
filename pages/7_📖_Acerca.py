import streamlit as st
from PIL import Image

from src.view.cargar_streamlit import cargar_crypto, cargar_stable

# =====================================
# CONFIGURACIÓN
# =====================================

st.set_page_config(
    page_title="Acerca del Proyecto",
    page_icon="📖",
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

    st.title("📖 Acerca del Proyecto")

    st.subheader("CriptoRadar")

    st.write(
        "Sistema de monitorización y análisis del mercado de criptomonedas y stablecoins."
    )

st.divider()

# =====================================
# RESUMEN DEL PROYECTO
# =====================================

st.header("📊 Resumen del Proyecto")

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
        "📄 Registros Crypto",
        f"{len(df_crypto):,}"
    )

with c4:

    st.metric(
        "📄 Registros Stable",
        f"{len(df_stable):,}"
    )

st.divider()

# =====================================
# OBJETIVO
# =====================================

st.header("🎯 Objetivo")

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

st.header("🏗 Arquitectura del Proyecto")

st.code("""
             🌐 APIs
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

st.header("🛠 Tecnologías Utilizadas")

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
🗄 Bases de Datos

• SQL

• MySQL
""")

with col3:

    st.success("""
☁ Herramientas

• Git

• GitHub

• APIs REST
""")

st.divider()

# =====================================
# FUNCIONALIDADES
# =====================================

st.header("🚀 Funcionalidades")

st.markdown("""
- ✅ Extracción automática desde la API de Bitget.
- ✅ Extracción automática desde la API de DefiLlama.
- ✅ Pipeline ETL desarrollado en Python.
- ✅ Limpieza y transformación de datos.
- ✅ Base de datos relacional en MySQL.
- ✅ Aplicación web desarrollada con Streamlit.
- ✅ Sistema automático de alertas.
- ✅ Consultas SQL para análisis.
- ✅ Análisis Exploratorio de Datos (EDA).
""")

st.divider()

# =====================================
# RESULTADOS
# =====================================

st.header("🏆 Resultados del Proyecto")

st.success("""
✔ Integración de múltiples fuentes de datos.

✔ Automatización del proceso ETL.

✔ Almacenamiento en MySQL.

✔ Dashboard profesional en Streamlit.

✔ Proyecto preparado para despliegue en la nube.
""")

st.divider()

# =====================================
# APRENDIZAJES
# =====================================

st.header("📚 Competencias Desarrolladas")

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

st.header("👩‍💻 Autores")

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

# st.header("📬 Contacto")

# st.info("""
# 💼 LinkedIn: (Añadir enlace)

# 💻 GitHub: (Añadir enlace)

# 📧 Email: (Añadir correo profesional)
# """)

# st.divider()

# st.success("🚀 Gracias por visitar CriptoRadar. ¡Espero que disfrutes explorando el proyecto!")