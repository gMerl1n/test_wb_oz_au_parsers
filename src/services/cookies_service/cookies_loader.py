import time
import logging

from datetime import datetime

from random import randint

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

from src.entitity.cookies import CookieObject
from src.use_cases.cookies_use_cases import BaseUseCasesCookies, CookiesUseCases
from src.entitity.cookies import CookiesObjectToUpdateExpire

logging.basicConfig(
    format='%(asctime)s - %(message)s | %(levelname)s ',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.INFO
)


class OZCookiesLoader:
    sign: str = "OZ"

    button: str = "reload-button"

    implicity_wait_limit: int = 120
    min_sleep_selenium_limit: int = 200  # milliseconds
    max_sleep_selenium_limit: int = 400  # milliseconds

    # минимум куки, которые должны быть в файле
    number_cookies_in_file: int = 2

    base_url: str = "https://www.ozon.ru/"

    cookies_use_cases: BaseUseCasesCookies = CookiesUseCases()

    def click_button(self, driver: webdriver.Firefox):

        button = driver.find_element(By.ID, self.button)
        if button is None:
            return

        button.click()
        driver.implicitly_wait(self.implicity_wait_limit)
        time.sleep(randint(self.min_sleep_selenium_limit, self.max_sleep_selenium_limit) / 1000)  # in seconds
        return driver

    def make_request_to_get_cookies(self) -> list[dict] | None:

        opts = Options()
        opts.add_argument("--headless")

        with webdriver.Firefox(options=opts) as driver:

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
                new_cookie_id = self.cookies_use_cases.create_new_cookies(cookies_object=new_cookie_obj)
                number_cookies_in_file += 1
                logging.info(f"В файл добавлены новые куки с id {new_cookie_id}. "
                             f"Теперь куков в файле: {number_cookies_in_file} "
                             f"Время: {round(time.time() - start, 2)} сек.")

        end = time.time() - start_all
        logging.info(f"Время для получения всех {self.number_cookies_in_file} куков: {round(end, 2)} сек. "
                     f"Number of bad requests: {counter_request_cookies}")

    def is_cookies_expired(self) -> None:

        cookies_objects = self.cookies_use_cases.get_all_cookies(provider_sign=self.sign)
        if cookies_objects is None:
            return

        now: float = datetime.now().timestamp()

        for cookie_obj in cookies_objects:

            for cookie in cookie_obj["cookies"]:
                if "expiry" not in cookie:
                    continue

                expire_cookies: float = cookie.get("expiry")
                if now > expire_cookies:
                    logging.info(f"{self.sign} "
                                 f"Cookies {cookie_obj['id']} have been expired. "
                                 f"Cookies expired at {datetime.fromtimestamp(expire_cookies)}")

                    data_to_update: CookiesObjectToUpdateExpire = CookiesObjectToUpdateExpire(id=cookie_obj["id"],
                                                                                              provider_sign=self.sign,
                                                                                              is_expired=True)

                    self.cookies_use_cases.update_cookie_object_by_id(data_to_update=data_to_update)

    def load_cookies(self) -> bool | None:

        number_cookies: int = self.cookies_use_cases.count_cookies_by_provider_sign(self.sign)

        # Проверяем, что все куки в файле валидны. Если какие-то не валидны, то удаляем их
        self.is_cookies_expired()
        self.cookies_use_cases.remove_all_expired_cookies(provider_sign=self.sign)
        self.cookies_use_cases.remove_all_non_working_cookies(provider_sign=self.sign)

        if number_cookies < self.number_cookies_in_file:
            self.load_new_cookies_in_file(number_cookies_in_file=number_cookies)
        else:
            return True


oz_loader_cookies = OZCookiesLoader()
