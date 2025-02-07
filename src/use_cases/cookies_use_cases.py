import logging

from abc import abstractmethod, ABC
from typing import Union, List

from src.repository.cookies_repository.cookies_repository import BaseRepositoryCookies, RepositoryCookies
from src.entitity.cookies import CookieObject, CookiesObjectToUpdateExpire, CookiesObjectToUpdateWorking


class BaseUseCasesCookies(ABC):

    @abstractmethod
    def create_new_cookies(self, cookies_object: CookieObject) -> int:
        pass

    @abstractmethod
    def get_cookie_by_id(self, id_cookie: int, provider_sign: str) -> Union[dict, None]:
        pass

    @abstractmethod
    def get_all_cookies(self, provider_sign: str) -> list:
        pass

    @abstractmethod
    def remove_all_non_working_cookies(self, provider_sign: str) -> bool:
        pass

    @abstractmethod
    def remove_all_expired_cookies(self, provider_sign: str) -> bool:
        pass

    @abstractmethod
    def update_cookie_object_by_id(self,
                                   data_to_update: Union[CookiesObjectToUpdateExpire, CookiesObjectToUpdateWorking]
                                   ) -> bool:
        pass

    @abstractmethod
    def count_cookies_by_provider_sign(self, provider_sign: str) -> int:
        pass


class CookiesUseCases(BaseUseCasesCookies):
    __repo_cookies: BaseRepositoryCookies = RepositoryCookies()

    def create_new_cookies(self, cookies_object: CookieObject) -> int:
        new_cookie_id = self.__repo_cookies.create_cookies(new_cookies=cookies_object)
        return new_cookie_id

    def get_cookie_by_id(self, id_cookie: int, provider_sign: str) -> Union[dict, None]:
        cookie: Union[dict, None] = self.__repo_cookies.get_cookie_by_id(provider_sign=provider_sign,
                                                                         id_cookie=id_cookie)
        return cookie

    def get_all_cookies(self, provider_sign: str) -> list:
        cookies = self.__repo_cookies.get_cookies(provider_sign=provider_sign)
        return cookies

    def remove_all_non_working_cookies(self, provider_sign: str) -> bool:

        counter_non_working_cookies: int = 0

        cookies_objects = self.__repo_cookies.get_cookies(provider_sign=provider_sign)
        if not cookies_objects:
            logging.info(f"{provider_sign} No cookies in the file. "
                         f"Impossible to get all cookies to remove all non-working cookies")
            return False

        non_working_cookies: List[dict] = []

        for cookie_obj in cookies_objects:

            is_working: bool = cookie_obj["is_working"]

            if not is_working:
                non_working_cookies.append(cookie_obj)
                counter_non_working_cookies += 1

        if not non_working_cookies:
            logging.debug(f"{provider_sign} All cookies are working")
            return False

        logging.info(f"{provider_sign} Number of expired cookies in the file: {counter_non_working_cookies}")

        is_removed = self.__repo_cookies.remove_cookies(provider_sign=provider_sign,
                                                        cookies=non_working_cookies)
        return is_removed

    def remove_all_expired_cookies(self, provider_sign: str) -> bool:

        counter_expired_cookies: int = 0

        cookies_objects = self.__repo_cookies.get_cookies(provider_sign=provider_sign)
        if not cookies_objects:
            logging.info(f"{provider_sign} No cookies in the file. "
                         f"Impossible to get all cookies to remove all expired cookies")
            return False

        expired_cookies: List[dict] = []

        for cookie_obj in cookies_objects:

            is_expired = cookie_obj["is_expired"]

            if is_expired:
                expired_cookies.append(cookie_obj)
                counter_expired_cookies += 1

            if not expired_cookies:
                logging.debug(f"{provider_sign} No expired cookies")
                return False

        logging.info(f"{provider_sign} Number of expired cookies in the file: {counter_expired_cookies}")

        # Берем все куки, у которых истек срок жизни, которые надо удалить
        is_removed = self.__repo_cookies.remove_cookies(provider_sign=provider_sign, cookies=expired_cookies)
        return is_removed

    def update_cookie_object_by_id(self,
                                   data_to_update: Union[CookiesObjectToUpdateExpire, CookiesObjectToUpdateWorking]
                                   ) -> bool:

        is_updated = self.__repo_cookies.update_cookie_by_id(data_to_update=data_to_update)
        return is_updated

    def count_cookies_by_provider_sign(self, provider_sign: str) -> int:

        cookies_objects = self.__repo_cookies.get_cookies(provider_sign=provider_sign)
        return len(cookies_objects)
