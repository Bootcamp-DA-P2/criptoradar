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

# 1. Instalar dependencias del sistema (Sigue siendo ROOT)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-mysql-client \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# 2. Copiar las dependencias a un directorio accesible para todos los usuarios
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# 3. Copiar y preparar el script de inicio (Sigue siendo ROOT para poder escribir en /)
COPY entrypoint.sh /entrypoint.sh
RUN dos2unix /entrypoint.sh && chmod +x /entrypoint.sh

# 4. Crear el usuario, darle propiedad de sus dependencias y cambiar de usuario
RUN useradd -ms /bin/bash appuser && \
    chown -R appuser:appuser /home/appuser/.local

USER appuser

EXPOSE 8501

ENTRYPOINT ["/entrypoint.sh"]