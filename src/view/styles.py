import streamlit as st

def cargar_css():

    st.markdown(
        """
<style>

.main{
    background-color:#0E1117;
}

section[data-testid="stSidebar"]{
    background-color:#171A21;
}

h1{
    color:#00D4FF;
    font-weight:700;
}

h2{
    color:white;
}

h3{
    color:#79CFFF;
}

p{
    font-size:17px;
}

div[data-testid="metric-container"]{

    background:#1A1E27;

    border-radius:15px;

    padding:15px;

    border:1px solid #2A3240;

    box-shadow:0px 0px 10px rgba(0,212,255,0.15);

}

div.stAlert{

    border-radius:15px;

}

div[data-testid="stDataFrame"]{

    border-radius:15px;

}

</style>
""",
        unsafe_allow_html=True
    )