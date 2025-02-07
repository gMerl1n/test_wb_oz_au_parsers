import uvicorn
import logging
from fastapi import FastAPI
from src.routes import _routes
from di_container.di_container import di_container
from config.settings import settings
from src.services.cookies_service.cookies_loader import oz_loader_cookies
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Remove all handlers associated with the root logger object.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    format='%(asctime)s - %(message)s | %(levelname)s ',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO
)

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    wb = di_container.get_parser_wb()
    oz = di_container.get_parser_oz()

    try:
        # Настройка и запуск планировщика
        scheduler.add_job(
            wb.parse_wb,
            trigger=IntervalTrigger(minutes=3),

        )
        scheduler.add_job(
            oz.parse_oz,
            trigger=IntervalTrigger(minutes=5),

        )
        scheduler.add_job(
            oz_loader_cookies.load_cookies,
            trigger=IntervalTrigger(minutes=7),

        )

        scheduler.start()
        logging.info("Планировщик запущен")
        yield
    except Exception as e:
        logging.error(f"Ошибка инициализации планировщика: {e}")
    finally:
        # Завершение работы планировщика
        scheduler.shutdown()
        logging.info("Планировщик обновления остановлен")


app = FastAPI(lifespan=lifespan)
app.include_router(_routes)

if __name__ == "__main__":
    logging.info(f'Start server {settings.server_settings.port}')
    uvicorn.run("main:app",
                host="0.0.0.0",
                port=settings.server_settings.port,
                log_level=settings.server_settings.log_level)
