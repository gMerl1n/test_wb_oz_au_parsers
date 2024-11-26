from fastapi import FastAPI
from src.routes import _routes


app = FastAPI()
app.include_router(_routes)














