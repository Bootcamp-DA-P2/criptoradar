import streamlit as st
import plotly.express as px

from src.view.cargar_streamlit import cargar_crypto
from src.view.icons import icon_heading, icon_box, metric_html


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

st.markdown(icon_heading("coin", "Análisis de Criptomonedas", level=1), unsafe_allow_html=True)

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

with c1:
    st.markdown(
        metric_html("banknote", "Precio actual", f"${precio_actual:,.2f}", delta=f"{delta:.2f}%"),
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        metric_html("trending-up", "Máximo histórico", f"${datos['high'].max():,.2f}"),
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        metric_html("trending-down", "Mínimo histórico", f"${datos['low'].min():,.2f}"),
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        metric_html("bar-chart", "Volumen promedio", f"{datos['volume'].mean():,.0f}"),
        unsafe_allow_html=True,
    )

st.divider()

# ==================================
# PRECIO
# ==================================

fig = px.line(
    datos,
    x="datetime",
    y=["close", "media_movil_30"],
    title="Evolución del precio"
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

st.markdown(
    icon_box(
        "search",
        f"**Interpretación**\n\n"
        f"Durante el periodo analizado, **{crypto.capitalize()}** presenta una evolución "
        "histórica que permite identificar tendencias alcistas y bajistas.\n\n"
        "La **media móvil de 30 días** suaviza las fluctuaciones diarias y facilita "
        "la identificación de la tendencia predominante.",
        kind="info",
    ),
    unsafe_allow_html=True,
)

# ==================================
# VOLUMEN
# ==================================

fig2 = px.area(
    datos,
    x="datetime",
    y="volume",
    title="Volumen diario"
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

st.markdown(
    icon_box(
        "search",
        "**Interpretación**\n\n"
        "Los picos de volumen representan un incremento importante en la actividad "
        "de compra y venta del activo.\n\n"
        "Generalmente coinciden con eventos relevantes del mercado o periodos "
        "de elevada volatilidad.",
        kind="info",
    ),
    unsafe_allow_html=True,
)

# ==================================
# RETORNO
# ==================================

fig3 = px.line(
    datos,
    x="datetime",
    y="retorno",
    title="Variación porcentual diaria"
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

st.markdown(
    icon_box(
        "search",
        "**Interpretación**\n\n"
        "El retorno diario muestra la variación porcentual respecto al día anterior.\n\n"
        "Valores cercanos a cero indican estabilidad, mientras que variaciones "
        "grandes reflejan jornadas de alta volatilidad.",
        kind="info",
    ),
    unsafe_allow_html=True,
)

# ==================================
# HISTOGRAMA
# ==================================

fig4 = px.histogram(
    datos,
    x="close",
    nbins=40,
    title="Distribución histórica del precio"
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

st.markdown(
    icon_box(
        "search",
        "**Interpretación**\n\n"
        "La distribución permite identificar los rangos de precio donde la "
        "criptomoneda ha permanecido con mayor frecuencia durante el periodo "
        "analizado.",
        kind="info",
    ),
    unsafe_allow_html=True,
)

# ==================================
# ESTADÍSTICAS
# ==================================

st.markdown(icon_heading("document", "Estadísticas descriptivas", level=3), unsafe_allow_html=True)

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

with st.expander("Ver últimos registros"):

    st.dataframe(
        datos.tail(30),
        use_container_width=True
    )