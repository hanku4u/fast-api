from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# ===========================sqlite database connection==========================
# SQLALCHEMY_DATABASE_URL = 'sqlite:///./todos.db'

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# ===========================sqlite database connection==========================


# ===========================postgresql database connection==========================
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1bigone@localhost:5432/TodoApplicationDatabase"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
# ===========================postgresql database connection==========================

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
