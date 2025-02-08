import os
import json
import logging

from pathlib import Path
from abc import abstractmethod, ABC
from src.entitity.cookies import CookieObject, CookiesObjectToUpdateExpire, CookiesObjectToUpdateWorking

# Remove all handlers associated with the root logger object.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    level=logging.WARNING
)


class BaseRepositoryCookies(ABC):

    @abstractmethod
    def create_cookies(self, new_cookies: CookieObject) -> int:
        pass

    @abstractmethod
    def get_cookie_by_id(self, provider_sign: str, id_cookie: int) -> dict | None:
        pass

    @abstractmethod
    def get_cookies(self, provider_sign: str) -> list:
        pass

    @abstractmethod
    def remove_cookie_by_id(self, provider_sign: str, id_cookie: int) -> bool:
        pass

    @abstractmethod
    def remove_cookies(self, provider_sign: str, cookies: list[dict]) -> bool:
        pass

    @abstractmethod
    def update_cookie_by_id(self,
                            data_to_update: CookiesObjectToUpdateExpire | CookiesObjectToUpdateWorking) -> bool:
        pass

    @abstractmethod
    def update_cookies(self, provider_sign: str, updated_cookies: list[dict]):
        pass


class RepositoryCookies(BaseRepositoryCookies):
    root_dir = Path(__file__).resolve().parent.parent
    temp_dir_path: str = os.path.join(root_dir, "temp")
    cookies_dir_path: str = os.path.join(temp_dir_path, "cookies_storage")

    def create_cookies(self, new_cookies: CookieObject) -> int:

        path: str = os.path.join(self.cookies_dir_path, f"{new_cookies.provider_sign}_cookies.json")

        self.check_or_create_cookies_file(path)

        if self.is_cookies_file_empty(path):
            with open(path, "w", encoding="utf-8") as file:

                new_cookies.id = 1
                empty_list_cookies = [new_cookies.dict()]
                json.dump(empty_list_cookies, file, indent=4, ensure_ascii=False)

                return new_cookies.id

        else:
            with open(path, "r+") as file:

                cookies_objects: list[dict] = json.load(file)
                if cookies_objects:
                    last_object_id: int = cookies_objects[-1]["id"]
                    new_cookies_id: int = last_object_id + 1
                else:
                    new_cookies_id: int = 0

                new_cookies.id = new_cookies_id

                cookies_objects.append(new_cookies.dict())
                file.truncate(0)
                file.seek(0)

                json.dump(cookies_objects, file, indent=4, ensure_ascii=False)

                return new_cookies.id

    def get_cookie_by_id(self, provider_sign: str, id_cookie: int) -> dict | None:

        path: str = os.path.join(self.cookies_dir_path, f"{provider_sign}_cookies.json")

        self.check_or_create_cookies_file(path)

        if self.is_cookies_file_empty(path):
            return

        with open(path, "r") as file:

            cookies_objects = json.load(file)

            for cookie_obj in cookies_objects:
                if cookie_obj["id"] == id_cookie:
                    return cookie_obj

    def get_cookies(self, provider_sign: str) -> list:

        path: str = os.path.join(self.cookies_dir_path, f"{provider_sign}_cookies.json")

        self.check_or_create_cookies_file(path)

        if self.is_cookies_file_empty(path):
            return []

        cookies_by_provider_sign: list[dict] = []

        with open(path, "r") as file:
            cookies_objects = json.load(file)

            for cookie_obj in cookies_objects:
                if cookie_obj["provider_sign"] == provider_sign:
                    cookies_by_provider_sign.append(cookie_obj)

            return cookies_by_provider_sign

    def remove_cookie_by_id(self, provider_sign: str, id_cookie: int) -> bool:

        is_deleted: bool = False

        path: str = os.path.join(self.cookies_dir_path, f"{provider_sign}_cookies.json")

        if self.is_cookies_file_empty(path):
            logging.warning(f"{provider_sign} No cookies in the file. "
                            f"Impossible to remove cookie with id {id_cookie}")
            return False

        self.check_or_create_cookies_file(path)

        with open(path, "r+") as file:

            cookies_objects = json.load(file)

            for cookie_obj in cookies_objects:

                if cookie_obj["id"] == id_cookie:
                    cookies_objects.remove(cookie_obj)
                    is_deleted = True
                    break

            file.truncate(0)
            file.seek(0)

            if cookies_objects:
                json.dump(cookies_objects, file, indent=4, ensure_ascii=False)

            if is_deleted:
                logging.info(f"{provider_sign} Cookies with id {id_cookie} removed successfully")
                return is_deleted
            else:
                logging.warning(f"{provider_sign} Cookies with id {id_cookie} does not exist. Impossible to remove")
            return is_deleted

    def remove_cookies(self, provider_sign: str, cookies: list[dict]) -> bool:

        counter_removed_cookies: int = 0

        updated_cookies: list[dict] = []

        path: str = os.path.join(self.cookies_dir_path, f"{provider_sign}_cookies.json")

        self.check_or_create_cookies_file(path)

        if self.is_cookies_file_empty(path):
            logging.info(f"{provider_sign} No cookies in the file to remove")
            return False

        ids_cookies_to_delete = {c["id"] for c in cookies}

        with open(path, "r+") as file:

            cookies_objects = json.load(file)

            for cookie_obj in cookies_objects:

                if cookie_obj["id"] not in ids_cookies_to_delete:
                    updated_cookies.append(cookie_obj)
                else:
                    counter_removed_cookies += 1

            file.truncate(0)
            file.seek(0)
            if updated_cookies:
                json.dump(updated_cookies, file, indent=4, ensure_ascii=False)

            logging.info(f"{provider_sign} Number of removed cookies: {counter_removed_cookies}")

            return True if counter_removed_cookies > 0 else False

    @staticmethod
    def update_cookies_data(cookies_from_db: dict, data_to_update: dict) -> dict:

        for key in cookies_from_db:
            if data_to_update.get(key):
                if cookies_from_db[key] != data_to_update[key]:
                    cookies_from_db[key] = data_to_update[key]

        return cookies_from_db

    def update_cookie_by_id(self,
                            data_to_update: CookiesObjectToUpdateExpire | CookiesObjectToUpdateWorking) -> bool:

        is_updated: bool = False

        path: str = os.path.join(self.cookies_dir_path, f"{data_to_update.provider_sign}_cookies.json")

        self.check_or_create_cookies_file(path)

        if self.is_cookies_file_empty(path):
            return False

        data = data_to_update.dict()

        with open(path, "r+") as file:

            cookies_objects: list[dict] = json.load(file)

            for cookie_obj in cookies_objects:

                if cookie_obj["id"] == data["id"]:
                    if data.get("is_expired") is not None:
                        cookie_obj["is_expired"] = data.get("is_expired")
                        is_updated = True

                    if data.get("is_working") is not None:
                        cookie_obj["is_working"] = data.get("is_working")
                        is_updated = True

            file.truncate(0)
            file.seek(0)

            json.dump(cookies_objects, file, indent=4, ensure_ascii=False)

            return is_updated

    def update_cookies(self, provider_sign: str, updated_cookies: list[dict]):
        pass

    @staticmethod
    def check_or_create_cookies_file(path: str) -> None:
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8"):
                pass

    @staticmethod
    def is_cookies_file_empty(path: str) -> bool | None:
        if os.stat(path).st_size == 0:
            return True


root_dir = Path(__file__).resolve().parent.parent
cookies_dir_path: str = os.path.join(root_dir, "temp", "cookies_storage")


def check_or_create_dir(path: str) -> bool | None:
    if os.path.exists(path):
        return True

    logging.info(f"Dir was created: {os.path.exists(path)}")
    os.makedirs(path)


check_or_create_dir(cookies_dir_path)
