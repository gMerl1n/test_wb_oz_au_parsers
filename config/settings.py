import json
import os
from pydantic import BaseModel
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

DATABASE_URL_POSTGRES = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(DATABASE_URL_POSTGRES, echo=False, future=True)
async_session = sessionmaker(autoflush=False, bind=engine, class_=AsyncSession)

config_path = os.path.join(BASE_DIR, 'config', "config.json")

with open(config_path) as file:
    config = json.load(file)
    parsers_settings: dict = config["parsers_settings"]
    wb_settings: dict = parsers_settings["WB"]
    oz_settings: dict = parsers_settings["OZ"]
    au_settings: dict = parsers_settings["AU"]
    server_settings: dict = config["server"]


class SettingsWB(BaseModel):
    limit_page: int
    limit_requests: int


class SettingsOZ(BaseModel):
    limit_page: int
    limit_requests: int


class SettingsAU(BaseModel):
    limit_page: int
    limit_requests: int


class SettingsServer(BaseModel):
    port: int
    log_level: str


class Settings:
    wb_settings = SettingsWB(limit_page=wb_settings["limit_page"], limit_requests=wb_settings["limit_requests"])
    oz_settings = SettingsOZ(limit_page=oz_settings["limit_page"], limit_requests=oz_settings["limit_requests"])
    au_settings = SettingsAU(limit_page=au_settings["limit_page"], limit_requests=au_settings["limit_requests"])
    server_settings = SettingsServer(port=server_settings["port"], log_level=server_settings["log_level"])


settings = Settings()
