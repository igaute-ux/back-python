from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 🔹 Clase base para los modelos
Base = declarative_base()

# 🔹 Motor de conexión síncrono
engine = create_engine(
    settings.DATABASE_URL, 
    echo=True,  # útil en desarrollo para ver queries
    future=True
)

# 🔹 Session Local (síncrona)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# 🔹 Dependency para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
