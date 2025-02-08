import logging
import requests
import aiohttp
import asyncio

from src.use_cases.product_use_cases import BaseUseCasesProduct
from abc import abstractmethod, ABC
from config.settings import Settings
from src.entitity.product import Product

logging.basicConfig(
    format='%(asctime)s - %(message)s | %(levelname)s ',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO
)


class BaseAUParser(ABC):

    @abstractmethod
    def parse_au(self) -> None:
        pass


class AUParser(BaseAUParser):
    sign: str = "AU"

    category: str = "molochnye_kokteyli_napitki"

    api_url_shops: str = 'https://www.auchan.ru/v1/shops'
    api_url_products: str = 'https://www.auchan.ru/v1/catalog/products'

    list_json_data_from_au: list[dict] = []
    list_parsed_products: list[dict] = []

    def __init__(self, product_use_cases: BaseUseCasesProduct, settings: Settings) -> None:
        self.settings = settings
        self.product_use_cases = product_use_cases

    def get_shops_ids(self) -> list[int]:

        list_shop_ids: list[int] = []
        response: requests.Response = requests.get(url=self.api_url_shops, timeout=12)
        response_json: dict = response.json()
        for shop in response_json['shops']:
            list_shop_ids.append(shop['merchant_id'])

        return list_shop_ids

    def get_list_api_products(self) -> list[dict]:

        list_api_urls_merchants: list[dict] = []

        shops_ids: list[int] = self.get_shops_ids()

        for shop_id in shops_ids[:10]:
            params = {
                'merchantId': int(shop_id),
                'perPage': 100
            }

            body = {
                "filter": {"category": self.category, "promo_only": False, "active_only": False,
                           "cashback_only": False}
            }

            list_api_urls_merchants.append({
                "params": params,
                "body": body,
            })

            return list_api_urls_merchants

    def parse_product(self, product_data: dict) -> None:

        product: Product = Product(
            name=product_data.get("title"),
            full_price=product_data.get("price").get("value"),
            price_with_discount=product_data.get("oldPrice").get("oldPrice"),
            url=f'https://www.auchan.ru/product/{product_data.get("code")}/',
            in_stock=product_data.get("stock").get("qty"),
            sign=self.sign
        )

        self.list_parsed_products.append(product.to_dict())

    async def insert_products_in_db(self) -> None:
        await self.product_use_cases.add_products(self.list_parsed_products)

    async def get_product_data(self, sess, params_requests: dict) -> None:

        params = params_requests["params"]
        body = params_requests["body"]

        async with sess.get(url=self.api_url_products, params=params, data=body) as response:
            if response.status != 200:
                return

            data: dict = await response.json()

            list_items: list[dict] = data.get("items")
            if list_items:
                self.list_json_data_from_au.extend(list_items)

    async def parse_au(self) -> None:

        limit_requests: int = self.settings.au_settings.limit_requests

        list_api_urls_ = self.get_list_api_products()

        async with aiohttp.ClientSession() as sess:
            tasks: list = []
            for params_requests in list_api_urls_:
                task = asyncio.create_task(self.get_product_data(sess, params_requests))
                tasks.append(task)

            chunked_tasks = [tasks[offset:limit_requests + offset] for offset in range(0, len(tasks), limit_requests)]
            logging.info(f"{self.sign} Number of chunks: {len(chunked_tasks)}")

            for chunk in chunked_tasks[:2]:
                await asyncio.gather(*chunk)

        for data in self.list_json_data_from_au:
            await asyncio.to_thread(self.parse_product, data)

        await self.insert_products_in_db()
