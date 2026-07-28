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

WORKDIR /app

# Dependencias del sistema necesarias en ejecución
RUN apt-get update && apt-get install -y \
    dos2unix \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no privilegiado
RUN useradd -ms /bin/bash appuser

# Copiar dependencias instaladas desde la etapa builder
COPY --from=builder /root/.local /home/appuser/.local

# Añadir pip local al PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Copiar TODO el proyecto
COPY . /app

# Copiar el entrypoint
COPY entrypoint.sh /entrypoint.sh

# Preparar permisos
RUN dos2unix /entrypoint.sh && \
    chmod +x /entrypoint.sh && \
    chown -R appuser:appuser /app /home/appuser/.local

USER appuser

EXPOSE 8501

ENTRYPOINT ["/entrypoint.sh"]