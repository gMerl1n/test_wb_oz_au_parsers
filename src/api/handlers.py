from fastapi import APIRouter, HTTPException, Depends

from container.di_container import di_container
from src.use_cases.product_use_cases import BaseUseCasesProduct
from src.services.parsers_service.wb_service import BaseWBParser
from src.services.parsers_service.oz_service import BaseOZParser
from src.services.cookies_service.cookies_loader import oz_loader_cookies
from config.settings import PARSERS


router_product = APIRouter()


@router_product.get("/products_by_sign/{sign}")
async def get_products_by_sign(sign: str,
                               use_cases_product: BaseUseCasesProduct = Depends(di_container.get_use_cases_product)):

    if sign not in PARSERS:
        raise HTTPException(status_code=400, detail=f"No products with such a sign: {sign} "
                                                    f"Try {PARSERS}")

    products_by_sign = await use_cases_product.get_products_by_sign(sign=sign)
    return products_by_sign


@router_product.get("/all_products")
async def get_all_products(use_cases_product: BaseUseCasesProduct = Depends(di_container.get_use_cases_product)):

    products = await use_cases_product.get_all_products()
    return products


@router_product.post("/run_wb")
async def run_wb(wb_parser: BaseWBParser = Depends(di_container.get_parser_wb)):

    await wb_parser.parse_wb()
    return True

@router_product.post("/run_oz")
async def run_oz(oz_parser: BaseOZParser = Depends(di_container.get_parser_oz)):

    await oz_parser.parse_oz()
    return True


@router_product.post("/load_oz_cookies")
async def load_oz_cookies():

    result = oz_loader_cookies.load_cookies()
    return result