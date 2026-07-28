import streamlit as st

print("Estoy cargando componentes.py")

def cabecera(df_crypto, df_stable):

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
            "💰 Precio promedio",
            f"${df_crypto['close'].mean():,.2f}"
        )

    with c4:
        st.metric(
            "📈 Volumen promedio",
            f"{df_crypto['volume'].mean():,.0f}"
        )

    st.divider()

import streamlit as st

def cabecera_pagina(titulo, descripcion, fecha):

    st.title(titulo)

    st.caption(
        f"🕒 Datos actualizados hasta: {fecha.strftime('%d/%m/%Y')}"
    )

    st.write(descripcion)

    st.divider()