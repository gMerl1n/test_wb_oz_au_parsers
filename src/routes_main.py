from fastapi import APIRouter
from src.api.handlers import router_product


routes = APIRouter()

routes.include_router(router=router_product, prefix="/products_parsers")