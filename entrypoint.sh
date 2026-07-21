#!/bin/sh
set -e

echo "⏳ Esperando a que MySQL esté disponible..."

until mysqladmin ping \
    -h"$DB_HOST" \
    -P"${DB_PORT:-3306}" \
    -u"$DB_USER" \
    -p"$DB_PASS" \
    --skip-ssl
do
    echo "MySQL aún no está listo, esperando..."
    sleep 2
done

echo "✅ MySQL disponible"

# Intervalo de refresco del pipeline (en segundos). Por defecto 24h.
# Se puede sobreescribir con la variable de entorno PIPELINE_INTERVAL_SECONDS en Railway.
INTERVALO="${PIPELINE_INTERVAL_SECONDS:-86400}"

echo "🚀 Ejecutando pipeline inicial (descarga, limpieza, alertas y carga en MySQL)..."
python app.py || echo "⚠️  El pipeline inicial falló, revisa el log. Streamlit arrancará igualmente."

echo "🕒 Programando el pipeline para repetirse cada ${INTERVALO}s en segundo plano..."
(
    while true; do
        sleep "$INTERVALO"
        echo "🔄 [$(date -u +'%Y-%m-%dT%H:%M:%SZ')] Ejecutando pipeline programado..."
        python app.py || echo "⚠️  Error en la ejecución programada del pipeline, se reintentará en el próximo ciclo."
    done
) &

echo "🌐 Iniciando Streamlit..."
exec streamlit run streamlit_app.py \
    --server.address=0.0.0.0 \
    --server.port=8501