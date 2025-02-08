from abc import abstractmethod, ABC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.product_repository.product_model import Product


class BaseRepositoryProduct(ABC):

    @abstractmethod
    async def add_product(self, async_session, new_product: dict) -> None:
        raise NotImplemented

    @abstractmethod
    async def add_products(self, async_session, new_products: list[dict]) -> None:
        raise NotImplemented

    @abstractmethod
    def get_product_by_id(self) -> Product | None:
        raise NotImplemented

    @abstractmethod
    async def get_products_by_sign(self, async_session, sign: str) -> list[Product]:
        raise NotImplemented

    @abstractmethod
    async def get_all_products(self, async_session) -> list[Product]:
        raise NotImplemented

    @abstractmethod
    def update_product_by_id(self):
        raise NotImplemented


class RepositoryProduct(BaseRepositoryProduct):

    async def add_product(self, async_session, new_product: dict) -> None:
        async with async_session() as session:
            session.add(Product(**new_product))
            await session.commit()

    async def add_products(self, async_session, new_products: list[dict]) -> None:

        products_to_add = [Product(**p) for p in new_products]

        async with async_session() as session:
            session.add_all(products_to_add)
            await session.commit()

    def get_product_by_id(self):
        pass

    async def get_products_by_sign(self, async_session, sign: str) -> list:
        async with async_session() as session:
            query = select(Product).where(Product.sign == sign)
            products_by_sign = await session.execute(query)
            return products_by_sign.scalars().all()

    async def get_all_products(self, async_session) -> list:
        async with async_session() as session:
            query = select(Product)
            products = await session.execute(query)
            return products.scalars().all()

    def update_product_by_id(self):
        pass
