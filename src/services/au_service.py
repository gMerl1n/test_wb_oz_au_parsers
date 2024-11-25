import logging
from abc import abstractmethod, ABC
import requests
import aiohttp
import asyncio
from src.entitity.product import Product


logging.basicConfig(
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.WARNING
)


class BaseAUParser(ABC):

    @abstractmethod
    def parse_au(self):
        pass


class AUParser(BaseAUParser):

    sign: str = "AU"

    api_url_shops: str = 'https://www.auchan.ru/v1/shops'
    api_url_products: str = 'https://www.auchan.ru/v1/catalog/products'

    list_json_data: list[dict] = []
    list_parsed_products: list[Product] = []
    list_api_urls_merchants: list[dict] = []

    def get_shops_ids(self) -> list[int]:

        pr = {"https": "http://B6XsHR:UXEQr3@185.73.181.35:8000"}

        list_shop_ids: list[int] = []
        print(list_shop_ids)
        response: requests.Response = requests.get(url=self.api_url_shops, timeout=12, proxies=pr)
        response_json: dict = response.json()
        print("response_json")
        for shop in response_json['shops']:
            list_shop_ids.append(shop['merchant_id'])

        return list_shop_ids

    def parse_au(self):

        shops_ids: list[int] = self.get_shops_ids()

        print(shops_ids)

        for shop_id in shops_ids[:10]:

            params = {
                'merchantId': int(shop_id),
                'perPage': 100
            }

            body = {
                "filter": {"category": "molochnye_kokteyli_napitki", "promo_only": False, "active_only": False,
                           "cashback_only": False}
            }

            # response = requests.get(url='https://www.auchan.ru/v1/catalog/products', params=params, json=body)

            # print(response.json())

            # with open(f"auchan{shop_id}.json", "w") as file:
                 # json.dump(response.json(), file, indent=4, ensure_ascii=False)

            self.list_api_urls_merchants.append({
                "params": params,
                "body": body,
            })

    def parse_product(self, product_data: dict) -> Product:

        product: Product = Product(
            name=product_data.get("title"),
            full_price=product_data.get("price").get("value"),
            price_with_discount=product_data.get("oldPrice").get("oldPrice"),
            url=f'https://www.auchan.ru/product/{product_data.get("code")}/',
            in_stock=product_data.get("stock").get("qty"),
            provider=self.sign
            )

        self.list_parsed_products.append(product)


    async def get_product_data(self, sess, params_requests):

        params = params_requests["params"]
        body = params_requests["body"]

        async with sess.get(url=self.api_url_products, params=params, data=body) as response:
            if response.status != 200:
                return

            data: dict = await response.json()

            list_items: list[dict] = data.get("items")
            if list_items:
                self.list_json_data.extend(list_items)

    async def async_func(self):

        async with aiohttp.ClientSession() as sess:
            tasks: list = []
            for params_requests in self.list_api_urls_merchants:
                task = asyncio.create_task(self.get_product_data(sess, params_requests))
                tasks.append(task)

            await asyncio.gather(*tasks)

        for data in self.list_json_data:
            await asyncio.to_thread(self.parse_product, data)


