# Adaptia Backend

Backend minimalista construido con FastAPI, LangChain y Supabase.

## 🚀 Características

- **FastAPI**: Framework web moderno y rápido para Python
- **LangChain**: Framework para aplicaciones de IA
- **Supabase**: Base de datos PostgreSQL como servicio
- **Arquitectura modular**: Estructura organizada con routers y separación de responsabilidades

## 📋 Requisitos

- Python 3.8+
- Las dependencias ya están en `requirements.txt`

## ⚙️ Configuración

1. **Copiar el archivo de variables de entorno:**

   ```bash
   cp env.example .env
   ```

2. **Configurar las variables en `.env`:**

   ```env
   # Supabase Configuration
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key

   # OpenAI Configuration (para LangChain)
   OPENAI_API_KEY=your_openai_api_key

   # Server Configuration
   HOST=0.0.0.0
   PORT=8000
   DEBUG=True
   ```

3. **Obtener credenciales de Supabase:**
   - Ve a [supabase.com](https://supabase.com)
   - Crea un nuevo proyecto
   - Copia la URL del proyecto y la anon key desde Settings > API

## 🏃‍♂️ Ejecutar el proyecto

### Opción 1: Con Uvicorn (Recomendado)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Opción 2: Con FastAPI CLI

```bash
fastapi dev main.py
```

### Opción 3: Con Python

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Endpoints

- **GET /** - Endpoint raíz
- **GET /api/v1/** - API endpoints (estructura modular)
- **GET /docs** - Documentación automática de la API (Swagger UI)

> **Nota**: Este es solo el setup inicial del proyecto. Los endpoints específicos se implementarán según las necesidades del proyecto.

## 📁 Estructura del proyecto

```
adaptia--backend/
├── main.py                               # Archivo principal de FastAPI
├── app/                                  # Aplicación principal
│   ├── __init__.py
│   └── api/                              # API endpoints
│       ├── __init__.py
│       └── v1/                           # Versión 1 de la API
│           ├── __init__.py
│           └── router.py                 # Router principal de la API
├── config/                               # Configuraciones del proyecto
│   ├── __init__.py
│   ├── database.py                       # Configuración de Supabase
│   └── langchain_config.py               # Configuración de LangChain
├── requirements.txt                      # Dependencias del proyecto
├── env.example                           # Ejemplo de variables de entorno
├── .gitignore                            # Archivos a ignorar por Git
└── README.md                             # Este archivo
```

## 🏗️ Arquitectura del proyecto

El proyecto sigue una arquitectura modular y escalable:

- **`main.py`**: Punto de entrada de la aplicación
- **`app/`**: Lógica principal de la aplicación
  - **`app/api/`**: Endpoints de la API organizados por versiones
  - **`app/api/v1/`**: Primera versión de la API
- **`config/`**: Configuraciones centralizadas
- **Separación de responsabilidades**: Cada módulo tiene una función específica

## 🔧 Desarrollo

Para agregar nuevas funcionalidades:

1. **Nuevos endpoints**: Agregar en `app/api/v1/router.py` o crear nuevos routers
2. **Configuraciones**: Agregar en el directorio `config/`
3. **Modelos de datos**: Crear en un directorio `models/`
4. **Servicios**: Crear en un directorio `services/`
5. **Base de datos**: Agregar en `config/database.py`
6. **LangChain**: Configurar en `config/langchain_config.py`

## 📚 Documentación

- **FastAPI**: https://fastapi.tiangolo.com/
- **LangChain**: https://python.langchain.com/
- **Supabase**: https://supabase.com/docs

## 🆘 Troubleshooting

### Error de conexión a Supabase

- Verifica que `SUPABASE_URL` y `SUPABASE_KEY` estén correctos
- Asegúrate de que el proyecto de Supabase esté activo

### Error de LangChain

- Verifica que `OPENAI_API_KEY` esté configurado
- La API key debe ser válida y tener créditos disponibles

### Puerto ocupado

- Cambia el puerto en `.env` o usa otro puerto disponible
- Mata procesos que puedan estar usando el puerto 8000
