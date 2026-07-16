#!/bin/sh

echo "=== Directorio ==="
env

echo "=== Directorio ==="
pwd

echo "=== Archivos ==="
find /app -maxdepth 3

echo "=== Ejecutando carga_datos ==="

python src/database/carga_datos.py

echo "Código de salida: $?"

echo "=== Arrancando Streamlit ==="

exec streamlit run streamlit_app.py \
    --server.address=0.0.0.0 \
    --server.port=8501