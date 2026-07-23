import streamlit as st
import plotly.express as px

from src.view.cargar_streamlit import cargar_stable
from src.view.icons import icon_heading, icon_box, metric_html

# ==================================
# CONFIGURACIÓN
# ==================================

st.set_page_config(layout="wide")

# ==================================
# CARGAR DATOS
# ==================================

df = cargar_stable()

df = df.sort_values("datetime")

# ==================================
# TÍTULO
# ==================================

st.markdown(icon_heading("shield", "Análisis de Stablecoins", level=1), unsafe_allow_html=True)

st.markdown("""
Analiza la estabilidad de las principales stablecoins mediante indicadores de precio,
capitalización de mercado y desviación respecto al dólar.
""")

# ==================================
# FILTRO
# ==================================

stable = st.selectbox(
    "Selecciona una Stablecoin",
    sorted(df["stablecoin"].unique())
)

datos = df[df["stablecoin"] == stable].copy()

datos = datos.sort_values("datetime")

# ==================================
# KPIs
# ==================================

precio_actual = datos.iloc[-1]["price"]
precio_anterior = datos.iloc[-2]["price"]

delta = ((precio_actual - precio_anterior) / precio_anterior) * 100

marketcap = datos.iloc[-1]["market_cap"]

peg = datos["peg_deviation"].mean()

volatilidad = datos["price_volatility_3d"].mean()

st.divider()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        metric_html("banknote", "Precio actual", f"${precio_actual:.4f}", delta=f"{delta:.2f}%"),
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        metric_html("target", "Peg promedio", f"{peg:.5f}"),
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        metric_html("coin", "Market Cap", f"${marketcap:,.0f}"),
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        metric_html("bar-chart", "Volatilidad 3 días", f"{volatilidad:.4f}"),
        unsafe_allow_html=True,
    )

st.divider()

# ==================================
# PRECIO
# ==================================

fig = px.line(
    datos,
    x="datetime",
    y="price",
    title="Evolución del precio"
)

fig.update_layout(
    template="plotly_white",
    height=450,
    title_x=0.5
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown(
    icon_box(
        "target",
        "El precio debería permanecer muy cercano a **1 USD**. "
        "Desviaciones importantes pueden indicar pérdida temporal del peg.",
        kind="info",
    ),
    unsafe_allow_html=True,
)

# ==================================
# PEG
# ==================================

fig2 = px.line(
    datos,
    x="datetime",
    y="peg_deviation",
    title="Desviación respecto al dólar"
)

fig2.add_hline(
    y=0,
    line_dash="dash",
    line_color="red"
)

fig2.update_layout(
    template="plotly_white",
    height=450,
    title_x=0.5
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.markdown(
    icon_box(
        "target",
        "Cuanto más cerca esté la línea del valor **0**, mayor estabilidad presenta la stablecoin.",
        kind="info",
    ),
    unsafe_allow_html=True,
)

# ==================================
# MARKET CAP
# ==================================

fig3 = px.area(
    datos,
    x="datetime",
    y="market_cap",
    title="Evolución del Market Cap"
)

fig3.update_layout(
    template="plotly_white",
    height=450,
    title_x=0.5
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.markdown(
    icon_box(
        "coin",
        "La evolución del Market Cap refleja el crecimiento o disminución del uso de la stablecoin.",
        kind="info",
    ),
    unsafe_allow_html=True,
)

# ==================================
# SUPPLY
# ==================================

fig4 = px.line(
    datos,
    x="datetime",
    y=["supply_change_1d", "supply_change_7d"],
    title="Cambios de oferta"
)

fig4.update_layout(
    template="plotly_white",
    height=450,
    title_x=0.5,
    legend_title=""
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.markdown(
    icon_box(
        "bar-chart",
        "Estos indicadores muestran cómo cambia la oferta circulante de la stablecoin en 1 y 7 días.",
        kind="info",
    ),
    unsafe_allow_html=True,
)

# ==================================
# VOLATILIDAD
# ==================================

fig5 = px.line(
    datos,
    x="datetime",
    y="price_volatility_3d",
    title="Volatilidad de 3 días"
)

fig5.update_layout(
    template="plotly_white",
    height=450,
    title_x=0.5
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.markdown(
    icon_box(
        "trending-down",
        "Una volatilidad baja indica un comportamiento estable, mientras que incrementos "
        "pueden señalar episodios de incertidumbre.",
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
        [
            "price",
            "market_cap",
            "peg_deviation",
            "supply_change_1d",
            "supply_change_7d",
            "price_volatility_3d"
        ]
    ]
    .describe()
    .style.format("{:,.4f}"),
    use_container_width=True
)

with st.expander("Ver últimos registros"):

    st.dataframe(
        datos.tail(30),
        use_container_width=True
    )