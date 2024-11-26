from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.routes import _routes
from src.services.cookies_service.cookies_loader import oz_loader_cookies

app = FastAPI()
app.include_router(_routes)


scheduler = AsyncIOScheduler()

@app.on_event('startup')
async def run_cookies_oz_loader():
    scheduler.add_job(oz_loader_cookies.load_cookies, 'cron', minute='*/1')

scheduler.start()










