import streamlit as st
import pandas as pd
import plotly.express as px

# ==================================
# CONFIGURACIÓN
# ==================================

st.set_page_config(
    page_title="Centro de Alertas",
    page_icon="🚨",
    layout="wide"
)

# ==================================
# CONEXIÓN A LA BASE DE DATOS
# ==================================

# Creamos la conexión. 
# Si usas SQLite local, busca un archivo llamado "alertas.db" en tu proyecto.
# Para PostgreSQL/MySQL, consulta la sección de notas abajo.
conn = st.connection("sql", type="sql")

# Función para cargar los datos con caché para optimizar el rendimiento
@st.cache_data(ttl=300) # Expira la caché cada 5 minutos
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
    df_db = conn.query(query)
    
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
        df_db = conn.query(query)
        
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

st.title("🚨 Centro de Alertas")

ultima_fecha = df["datetime"].max()

st.caption(
    f"🕒 Última actualización: {ultima_fecha.strftime('%d/%m/%Y')}"
)

st.write("""
Monitorización automática del estado de las principales stablecoins
mediante el sistema inteligente de alertas desarrollado en CriptoRadar.
""")

st.divider()

# ==================================
# KPIs
# ==================================

normal = (df["nivel_alerta"] == "0_normal").sum()
vigilancia = (df["nivel_alerta"] == "1_VIGILANCIA_STABLECOIN").sum()
critica = (df["nivel_alerta"] == "2_ALERTA_MERCADO").sum()
total = len(df)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("📄 Registros", total)

with c2:
    st.metric("🟢 Normales", normal)

with c3:
    st.metric("🟡 Vigilancia", vigilancia)

with c4:
    st.metric("🔴 Alertas", critica)

st.divider()

# ==================================
# FILTROS
# ==================================

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

datos = df[
    (df["nivel_alerta"].isin(niveles))
    &
    (df["stablecoin"].isin(stable))
]

# ==================================
# EVOLUCIÓN DE ALERTAS
# ==================================

st.subheader("📈 Evolución temporal de las alertas")

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

st.info("""
Este gráfico muestra cómo evoluciona el número de alertas detectadas
por el sistema a lo largo del tiempo, permitiendo identificar periodos
de mayor estrés en el mercado.
""")

st.divider()

# ==================================
# DISTRIBUCIÓN
# ==================================

st.subheader("📊 Distribución de niveles de alerta")

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

st.subheader("📋 Registro de Alertas")

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
# CARGAR INFORME DE ALERTAS CRÍTICAS
# ==================================

df_criticas = cargar_criticas_desde_db()

if not df_criticas.empty:
    df_criticas["datetime"] = pd.to_datetime(df_criticas["datetime"])

st.divider()

# ==================================
# ALERTAS CRÍTICAS
# ==================================

st.subheader("🚨 Alertas relevantes")

if df_criticas.empty:
    st.success("✅ No existen alertas críticas registradas.")
else:
    for _, fila in df_criticas.sort_values("datetime", ascending=False).iterrows():
        if fila["nivel_alerta"] == "2_ALERTA_MERCADO":
            st.error(f"""
### 🔴 {fila['stablecoin']}

**Fecha:** {fila['datetime'].strftime('%d/%m/%Y')}

💵 Precio: **{fila['price']:.4f} USD**

🎯 Desviación del Peg: **{fila['peg_deviation']:.4f}**

📉 Volatilidad: **{fila['market_volatility']:.2f}**

🤖 Anomaly Score: **{fila['anomaly_score']:.2f}**
""")
        elif fila["nivel_alerta"] == "1_VIGILANCIA_STABLECOIN":
            st.warning(f"""
### 🟡 {fila['stablecoin']}

**Fecha:** {fila['datetime'].strftime('%d/%m/%Y')}

💵 Precio: **{fila['price']:.4f} USD**

🎯 Desviación del Peg: **{fila['peg_deviation']:.4f}**

🤖 Anomaly Score: **{fila['anomaly_score']:.2f}**
""")

st.divider()

# ==================================
# NARRATIVAS
# ==================================

if not df_criticas.empty and "narrativa_alerta" in df_criticas.columns:
    st.subheader("📝 Narrativa automática")
    for _, fila in df_criticas.sort_values("datetime", ascending=False).iterrows():
        with st.expander(f"{fila['datetime'].strftime('%d/%m/%Y')} - {fila['stablecoin']}"):
            st.write(fila["narrativa_alerta"])

st.divider()

# ==================================
# RANKING DE ANOMALÍAS
# ==================================

st.subheader("🏆 Stablecoins con mayor riesgo")

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

st.info("""
El Anomaly Score resume el comportamiento anómalo detectado por el sistema.
Cuanto mayor es este indicador, mayor es la probabilidad de que la stablecoin
esté experimentando condiciones fuera de su comportamiento habitual.
""")

st.divider()

# ==================================
# DESCARGAR INFORME
# ==================================

if not df_criticas.empty:
    csv = df_criticas.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Descargar informe de alertas",
        csv,
        file_name="alertas_criticas.csv",
        mime="text/csv"
    )

st.divider()

# ==================================
# CONCLUSIÓN AUTOMÁTICA
# ==================================

st.subheader("📌 Estado del sistema")

if critica > 0:
    st.error(f"""
Se detectaron **{critica} alertas de mercado**.

Se recomienda revisar inmediatamente las stablecoins afectadas,
ya que presentan anomalías relevantes detectadas por el sistema.
""")
elif vigilancia > 0:
    st.warning(f"""
Actualmente existen **{vigilancia} registros en vigilancia**.

Aunque no representan una situación crítica, conviene mantener
un seguimiento de su evolución.
""")
else:
    st.success("""
Todas las stablecoins analizadas presentan un comportamiento
estable y no se detectan anomalías relevantes.
""")