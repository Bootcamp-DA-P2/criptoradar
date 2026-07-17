# --- ETAPA 1: Compilación de dependencias (Builder) ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Instalar dependencias necesarias para compilar ruedas (wheels) de Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt


# --- ETAPA 2: Imagen de ejecución ligera (Final) ---
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalamos solo lo mínimo imprescindible para ejecutar la app (cliente mysql y dos2unix)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-mysql-client \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copiar las dependencias ya compiladas desde la etapa builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copiar el proyecto
COPY . .

# Copiar y preparar el script de inicio
COPY entrypoint.sh /entrypoint.sh
RUN dos2unix /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 8501

ENTRYPOINT ["/entrypoint.sh"]