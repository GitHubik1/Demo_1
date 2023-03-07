from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

Base = declarative_base()

def create_tables(db: Session):
    Base.metadata.create_all(bind=db.bind)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def create_all():
    with Session(engine) as db:
        create_tables(db)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
