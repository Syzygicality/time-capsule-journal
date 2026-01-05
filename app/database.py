from os import environ
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()

def getenv(config: str) -> str:
    value = environ.get(config)
    if not value:
        raise ValueError(f"{config} is missing from .env.")
    return value

DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_LOCATION = getenv("DB_LOCATION")
DB_PORT = getenv("DB_PORT")
DB_NAME = getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_LOCATION}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

def get_db():
    with Session(engine) as session:
        yield session
