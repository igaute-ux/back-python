FROM python:3.11-slim

# 🧩 Dependencias necesarias para WeasyPrint
RUN apt-get update && apt-get install -y \
    libcairo2 libpango-1.0-0 libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info \
    fonts-liberation libfreetype6 libjpeg62-turbo \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 📦 Crear directorio de trabajo
WORKDIR /app

# 🧰 Copiar requirements e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 📁 Copiar todo el código
COPY . .

# ✅ Railway define PORT dinámicamente (ej: 8080)
EXPOSE $PORT

# 🧠 Usa la variable $PORT si existe, o 8000 localmente
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
