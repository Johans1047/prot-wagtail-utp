FROM python:3.11-slim

# Metadata
LABEL maintainer="JIC Development Team"
LABEL description="Wagtail CMS with MinIO and PostgreSQL"
LABEL version="1.0.0"

# Evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    curl \
    wget \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt /app/requirements.txt

# Actualizar pip e instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copiar archivos del proyecto
COPY ./mysite /app/mysite

# Crear directorios necesarios
RUN mkdir -p /app/mysite/staticfiles 
# /app/media

# Exponer puerto
EXPOSE 8000
EXPOSE 35729

# Comando por defecto
CMD ["python", "mysite/manage.py", "runserver", "0.0.0.0:8000"]