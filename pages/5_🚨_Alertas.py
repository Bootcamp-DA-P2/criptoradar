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
# CARGAR DATOS
# ==================================

df = pd.read_csv("data/alertas_sistema_final.csv")

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
    st.metric(
        "📄 Registros",
        total
    )

with c2:
    st.metric(
        "🟢 Normales",
        normal
    )

with c3:
    st.metric(
        "🟡 Vigilancia",
        vigilancia
    )

with c4:
    st.metric(
        "🔴 Alertas",
        critica
    )

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

st.plotly_chart(
    fig,
    use_container_width=True
)

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

st.plotly_chart(
    fig2,
    use_container_width=True
)

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
    datos[columnas].sort_values(
        "datetime",
        ascending=False
    ),
    use_container_width=True
)
# ==================================
# CARGAR INFORME DE ALERTAS CRÍTICAS
# ==================================

try:

    df_criticas = pd.read_csv("data/alertas_criticas_informe.csv")

    df_criticas["datetime"] = pd.to_datetime(df_criticas["datetime"])

except:

    df_criticas = pd.DataFrame()

st.divider()

# ==================================
# ALERTAS CRÍTICAS
# ==================================

st.subheader("🚨 Alertas relevantes")

if df_criticas.empty:

    st.success("✅ No existen alertas críticas registradas.")

else:

    for _, fila in df_criticas.sort_values(
        "datetime",
        ascending=False
    ).iterrows():

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

if "narrativa_alerta" in df_criticas.columns:

    st.subheader("📝 Narrativa automática")

    for _, fila in df_criticas.sort_values(
        "datetime",
        ascending=False
    ).iterrows():

        with st.expander(
            f"{fila['datetime'].strftime('%d/%m/%Y')} - {fila['stablecoin']}"
        ):

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
    .sort_values(
        "anomaly_score",
        ascending=False
    )
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

st.plotly_chart(
    fig3,
    use_container_width=True
)

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
