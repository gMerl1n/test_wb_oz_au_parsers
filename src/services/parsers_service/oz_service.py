import time
import json
from abc import ABC, abstractmethod
from random import randint, shuffle

import asyncio
import aiohttp

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from src.use_cases.cookies_use_cases import CookiesUseCases
from src.use_cases.product_use_cases import BaseUseCasesProduct
from src.entitity.product import Product
from config.settings import config_parsers, log


class BaseOZParser(ABC):

    @abstractmethod
    def parse_oz(self):
        pass


class OZParser:

    sign: str = "OZ"

    use_cases = CookiesUseCases()

    parser: str = "html.parser"

    list_products = []
    list_json_data = []

    url_product: str = "j9t_23 tile-hover-target ju_23"
    api_url: str = "https://www.ozon.ru/api/composer-api.bx/page/json/v2?url="

    implicity_wait_limit: int = 120
    min_sleep_selenium_limit: int = 200  # milliseconds
    max_sleep_selenium_limit: int = 400  # milliseconds

    urls_products: list = []

    # минимум куки, которые должны быть в файле
    number_cookies_in_file: int = 2

    base_url: str = "https://www.ozon.ru/"
    coffee_url: str = "https://www.ozon.ru/category/kofe/"

    button: str = "reload-button"

    page: int = 1

    def __init__(self, product_use_cases: BaseUseCasesProduct) -> None:
        self.config = config_parsers
        self.product_use_cases = product_use_cases

    @staticmethod
    def to_json(data: str):
        return json.loads(data)

    def to_bs4(self, page_source: str):
        return BeautifulSoup(page_source, self.parser)

    def build_url(self):

        url = f"https://www.ozon.ru/category/kofe/?page={self.page}"
        return url

    def build_urls_pages(self):

        pages = []

        for _ in range(1, 3):
            url = self.build_url()
            pages.append(url)

        return pages

    def make_request_to_get_urls_products(self, cookies: list[dict], url):

        opts = Options()
        opts.add_argument("--headless")

        with webdriver.Firefox(options=opts) as driver:

            cookie = [c["cookies"] for c in cookies]

            for c1 in cookie:

                driver.get(url)
                driver.implicitly_wait(self.implicity_wait_limit)
                time.sleep(randint(self.min_sleep_selenium_limit, self.max_sleep_selenium_limit) / 1000)  # in seconds
                driver.delete_all_cookies()

                for c2 in c1:
                    driver.add_cookie(c2)

                driver.get(url)
                driver.implicitly_wait(self.implicity_wait_limit)
                time.sleep(randint(self.min_sleep_selenium_limit, self.max_sleep_selenium_limit) / 1000)  # in seconds

                return driver.page_source

    def get_api_url_products(self) -> None:

        # Когда убедились, что в файле есть необходимое количество валидных кук, то
        # начинаем их использовать для парсинга ссылок
        cookies: list[dict] = self.use_cases.get_all_cookies(provider_sign=self.sign)
        log.info(f"{self.sign} Куки в файле для парсинга: {len(cookies)}")
        shuffle(cookies)

        urls = self.build_urls_pages()
        log.info(f"{self.sign} Number pages to parse {len(urls)}")

        for url in urls:
            page_source = self.make_request_to_get_urls_products(cookies=cookies, url=url)

            soup = self.to_bs4(page_source)

            urls_products = soup.find_all("a", class_=self.url_product)

            for url_pr in urls_products:
                api_url_product = self.api_url + url_pr["href"]

                self.urls_products.append(api_url_product)

        log.info(f"{self.sign} Number urls of products to parse {len(self.urls_products)}")

    def get_original_price(self, widget_states: dict):

        web_price = widget_states.get("webPrice-3121879-default-1")
        if not web_price:
            return
        else:
            json_title = self.to_json(web_price)
            full_price = json_title.get("originalPrice")
            return full_price if full_price else None

    def get_discount_price(self, widget_states: dict):

        web_price = widget_states.get("webPrice-3121879-default-1")
        if not web_price:
            return
        else:
            json_title = self.to_json(web_price)
            price_with_discount = json_title.get("price")
            return price_with_discount if price_with_discount else None

    def get_product_name(self, widget_states: dict):

        web_product_heading = widget_states.get("webProductHeading-3385933-default-1")
        if not web_product_heading:
            return
        else:
            json_title = self.to_json(web_product_heading)
            name = json_title.get("title")
            return name if name else None

    def count_in_stock(self, widget_states: dict):

        big_promo = widget_states.get("bigPromoPDP-3422454-default-1")
        if not big_promo:
            return
        else:
            json_title = self.to_json(big_promo)
            stock_text = json_title.get("stockNumber")
            in_stock = stock_text.get("text") if stock_text else ""
            if not in_stock:
                return
            else:
                in_stock_num = [num for num in in_stock if num.isdigit()]
                return int(''.join(in_stock_num))

    @staticmethod
    def get_product_url(data):
        seo: dict = data.get("seo")
        link: list = seo.get("link")
        href = link[0].get("href")
        return href if href else ""

    def parse_product(self, data):

        widget_states = data.get("widgetStates")
        if not widget_states:
            log.warning(f"{self.sign} "
                        f"Failed to get widget_states. Impossible to parse other product name, price, url")
            return

        name = self.get_product_name(widget_states)
        if name is None:
            log.debug(f"Failed to get name product")
            return

        price_with_discount = self.get_discount_price(widget_states)
        if price_with_discount is None:
            log.debug(f"Failed to get discount price")
            return

        full_price = self.get_original_price(widget_states)
        if full_price is None:
            log.debug(f"Failed to get full price")
            return

        in_stock = self.count_in_stock(widget_states)
        if in_stock is None:
            log.debug(f"Failed to get in_stock")

        url: str = self.get_product_url(data)

        new_product: Product = Product(
                name=name,
                full_price=int(full_price.split()[0]),
                price_with_discount=int(price_with_discount.split()[0]),
                in_stock=in_stock,
                url=url,
                sign=self.sign
            )

        self.list_products.append(new_product.to_dict())

    async def insert_products_in_db(self):
        await self.product_use_cases.add_products(self.list_products)

    async def get_product_data(self, sess, url):
        async with sess.get(url=url) as response:

            if response.status != 200:
                return

            data: dict = await response.json()

            self.parse_product(data)

    async def parse_oz(self):

        limit_requests: int = self.config[self.sign]["limit_requests"]

        # Получаем ссылки на товары, формируем их них ссылки для API Ozon
        await asyncio.to_thread(self.get_api_url_products)

        async with aiohttp.ClientSession() as sess:
            tasks: list = []
            for url in self.urls_products:
                task = asyncio.create_task(self.get_product_data(sess, url))
                tasks.append(task)

            chunked_tasks = [tasks[offset:limit_requests + offset] for offset in range(0, len(tasks), limit_requests)]

            for chunk in chunked_tasks:

                await asyncio.gather(*chunk)

            log.info(f"{self.sign} Number of parsed products: {len(self.list_products)}")

            await self.insert_products_in_db()

            log.info(f"{self.sign} Products added into DB")




