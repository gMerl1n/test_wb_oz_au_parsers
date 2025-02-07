from fastapi import FastAPI
from src.routes import _routes
from di_container.di_container import di_container
from src.services.cookies_service.cookies_loader import oz_loader_cookies
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config.settings import log

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
        log.info("Планировщик запущен")
        yield
    except Exception as e:
        log.error(f"Ошибка инициализации планировщика: {e}")
    finally:
        # Завершение работы планировщика
        scheduler.shutdown()
        log.info("Планировщик обновления остановлен")


app = FastAPI(lifespan=lifespan)
app.include_router(_routes)
