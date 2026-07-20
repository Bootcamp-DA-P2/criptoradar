#!/bin/sh
set -e

echo "⏳ Esperando a que MySQL esté disponible..."

until mysqladmin ping \
    -h"$DB_HOST" \
    -u"$DB_USER" \
    -p"$DB_PASS" \
    --silent
do
    echo "MySQL aún no está listo, esperando..."
    sleep 2
done

echo "✅ MySQL disponible"

echo "🚀 Inicializando la base de datos..."
python src/database/carga_datos.py

echo "✅ Base de datos inicializada"

echo "🌐 Iniciando Streamlit..."
exec streamlit run streamlit_app.py \
    --server.address=0.0.0.0 \
    --server.port=8501