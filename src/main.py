from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.routes import _routes
from container.di_container import di_container


app = FastAPI()
app.include_router(_routes)


scheduler = AsyncIOScheduler()


@app.on_event('startup')
async def run_wb_parser():
    wq = di_container.get_parser_wb()
    scheduler.add_job(wq.parse_wb, 'cron', minute='*/1')
    scheduler.start()


@app.on_event('startup')
async def run_oz_parser():
    pass


@app.on_event('startup')
async def run_au_parser():
    pass










