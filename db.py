from sqlmodel import create_engine, SQLModel,Session
from config import DATABASE_URL


if DATABASE_URL is None:
    raise ValueError("DATABASE_URL must be set")

engine = create_engine(DATABASE_URL)

def create_tables():

  SQLModel.metadata.create_all(engine)

def get_session():
  with Session(engine) as session:
    yield session


    