import streamlit as st
import plotly.express as px

from src.view.cargar_streamlit import cargar_crypto


# ==================================
# CONFIGURACIÓN
# ==================================

st.set_page_config(layout="wide")

# ==================================
# CARGAR DATOS
# ==================================

df = cargar_crypto()

df = df.sort_values("datetime")

# ==================================
# TÍTULO
# ==================================

st.title("🪙 Análisis de Criptomonedas")

st.markdown("""
Explora el comportamiento histórico de las criptomonedas analizadas mediante
indicadores, estadísticas y visualizaciones interactivas.
""")

# ==================================
# FILTROS
# ==================================

crypto = st.selectbox(
    "Selecciona una criptomoneda",
    sorted(df["crypto_id"].unique())
)

datos = df[df["crypto_id"] == crypto].copy()

datos = datos.sort_values("datetime")

# ==================================
# VARIABLES
# ==================================

precio_actual = datos.iloc[-1]["close"]
precio_anterior = datos.iloc[-2]["close"]

delta = (
    (precio_actual - precio_anterior)
    / precio_anterior
) * 100

datos["media_movil_30"] = (
    datos["close"]
    .rolling(30)
    .mean()
)

datos["retorno"] = (
    datos["close"]
    .pct_change()
    * 100
)

# ==================================
# KPIs
# ==================================

st.divider()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "💰 Precio actual",
    f"${precio_actual:,.2f}",
    f"{delta:.2f}%"
)

c2.metric(
    "📈 Máximo histórico",
    f"${datos['high'].max():,.2f}"
)

c3.metric(
    "📉 Mínimo histórico",
    f"${datos['low'].min():,.2f}"
)

c4.metric(
    "📊 Volumen promedio",
    f"{datos['volume'].mean():,.0f}"
)

st.divider()

# ==================================
# PRECIO
# ==================================

fig = px.line(
    datos,
    x="datetime",
    y=["close", "media_movil_30"],
    title="📈 Evolución del precio"
)

fig.update_traces(
    line_width=3
)

fig.update_layout(
    template="plotly_dark",
    height=500,
    title_x=0.5,
    legend_title=""
)

fig.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#161A24",
    font=dict(color="white"),
    title_x=0.5,
    legend_title="",
    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.info(f"""
### Interpretación

Durante el periodo analizado, **{crypto.capitalize()}** presenta una evolución
histórica que permite identificar tendencias alcistas y bajistas.

La **media móvil de 30 días** suaviza las fluctuaciones diarias y facilita
la identificación de la tendencia predominante.
""")

# ==================================
# VOLUMEN
# ==================================

fig2 = px.area(
    datos,
    x="datetime",
    y="volume",
    title="💵 Volumen diario"
)

fig2.update_layout(
    template="plotly_dark",
    height=450,
    title_x=0.5
)

fig.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#161A24",
    font=dict(color="white"),
    title_x=0.5,
    legend_title="",
    hovermode="x unified"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.info("""
### Interpretación

Los picos de volumen representan un incremento importante en la actividad
de compra y venta del activo.

Generalmente coinciden con eventos relevantes del mercado o periodos
de elevada volatilidad.
""")

# ==================================
# RETORNO
# ==================================

fig3 = px.line(
    datos,
    x="datetime",
    y="retorno",
    title="📊 Variación porcentual diaria"
)

fig3.update_layout(
    template="plotly_dark",
    height=450,
    title_x=0.5
)

fig.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#161A24",
    font=dict(color="white"),
    title_x=0.5,
    legend_title="",
    hovermode="x unified"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.info("""
### Interpretación

El retorno diario muestra la variación porcentual respecto al día anterior.

Valores cercanos a cero indican estabilidad, mientras que variaciones
grandes reflejan jornadas de alta volatilidad.
""")

# ==================================
# HISTOGRAMA
# ==================================

fig4 = px.histogram(
    datos,
    x="close",
    nbins=40,
    title="📉 Distribución histórica del precio"
)

fig4.update_layout(
    template="plotly_dark",
    height=450,
    title_x=0.5
)

fig.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#161A24",
    font=dict(color="white"),
    title_x=0.5,
    legend_title="",
    hovermode="x unified"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.info("""
### Interpretación

La distribución permite identificar los rangos de precio donde la
criptomoneda ha permanecido con mayor frecuencia durante el periodo
analizado.
""")

# ==================================
# ESTADÍSTICAS
# ==================================

st.subheader("📋 Estadísticas descriptivas")

st.dataframe(
    datos[
        ["open", "high", "low", "close", "volume"]
    ]
    .describe()
    .style.format("{:,.2f}"),
    use_container_width=True
)

# ==================================
# DATOS
# ==================================

with st.expander("📄 Ver últimos registros"):

    st.dataframe(
        datos.tail(30),
        use_container_width=True
    )