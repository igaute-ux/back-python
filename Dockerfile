FROM python:3.11-slim

# Dependencias necesarias para WeasyPrint
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
    libfreetype6 \
    libjpeg62-turbo \
    libglib2.0-0 \
    libgobject-2.0-0 \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Railway asigna el puerto automáticamente
ENV PORT=${PORT:-8080}
EXPOSE $PORT

# Healthcheck para Railway
HEALTHCHECK CMD curl -f http://localhost:${PORT}/ || exit 1

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
