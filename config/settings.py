import json
import os
import logging
from typing import Literal
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


PARSERS: tuple = ("WB", "OZ", "AU")


BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)


POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

DATABASE_URL_POSTGRES = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}?async_fallback=True"

engine = create_async_engine(DATABASE_URL_POSTGRES, echo=False, future=True)
async_session = sessionmaker(autoflush=False, bind=engine, class_=AsyncSession)


config_path = os.path.join(BASE_DIR, 'config', "config.json")

with open(config_path) as file:
    config_parsers = json.load(file)


def init_logger(
    name: str, level: int | Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'] = logging.INFO
):
    """
    Configure and get logger by provided name.
    """
    if isinstance(level, str):
        level = getattr(logging, level)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    return logger


log = init_logger("parsers", "INFO")