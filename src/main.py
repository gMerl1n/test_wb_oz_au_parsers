from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.routes import _routes
from container.di_container import di_container
from src.services.cookies_service.cookies_loader import oz_loader_cookies


app = FastAPI()
app.include_router(_routes)


scheduler = AsyncIOScheduler()


@app.on_event('startup')
async def run_wb_parser():
    w = di_container.get_parser_wb()
    scheduler.add_job(w.parse_wb, 'cron', minute='*/5')
    scheduler.start()


@app.on_event('startup')
async def run_oz_parser():
    pass


@app.on_event('startup')
async def run_au_parser():
    pass


@app.on_event('startup')
async def run_cookies_oz_loader():
    scheduler.add_job(oz_loader_cookies.load_cookies, 'cron', minute='*/3')
    scheduler.start()











