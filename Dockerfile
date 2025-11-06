FROM python:3.11-slim

# Dependencias de sistema necesarias para WeasyPrint
RUN apt-get update && apt-get install -y \
    libcairo2 libpango-1.0-0 libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info \
    fonts-liberation libfreetype6 libjpeg62-turbo curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# ⚙️ Dejá que Railway asigne el puerto dinámico
ENV PORT=${PORT:-8000}
EXPOSE ${PORT}

# 🚀 Iniciar Uvicorn con el puerto asignado
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
