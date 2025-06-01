# Imagen base
FROM python:3.12-slim

# Evita preguntas interactivas
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema para WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    fonts-liberation \
    fonts-dejavu \
    libfontconfig1 \
    libfreetype6 \
 && apt-get clean && rm -rf /var/lib/apt/lists/*


# Crear carpeta para la app
WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto (si usas Uvicorn)
EXPOSE 8000

# Comando para ejecutar la app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
