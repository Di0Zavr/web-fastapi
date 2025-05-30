import os
from sqlmodel import Session, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv(".env")

db_url = os.getenv('POSTGRES_URL')
async_db_url = os.getenv("ASYNC_POSTGRES_URL")

engine = create_engine(db_url, echo=False)

def get_session():
    with Session(engine) as session:
        yield session
