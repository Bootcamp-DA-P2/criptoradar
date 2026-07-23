import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine
from pathlib import Path
import os

from src.view.icons import icon_heading, icon_md, icon_box, metric_html, icon

# ==================================
# CONFIGURACIÓN
# ==================================

st.set_page_config(
    page_title="Centro de Alertas",
    layout="wide"
)

# ==================================
# CONEXIÓN A LA BASE DE DATOS
# ==================================

# Creamos la conexión. 
# Si usas SQLite local, busca un archivo llamado "alertas.db" en tu proyecto.
# Para PostgreSQL/MySQL, consulta la sección de notas abajo.
# ==================================
# CONEXIÓN A LA BASE DE DATOS (.env)
# ==================================

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")

# Acepta ambos nombres por compatibilidad
DB_PASS = os.getenv("DB_PASS")

required = {
    "DB_HOST": DB_HOST,
    "DB_PORT": DB_PORT,
    "DB_NAME": DB_NAME,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASS,
}

missing = [k for k, v in required.items() if not v]

if missing:
    st.error(f"Faltan variables en el .env: {', '.join(missing)}")
    st.stop()

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Función para cargar los datos con caché para optimizar el rendimiento
@st.cache_data(ttl=300)  # Expira la caché cada 5 minutos
def cargar_datos_desde_db():
    # Hacemos un JOIN para juntar la alerta con el nombre de la stablecoin
    # y traer el precio e histórico de desviación correspondiente a esa fecha
    query = """
        SELECT 
            a.datetime,
            s.nombre_stablecoin AS stablecoin,
            COALESCE(p.price, 1.0) AS price,
            COALESCE(p.peg_deviation, 0.0) AS peg_deviation,
            a.market_volatility,
            a.anomaly_score,
            a.nivel_alerta
        FROM alertas_sistema a
        INNER JOIN stablecoins s ON a.stablecoin_id = s.stablecoin_id
        LEFT JOIN preprocesados_historico p 
            ON a.stablecoin_id = p.stablecoin_id AND a.datetime = p.datetime;
    """
    df_db = engine.query(query)

    # Forzar minúsculas en las columnas para asegurar coincidencia con el resto del script
    df_db.columns = df_db.columns.str.lower()
    return df_db

@st.cache_data(ttl=300)
def cargar_criticas_desde_db():
    try:
        # Hacemos un JOIN similar para las alertas críticas
        query = """
            SELECT 
                ac.datetime,
                s.nombre_stablecoin AS stablecoin,
                COALESCE(p.price, 1.0) AS price,
                COALESCE(p.peg_deviation, 0.0) AS peg_deviation,
                ac.nivel_alerta,
                ac.narrativa_alerta,
                ac.btc_return,
                ac.eth_return,
                -- Agregamos un placeholder de market_volatility y anomaly_score si tu frontend lo requiere
                0.0 AS market_volatility, 
                0.0 AS anomaly_score
            FROM alertas_criticas ac
            INNER JOIN stablecoins s ON ac.stablecoin_id = s.stablecoin_id
            LEFT JOIN preprocesados_historico p 
                ON ac.stablecoin_id = p.stablecoin_id AND ac.datetime = p.datetime;
        """
        with engine.connect() as connection:
            df_db = pd.read_sql(query, connection)
        
        df_db.columns = df_db.columns.str.lower()
        return df_db
    except Exception as e:
        # Si la tabla da algún problema, devuelve un DataFrame vacío estructurado
        st.sidebar.error(f"Error cargando alertas críticas: {e}")
        return pd.DataFrame()

# ==================================
# PROCESAMIENTO DE DATOS
# ==================================

df = cargar_datos_desde_db()

# Asegurar que los tipos de datos sean correctos tras la consulta
df["datetime"] = pd.to_datetime(df["datetime"])
df = df.sort_values("datetime")

# ==================================
# TÍTULO
# ==================================

st.markdown(icon_heading("alert", "Centro de Alertas", level=1), unsafe_allow_html=True)

ultima_fecha = df["datetime"].max()

st.markdown(
    icon_md("clock", f"Última actualización: {ultima_fecha.strftime('%d/%m/%Y')}", size=14),
    unsafe_allow_html=True,
)

st.write("""
Monitorización automática del estado de las principales stablecoins
mediante el sistema inteligente de alertas desarrollado en CriptoRadar.
""")

st.divider()

# ==================================
# FILTROS
# ==================================
# Este bloque ahora va ANTES de los KPIs (antes estaba después), para poder
# filtrar "datos" primero y calcular los KPIs sobre ese dataframe filtrado.

st.sidebar.markdown(icon_heading("settings", "Filtros", level=3), unsafe_allow_html=True)

niveles = st.sidebar.multiselect(
    "Nivel de alerta",
    sorted(df["nivel_alerta"].unique()),
    default=sorted(df["nivel_alerta"].unique())
)

stable = st.sidebar.multiselect(
    "Stablecoin",
    sorted(df["stablecoin"].unique()),
    default=sorted(df["stablecoin"].unique())
)

min_fecha = df["datetime"].min().date()
max_fecha = df["datetime"].max().date()

rango_fechas = st.sidebar.slider(
    "Rango de fechas",
    min_value=min_fecha,
    max_value=max_fecha,
    value=(min_fecha, max_fecha),
    format="DD/MM/YYYY"
)

fecha_inicio, fecha_fin = rango_fechas

# ==================================
# FILTRAR DATOS
# ==================================

datos = df[
    (df["nivel_alerta"].isin(niveles))
    &
    (df["stablecoin"].isin(stable))
    &
    (df["datetime"].dt.date >= fecha_inicio)
    &
    (df["datetime"].dt.date <= fecha_fin)
].copy()

# ==================================
# KPIs
# ==================================


normal = (datos["nivel_alerta"] == "0_normal").sum()
vigilancia = (datos["nivel_alerta"] == "1_VIGILANCIA_STABLECOIN").sum()
critica = (datos["nivel_alerta"] == "2_ALERTA_MERCADO").sum()
total = len(datos)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(metric_html("document", "Registros", str(total)), unsafe_allow_html=True)

with c2:
    st.markdown(metric_html("dot-green", "Normales", str(normal)), unsafe_allow_html=True)

with c3:
    st.markdown(metric_html("dot-yellow", "Vigilancia", str(vigilancia)), unsafe_allow_html=True)

with c4:
    st.markdown(metric_html("dot-red", "Alertas", str(critica)), unsafe_allow_html=True)

st.divider()


# ==================================
# EVOLUCIÓN DE ALERTAS
# ==================================

st.markdown(icon_heading("trending-up", "Evolución temporal de las alertas", level=3), unsafe_allow_html=True)

evolucion = (
    datos
    .groupby(["datetime","nivel_alerta"])
    .size()
    .reset_index(name="cantidad")
)

fig = px.line(
    evolucion,
    x="datetime",
    y="cantidad",
    color="nivel_alerta",
    markers=True,
    title="Número de alertas por fecha"
)

fig.update_layout(
    template="plotly_dark",
    title_x=0.5,
    height=500,
    legend_title=""
)

st.plotly_chart(fig, use_container_width=True)

st.markdown(
    icon_box(
        "search",
        "Este gráfico muestra cómo evoluciona el número de alertas detectadas "
        "por el sistema a lo largo del tiempo, permitiendo identificar periodos "
        "de mayor estrés en el mercado.",
        kind="info",
    ),
    unsafe_allow_html=True,
)

st.divider()

# ==================================
# DISTRIBUCIÓN
# ==================================

st.markdown(icon_heading("bar-chart", "Distribución de niveles de alerta", level=3), unsafe_allow_html=True)

conteo = (
    datos["nivel_alerta"]
    .value_counts()
    .reset_index()
)
conteo.columns = ["nivel_alerta","cantidad"]

fig2 = px.pie(
    conteo,
    names="nivel_alerta",
    values="cantidad",
    hole=0.5,
    title="Distribución de alertas"
)

fig2.update_layout(
    template="plotly_dark",
    title_x=0.5,
    height=500
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ==================================
# TABLA
# ==================================

st.markdown(icon_heading("document", "Registro de Alertas", level=3), unsafe_allow_html=True)

columnas = [
    "datetime",
    "stablecoin",
    "price",
    "peg_deviation",
    "market_volatility",
    "anomaly_score",
    "nivel_alerta"
]

st.dataframe(
    datos[columnas].sort_values("datetime", ascending=False),
    use_container_width=True
)

# ==================================
# MATRIZ Y COMPARATIVA DE ALERTAS (NIVELES 1 Y 2)
# ==================================



st.markdown(icon_heading("search", "Análisis detallado de anomalías críticas", level=3), unsafe_allow_html=True)

# 1. Filtramos solo los niveles críticos (Vigilancia y Alerta)
df_criticas_filtrado = datos[datos["nivel_alerta"].isin(["1_VIGILANCIA_STABLECOIN", "2_ALERTA_MERCADO"])]

if df_criticas_filtrado.empty:
    st.markdown(
        icon_box("check-circle", "No hay alertas de nivel 'Vigilancia' o 'Alerta de Mercado' en el rango de filtros seleccionado.", kind="success"),
        unsafe_allow_html=True,
    )
else:

    columnas_esperadas = ["1_VIGILANCIA_STABLECOIN", "2_ALERTA_MERCADO"]

    ct = pd.crosstab(df_criticas_filtrado["stablecoin"], df_criticas_filtrado["nivel_alerta"])

    # Lista completa de stablecoins según el filtro activo (no solo las que tienen
    # alertas 1/2), para que las que tengan 0 alertas también aparezcan en la tabla.
    todas_las_stables = sorted(datos["stablecoin"].unique())

    ct_alertas = ct.reindex(
        index=todas_las_stables,
        columns=columnas_esperadas,
        fill_value=0
    )

    # Creamos dos columnas en Streamlit para el diseño side-by-side
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        # HEATMAP interactivo con Plotly
        fig_heat = px.imshow(
            ct_alertas,
            text_auto=True,
            color_continuous_scale="Reds",
            aspect="auto",  # <- clave: sin esto, imshow fuerza celdas cuadradas y el
                             #    gráfico se encoge dentro del contenedor (era el bug)
            title="Nº de alertas por stablecoin (niveles 1 y 2)",
            labels=dict(x="Nivel de Alerta", y="Stablecoin", color="Cantidad")
        )

        fig_heat.update_layout(
            template="plotly_dark",
            title_x=0.5,
            height=450,
            margin=dict(t=60, b=100, l=10, r=10),
            coloraxis_showscale=False
        )

        fig_heat.update_xaxes(tickangle=25, tickfont=dict(size=11))
        fig_heat.update_traces(textfont=dict(size=13))

        st.plotly_chart(fig_heat, use_container_width=True)

    with col_chart2:
        # GRÁFICO DE BARRAS APILADAS interactivo con Plotly
        fig_bar = px.bar(
            ct_alertas,
            x=ct_alertas.index,
            y=["1_VIGILANCIA_STABLECOIN", "2_ALERTA_MERCADO"],
            title="Alertas por stablecoin (barras apiladas)",
            color_discrete_map={
                "1_VIGILANCIA_STABLECOIN": "#FFA500",  # Naranja
                "2_ALERTA_MERCADO": "#FF0000"          # Rojo
            }
        )

        fig_bar.update_layout(
            template="plotly_dark",
            barmode="stack",
            xaxis_title="",
            yaxis_title="Cantidad de Alertas",
            title_x=0.5,
            legend_title="",
            height=450,
            margin=dict(t=60, b=100, l=10, r=10)
        )

        fig_bar.update_xaxes(tickangle=25, tickfont=dict(size=11))

        st.plotly_chart(fig_bar, use_container_width=True)
# ==================================
# CARGAR INFORME DE ALERTAS CRÍTICAS
# ==================================

df_criticas = cargar_criticas_desde_db()

if not df_criticas.empty:
    df_criticas["datetime"] = pd.to_datetime(df_criticas["datetime"])

st.divider()


# ==================================
# RANKING DE ANOMALÍAS
# ==================================

st.markdown(icon_heading("trophy", "Stablecoins con mayor estabilidad", level=3), unsafe_allow_html=True)

ranking = (
    datos.groupby("stablecoin")["anomaly_score"]
    .mean()
    .reset_index()
    .sort_values("anomaly_score", ascending=False)
)

fig3 = px.bar(
    ranking,
    x="stablecoin",
    y="anomaly_score",
    title="Anomaly Score promedio"
)

fig3.update_layout(
    template="plotly_dark",
    title_x=0.5,
    height=450
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown(
    icon_box(
        "search",
        "El Anomaly Score resume el comportamiento anómalo detectado por el sistema. "
        "Cuanto menor es este indicador (más cercano a cero o negativo), "
        "mayor es la probabilidad de anomalías",
        kind="info",
    ),
    unsafe_allow_html=True,
)

st.divider()

# ==================================
# DESCARGAR INFORME
# ==================================

if not df_criticas.empty:
    csv = df_criticas.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Descargar informe de alertas",
        csv,
        file_name="alertas_criticas.csv",
        mime="text/csv"
    )

st.divider()

# ==================================
# CONCLUSIÓN AUTOMÁTICA
# ==================================

st.markdown(icon_heading("pin", "Estado del sistema", level=3), unsafe_allow_html=True)

if critica > 0:
    st.markdown(
        icon_box(
            "alert",
            f"Se detectaron **{critica} alertas de mercado**.\n\n"
            "Se recomienda revisar inmediatamente las stablecoins afectadas, "
            "ya que presentan anomalías relevantes detectadas por el sistema.",
            kind="error",
        ),
        unsafe_allow_html=True,
    )
elif vigilancia > 0:
    st.markdown(
        icon_box(
            "alert",
            f"Actualmente existen **{vigilancia} registros en vigilancia**.\n\n"
            "Aunque no representan una situación crítica, conviene mantener "
            "un seguimiento de su evolución.",
            kind="warning",
        ),
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        icon_box(
            "check-circle",
            "Todas las stablecoins analizadas presentan un comportamiento "
            "estable y no se detectan anomalías relevantes.",
            kind="success",
        ),
        unsafe_allow_html=True,
    )

# ==================================
# ALERTAS CRÍTICAS
# ==================================
# Reemplaza tu bloque actual de "ALERTAS CRÍTICAS" por este. Ahora incluye el texto
# de narrativa_alerta (tabla Alertas_Criticas) dentro de la propia tarjeta, en vez
# de dejarlo solo en la sección separada de más abajo.

st.markdown(icon_heading("alert", "Alertas relevantes", level=3), unsafe_allow_html=True)

if df_criticas.empty:
    st.markdown(
        icon_box("check-circle", "No existen alertas críticas registradas.", kind="success"),
        unsafe_allow_html=True,
    )
else:
    for _, fila in df_criticas.sort_values("datetime", ascending=False).iterrows():

        # Texto de la narrativa automática (si existe y no está vacío)
        tiene_narrativa = (
            "narrativa_alerta" in fila
            and pd.notna(fila["narrativa_alerta"])
            and str(fila["narrativa_alerta"]).strip() != ""
        )
        narrativa_md = (
            f"\n\n**Narrativa:** {fila['narrativa_alerta']}" if tiene_narrativa else ""
        )

        cuerpo = (
            f"### {fila['stablecoin']}\n\n"
            f"**Fecha:** {fila['datetime'].strftime('%d/%m/%Y')}\n\n"
            f"Precio: **{fila['price']:.4f} USD**\n\n"
            f"Desviación del Peg: **{fila['peg_deviation']:.4f}**{narrativa_md}"
        )

        if fila["nivel_alerta"] == "2_ALERTA_MERCADO":
            st.markdown(icon_box("dot-red", cuerpo, kind="error"), unsafe_allow_html=True)

        elif fila["nivel_alerta"] == "1_VIGILANCIA_STABLECOIN":
            st.markdown(icon_box("dot-yellow", cuerpo, kind="warning"), unsafe_allow_html=True)

st.divider()