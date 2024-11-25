from fastapi import FastAPI
from src.routes import routes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.services.wb_service import WBParser
from container.di_container import di_container


w = WBParser()


app = FastAPI()
app.include_router(routes)


@app.on_event('startup')
async def update_cars_locations():
    scheduler = AsyncIOScheduler()
    wq = di_container.get_parser_wb()
    scheduler.add_job(wq.parse_wb, 'cron', minute='*/1')
    scheduler.start()


