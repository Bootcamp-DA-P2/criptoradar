import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# 1. Cachamos el motor de conexión (Engine) para no recrearlo en cada renderizado
@st.cache_resource
def obtener_conexion_db():
    # Creamos un engine de SQLAlchemy
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")
    return engine

# 2. Extraer datos de Criptomonedas de la Base de Datos
@st.cache_data
def cargar_crypto():
    engine = obtener_conexion_db()
    # Hacemos la consulta a la tabla correspondiente
    query = "SELECT * FROM crypto_Precios"
    df = pd.read_sql(query, con=engine)
    
    # Aseguramos el tipo de dato datetime
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df

# 3. Extraer datos de Stablecoins de la Base de Datos
@st.cache_data
def cargar_stable():
    engine = obtener_conexion_db()
    
    # IMPORTANTE: Como en tu base de datos la tabla 'Preprocesados_Historico' 
    # solo guarda 'stablecoin_id', hacemos un JOIN con la tabla maestra 'Stablecoins'
    # para recuperar la columna de texto 'stablecoin' (USDT, USDC...) que usa tu App/EDA.
    query = """
        SELECT 
            h.*, 
            s.nombre_stablecoin AS stablecoin 
        FROM preprocesados_historico h
        LEFT JOIN stablecoins s ON h.stablecoin_id = s.stablecoin_id
    """
    df = pd.read_sql(query, con=engine)
    
    # Aseguramos el tipo de dato datetime
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df