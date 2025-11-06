FROM python:3.11-slim

# 🧩 Instalar dependencias del sistema necesarias para WeasyPrint
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libffi-dev shared-mime-info \
    libgdk-pixbuf2.0-0 fonts-liberation libfreetype6 libjpeg62-turbo \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 📦 Crear directorio de trabajo
WORKDIR /app

# 🧰 Copiar requirements e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 📁 Copiar todo el código
COPY . .

# 🚀 Exponer el puerto y lanzar FastAPI
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
