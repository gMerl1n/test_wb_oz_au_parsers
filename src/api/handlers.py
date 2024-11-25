from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from container.di_container import di_container
from src.use_cases.product_use_cases import BaseUseCasesProduct
from settings.settings import PARSERS


router_product = APIRouter()


@router_product.get("/")
async def get_products_by_sign(sign: str,
                               use_cases_product: BaseUseCasesProduct = Depends(di_container.get_use_cases_product)):

    if sign not in PARSERS:
        raise HTTPException(status_code=400, detail=f"No products with such a sign: {sign} "
                                                    f"Try {PARSERS}")

    products_by_sign = use_cases_product.get_products_by_sign(sign=sign)
    return JSONResponse(status_code=200, content=products_by_sign)


@router_product.get("/")
async def get_all_products(use_cases_product: BaseUseCasesProduct = Depends(di_container.get_use_cases_product)):

    products = use_cases_product.get_all_products()
    return JSONResponse(status_code=200, content=products)

