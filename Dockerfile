FROM python:3.11-slim

# 🧩 Instalar dependencias del sistema necesarias para WeasyPrint
RUN apt-get update && apt-get install -y \
    libcairo2 libpango-1.0-0 libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info \
    fonts-liberation libfreetype6 libjpeg62-turbo \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 📦 Crear directorio de trabajo
WORKDIR /app

# 🧰 Copiar requirements e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 📁 Copiar todo el código
COPY . .

# ✅ Railway asigna el puerto automáticamente
EXPOSE ${PORT}

# 🩺 Opcional: Healthcheck para que Railway detecte readiness
HEALTHCHECK CMD curl -f http://localhost:${PORT} || exit 1

# 🚀 Comando de arranque
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
