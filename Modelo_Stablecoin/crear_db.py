import pandas as pd
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
CSV_PATH = PROJECT_ROOT / 'dataset_stablecoins_macro_2021_2026.csv'
DB_PATH = PROJECT_ROOT / 'cripto_data.db'

# 1. Cargar el CSV asegurando el formato de fecha
df = pd.read_csv(CSV_PATH)
df['fecha'] = pd.to_datetime(df['fecha'])

# 2. Conectar a SQLite (creará el archivo 'cripto_data.db' si no existe)
conn = sqlite3.connect(DB_PATH)

# 3. Guardar los datos en una tabla
# Usamos index=False para que no guarde el número de fila como columna
df.to_sql('riesgo_macro', conn, if_exists='replace', index=False)

print("¡Base de datos creada y datos importados con éxito!")

# 4. Cerrar la conexión
conn.close()