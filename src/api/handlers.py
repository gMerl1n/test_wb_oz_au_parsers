from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Depends
from src.services.wb_service import BaseWBParser
from container.di_container import di_container


router_product = APIRouter()


@router_product.get("/")
async def run_wb_parser(sign: str,
                        parser_wb_service: BaseWBParser = Depends(di_container.get_parser_wb)):
    pass


@router_product.get("/")
async def run_oz_parser(sign: str):
    pass


@router_product.get("/")
async def run_au_parser(sign: str):
    pass


