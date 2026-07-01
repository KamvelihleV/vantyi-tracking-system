"""
Database connection setup.

Uses SQLite locally for easy development and demoing.
To deploy to Azure SQL, just change DATABASE_URL to something like:

    mssql+pyodbc://<user>:<password>@<server>.database.windows.net:1433/<db>?driver=ODBC+Driver+17+for+SQL+Server

Everything else (models, routes) stays the same — that's the point of
using SQLAlchemy as the ORM layer.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./vantyi.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
