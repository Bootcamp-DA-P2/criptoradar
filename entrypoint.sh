#!/bin/sh
set -e

echo "⏳ Esperando a que MySQL esté disponible..."
echo "🔎 DB_HOST=$DB_HOST DB_PORT=$DB_PORT DB_USER=$DB_USER DB_NAME=$DB_NAME"
echo "🔎 Resolviendo DNS de $DB_HOST..."
getent hosts "$DB_HOST" || echo "⚠️  No se pudo resolver $DB_HOST por DNS"

intentos=0
until mysqladmin ping \
    -h"$DB_HOST" \
    -P"${DB_PORT:-3306}" \
    -u"$DB_USER" \
    -p"$DB_PASS" \
    --skip-ssl
do
    intentos=$((intentos+1))
    echo "MySQL aún no está listo (intento $intentos), esperando..."
    if [ "$intentos" -ge 5 ]; then
        echo "❌ Han pasado 5 intentos, abortando para ver el error completo arriba."
        exit 1
    fi
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