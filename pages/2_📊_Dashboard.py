import streamlit as st
import plotly.express as px

from src.componentes import cabecera
from src.cargar_streamlit import cargar_crypto, cargar_stable

# =====================================================
# CARGAR DATOS
# =====================================================

df_crypto = cargar_crypto()
df_stable = cargar_stable()

df_crypto = df_crypto.sort_values("datetime")

# =====================================================
# CABECERA
# =====================================================

cabecera(df_crypto, df_stable)

st.title("📊 Dashboard Ejecutivo")

ultima_actualizacion = df_crypto["datetime"].max()

st.caption(
    f"🕒 Datos actualizados hasta: {ultima_actualizacion.strftime('%d/%m/%Y')}"
)

st.write(
    "Resumen general del mercado de criptomonedas y stablecoins."
)

# =====================================================
# FILTROS
# =====================================================

st.sidebar.header("⚙️ Filtros")

crypto = st.sidebar.selectbox(
    "Criptomoneda",
    sorted(df_crypto["crypto_id"].unique())
)

fecha_inicio = st.sidebar.date_input(
    "📅 Fecha inicial",
    value=df_crypto["datetime"].min().date()
)

fecha_fin = st.sidebar.date_input(
    "📅 Fecha final",
    value=df_crypto["datetime"].max().date()
)

# =====================================================
# FILTRAR DATOS
# =====================================================

datos = df_crypto[
    (df_crypto["crypto_id"] == crypto)
    &
    (df_crypto["datetime"].dt.date >= fecha_inicio)
    &
    (df_crypto["datetime"].dt.date <= fecha_fin)
].copy()

datos = datos.sort_values("datetime")

# =====================================================
# MÉTRICAS
# =====================================================

datos["media_movil_30"] = datos["close"].rolling(30).mean()

precio_actual = datos.iloc[-1]["close"]
precio_anterior = datos.iloc[-2]["close"]

variacion = (
    (precio_actual - precio_anterior)
    / precio_anterior
) * 100

# =====================================================
# KPIs
# =====================================================

st.subheader(f"🪙 Resumen de {crypto.capitalize()}")

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "💰 Precio actual",
        f"${precio_actual:,.2f}",
        delta=f"{variacion:.2f}%"
    )

with c2:

    st.metric(
        "📈 Máximo",
        f"${datos['high'].max():,.2f}"
    )

with c3:

    st.metric(
        "📉 Mínimo",
        f"${datos['low'].min():,.2f}"
    )

with c4:

    st.metric(
        "📊 Volumen total",
        f"{datos['volume'].sum():,.0f}"
    )

st.divider()

# =====================================================
# PRECIO
# =====================================================

fig = px.line(
    datos,
    x="datetime",
    y=["close", "media_movil_30"],
    title=f"📈 Evolución del precio de {crypto.capitalize()}",
    labels={
        "value": "Precio USD",
        "datetime": "Fecha"
    }
)

fig.update_layout(

    template="plotly_dark",

    paper_bgcolor="#0E1117",

    plot_bgcolor="#161A24",

    font=dict(color="white"),

    title_x=0.5,

    legend_title="",

    hovermode="x unified",

    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

if variacion >= 0:

    st.success(
        f"📈 {crypto.capitalize()} registró una variación positiva de {variacion:.2f}% respecto al día anterior."
    )

else:

    st.error(
        f"📉 {crypto.capitalize()} registró una variación negativa de {variacion:.2f}% respecto al día anterior."
    )

st.divider()

# =====================================================
# VOLUMEN
# =====================================================

fig2 = px.area(
    datos,
    x="datetime",
    y="volume",
    title=f"💵 Volumen negociado de {crypto.capitalize()}"
)

fig2.update_layout(

    template="plotly_dark",

    paper_bgcolor="#0E1117",

    plot_bgcolor="#161A24",

    font=dict(color="white"),

    title_x=0.5,

    hovermode="x unified",

    height=450
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.info(
    """
**Interpretación**

Los incrementos de volumen suelen coincidir con periodos
de mayor actividad del mercado y aumentos de volatilidad.
"""
)

st.divider()

# =====================================================
# TABLA
# =====================================================

st.subheader("📋 Últimos registros")

st.dataframe(

    datos.tail(10).style.format({

        "open":"{:,.2f}",

        "high":"{:,.2f}",

        "low":"{:,.2f}",

        "close":"{:,.2f}",

        "volume":"{:,.0f}"

    }),

    use_container_width=True
)

# =====================================================
# DESCARGA
# =====================================================

csv = datos.to_csv(index=False).encode("utf-8")

st.download_button(

    "📥 Descargar datos en CSV",

    csv,

    file_name=f"{crypto}.csv",

    mime="text/csv"
)