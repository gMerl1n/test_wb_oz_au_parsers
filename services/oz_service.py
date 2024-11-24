import time
from abc import abstractmethod, ABC
import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from random import randint, shuffle

import asyncio
import aiohttp

from entitity.product import Product
from use_cases.cookies_use_cases import CookiesUseCases
from entitity.cookies import CookieObject


logging.basicConfig(
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.WARNING
)


class BaseOZParser(ABC):

    @abstractmethod
    def parse_oz(self):
        pass


class OZParser(BaseOZParser):

    sign: str = "OZ"

    use_cases = CookiesUseCases()

    parser: str = "html.parser"

    list_products = []
    list_json_data = []

    url_product: str = "tj7_23 tile-hover-target j8t_23"
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

    def click_button(self, driver: webdriver.Firefox):

        button = driver.find_element(By.ID, self.button)
        if button is None:
            return

        button.click()
        time.sleep(5)
        return driver

    def make_request_to_get_cookies(self):

        with webdriver.Firefox() as driver:

            driver.get(url=self.base_url)
            driver.implicitly_wait(self.implicity_wait_limit)

            time.sleep(randint(self.min_sleep_selenium_limit, self.max_sleep_selenium_limit) / 1000)  # in seconds
            driver_with_cookies = self.click_button(driver)

            # Если куки пришли пустые
            if not driver_with_cookies.get_cookies():
                return
            else:
                return driver_with_cookies.get_cookies()

    def load_new_cookies_in_file(self, number_cookies_in_file: int) -> None:

        counter_request_cookies: int = 0

        # Если файл с куками не создан или в файле с куками мало куков
        start_all: float = time.time()
        while number_cookies_in_file < self.number_cookies_in_file:

            start = time.time()

            logging.debug(f"{self.sign} Making request to get captcha and cookies to write in the file")
            new_cookies = self.make_request_to_get_cookies()

            if new_cookies is None:
                logging.debug(f"Failed to get new cookies")

                counter_request_cookies += 1
                logging.info(f"Number of bad requests: {counter_request_cookies}")
                continue

            if not new_cookies:
                logging.debug(f"New cookies are empty: {new_cookies}")

                counter_request_cookies += 1
                logging.info(f"Number of bad requests: {counter_request_cookies}")
                continue

            try:
                new_cookie_obj: CookieObject = CookieObject(provider_sign=self.sign, cookies=new_cookies)
            except Exception as ex:
                logging.warning(f"Error: {ex}")
            else:
                new_cookie_id = self.use_cases.create_new_cookies(cookies_object=new_cookie_obj)
                number_cookies_in_file += 1
                logging.info(f"В файл добавлены новые куки с id {new_cookie_id}. "
                             f"Теперь куков в файле: {number_cookies_in_file} "
                             f"Время: {round(time.time() - start, 2)} сек.")

        end = time.time() - start_all
        logging.info(f"Время для получения всех {self.number_cookies_in_file} куков: {round(end, 2)} сек. "
                     f"Number of bad requests: {counter_request_cookies}")

    @staticmethod
    def make_request_to_get_urls_products(cookies: list[dict], url):

        with webdriver.Firefox() as driver:

            cookie = [c["cookies"] for c in cookies]

            for c1 in cookie:

                driver.get(url)
                time.sleep(4)
                driver.delete_all_cookies()

                for c2 in c1:
                    driver.add_cookie(c2)

                time.sleep(4)
                driver.get(url)

                return driver.page_source

    def parse_oz(self):

        number_cookies: int = self.use_cases.count_cookies_by_provider_sign(self.sign)
        print("number_cookies", number_cookies)

        if number_cookies < self.number_cookies_in_file:
            self.load_new_cookies_in_file(number_cookies_in_file=number_cookies)

        # Когда убедились, что в файле есть необходимое количество валидных кук, то
        # начинаем их использовать для парсинга ссылок
        cookies: list[dict] = self.use_cases.get_all_cookies(provider_sign=self.sign)
        shuffle(cookies)

        urls = self.build_urls_pages()

        for url in urls:
            page_source = self.make_request_to_get_urls_products(cookies=cookies, url=url)

            soup = self.to_bs4(page_source)

            urls_products = soup.find_all("a", class_=self.url_product)

            for url_pr in urls_products:

                api_url_product = self.api_url + url_pr["href"]

                self.urls_products.append(api_url_product)

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

    def get_product_url(self, widget_states: dict):
        pass

    def count_in_stock(self, widget_states: dict):

        big_promo = widget_states.get("bigPromoPDP-3422454-default-1")
        if not big_promo:
            return
        else:
            json_title = self.to_json(big_promo)
            stock_text = json_title.get("stockNumber")
            in_stock = stock_text.get("text") if stock_text else ""
            return in_stock

    def parse_product(self, data):

        widget_states = data.get("widgetStates")
        if not widget_states:
            return

        name = self.get_product_name(widget_states)
        if name is None:
            logging.warning(f"Failed to get name product")
            return

        price_with_discount = self.get_discount_price(widget_states)
        if price_with_discount is None:
            logging.warning(f"Failed to get discount price")
            return

        full_price = self.get_original_price(widget_states)
        if full_price is None:
            logging.warning(f"Failed to get full price")
            return

        in_stock = self.count_in_stock(widget_states)
        if in_stock is None:
            logging.warning(f"Failed to get in_stock")
            return

        self.list_products.append(
            Product(
                name=name,
                full_price=full_price,
                price_with_discount=price_with_discount,
                in_stock=int(in_stock),
                url=""
            )
        )

    async def get_product_data(self, sess, url):
        async with sess.get(url=url) as response:

            if response.status != 200:
                return

            data: dict = await response.json()

            self.list_json_data.append(data)

    async def async_func(self):

        async with aiohttp.ClientSession() as sess:
            tasks: list = []
            for url in self.urls_products:
                task = asyncio.create_task(self.get_product_data(sess, url))
                tasks.append(task)

            await asyncio.gather(*tasks)

        for data in self.list_json_data:
            await asyncio.to_thread(self.parse_product, data)


obj = OZParser()
obj.parse_oz()
print(obj.urls_products)
asyncio.run(obj.async_func())
for i in obj.list_products:
    print(i)
