import asyncio
import aiohttp

from abc import abstractmethod, ABC
from entitity.product import Product


class BaseWBParser(ABC):

    @abstractmethod
    def parse_wb(self):
        pass


class WBParser(BaseWBParser):

    list_products: list[Product] = []
    list_json_pages: list[dict] = []
    list_urls: list[str] = []

    base_wb_url: str = "https://catalog.wb.ru/"
    page: int = 1

    num_products_on_page: int = 99

    def build_wb_api_url(self) -> str:

        if self.page == 1:
            api_url: str = (f"{self.base_wb_url}catalog/new_year4/v2/"
                            f"catalog?ab_testing=false&appType=1&cat=130404&curr=rub&dest=-5818883&sort=popular&spp=30")
            return api_url
        else:
            api_url: str = (f"{self.base_wb_url}catalog/new_year4/v2/"
                            f"catalog?ab_testing=false&appType=1&cat=130404&curr=rub&dest=-5818883&page={self.page}&sort=popular&spp=30")
            return api_url

    def get_page_numbers(self, data_products: dict) -> int | None:

        data: dict = data_products.get("data")

        if data is None:
            return

        num_products: int = data.get("total")
        if num_products is None:
            return

        return int(num_products // self.num_products_on_page)

    def build_urls(self) -> None:

        for _ in range(1, 4):

            api_url = self.build_wb_api_url()
            self.list_urls.append(api_url)
            self.page += 1

    @staticmethod
    def get_products(data_products: dict) -> list[dict] | None:

        data = data_products.get("data")

        if not data:
            return

        products = data.get("products")
        if not products:
            return

        return products

    @staticmethod
    def create_product_object(product_wb: dict) -> Product:

        return Product(
            name=product_wb.get("name"),
            full_price=product_wb.get("sizes")[0].get("price").get("basic") // 100,
            price_with_discount=product_wb.get("sizes")[0].get("price").get("product") // 100,
            url=f"https://www.wildberries.ru/catalog/{product_wb.get('id')}/detail.aspx",
            in_stock=product_wb.get("totalQuantity")
        )

    def parse_products(self) -> None:

        for json_page in self.list_json_pages:

            products = self.get_products(json_page)
            if products is None:
                continue

            for pr in products:
                new_product = self.create_product_object(pr)
                self.list_products.append(new_product)

    async def get_product_data(self, sess: aiohttp.ClientSession, url: str):
        async with sess.get(url=url) as response:

            if response.status != 200:
                return

            data: dict = await response.json()

            self.list_json_pages.append(data)

    async def parse_wb(self) -> None:
        async with aiohttp.ClientSession() as sess:
            tasks: list = []
            for url in self.list_urls:
                task = asyncio.create_task(self.get_product_data(sess, url))
                tasks.append(task)

            await asyncio.gather(*tasks)

        for pr in self.list_json_pages:
            await asyncio.to_thread(self.parse_products)

obj = WBParser()
obj.build_urls()

asyncio.run(obj.parse_wb())

print(obj.list_products)


