FROM python:3.12-slim

# Evita crear archivos .pyc y fuerza salida inmediata de logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Dependencias del sistema (Añadimos dos2unix aquí)
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    gcc \
    build-essential \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto completo
COPY . .

# Copiar el script de inicio
COPY entrypoint.sh /entrypoint.sh

# Convertir saltos de línea a formato Linux y dar permisos de ejecución
RUN dos2unix /entrypoint.sh && chmod +x /entrypoint.sh

# Puerto de Streamlit
EXPOSE 8501

# Script que inicializa la aplicación
ENTRYPOINT ["/entrypoint.sh"]