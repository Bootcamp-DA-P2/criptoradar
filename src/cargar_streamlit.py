from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

@st.cache_data
def cargar_crypto():
    df = pd.read_csv(DATA_DIR / "criptoradar_crypto_final_clean.csv")
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df

@st.cache_data
def cargar_stable():
    df = pd.read_csv(DATA_DIR / "datos_preprocesados_clean.csv")
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df