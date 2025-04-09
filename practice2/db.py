from sqlmodel import SQLModel, Session, create_engine
import models

db_url = 'postgresql://postgres:postgres@localhost:5432/practice_db'
engine = create_engine(db_url, echo=True)

def init_db():
    # SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
