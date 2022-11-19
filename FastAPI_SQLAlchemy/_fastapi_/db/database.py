from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from FastAPI_SQLAlchemy.config import settings

engine = create_engine(settings.db_url)

SessionLocal = sessionmaker(engine, autocommit=False, autoflush=False)

Base = declarative_base()
