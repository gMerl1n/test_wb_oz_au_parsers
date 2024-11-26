from abc import abstractmethod, ABC

from src.repository.product_repository.product_repository import BaseRepositoryProduct
from config.settings import async_session


class BaseUseCasesProduct(ABC):

    @abstractmethod
    async def add_product(self, new_product: dict):
        raise NotImplemented

    @abstractmethod
    async def add_products(self, new_products: list[dict]):
        raise NotImplemented

    @abstractmethod
    async def get_products_by_sign(self, sign: str):
        raise NotImplemented

    @abstractmethod
    async def get_all_products(self):
        raise NotImplemented


class UseCasesProduct(BaseUseCasesProduct):

    def __init__(self, repo_product: BaseRepositoryProduct):
        self.repo_product = repo_product

    async def add_product(self, new_product: dict):
        return await self.repo_product.add_product(async_session=async_session, new_product=new_product)

    async def add_products(self, new_products: list[dict]):
        return await self.repo_product.add_products(async_session=async_session, new_products=new_products)

    async def get_products_by_sign(self, sign: str):
        return await self.repo_product.get_products_by_sign(async_session=async_session, sign=sign)

    async def get_all_products(self):
        return await self.repo_product.get_all_products(async_session=async_session)