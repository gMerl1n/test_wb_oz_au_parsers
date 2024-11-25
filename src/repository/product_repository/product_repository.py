from abc import abstractmethod, ABC
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.product_repository.product_model import Product


class BaseRepositoryProduct(ABC):

    @abstractmethod
    async def add_product(self, async_session, new_product: dict):
        raise NotImplemented

    @abstractmethod
    async def add_products(self, async_session, new_products: list[dict]):
        raise NotImplemented

    @abstractmethod
    def get_product_by_id(self):
        raise NotImplemented

    @abstractmethod
    async def get_products_by_sign(self, async_session: AsyncSession, sign: str):
        raise NotImplemented

    @abstractmethod
    async def get_all_products(self, async_session: AsyncSession):
        raise NotImplemented

    @abstractmethod
    def update_product_by_id(self):
        raise NotImplemented


class RepositoryProduct(BaseRepositoryProduct):

    async def add_product(self, async_session,  new_product: dict):

        async with async_session() as session:
            new_product["created_at"] = datetime.now()
            session.add(Product(**new_product))
            await session.commit()

    async def add_products(self, async_session, new_products: list[dict]):

        np = []

        for p in new_products:
            p["created_at"] = datetime.now()
            np.append(p)

        res = [Product(**p) for p in np]

        async with async_session() as session:
            session.add_all(res)
            await session.commit()

    def get_product_by_id(self):
        pass

    async def get_products_by_sign(self, async_session: AsyncSession, sign: str):
        query = select(Product).where(Product.provider == sign)
        products_by_sign = await async_session.execute(query)
        return products_by_sign.scalars().all()

    async def get_all_products(self, async_session: AsyncSession):
        query = select(Product)
        products = await async_session.execute(query)
        return products.scalars().all()

    def update_product_by_id(self):
        pass