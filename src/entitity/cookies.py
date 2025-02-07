from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class CookieObject:
    provider_sign: str
    cookies: List[dict]
    id: Optional[int] = field(init=False)
    is_expired: bool = field(default=False)
    is_working: bool = field(default=True)

    def __post_init__(self):

        is_cookies_type = self.is_cookies_valid_type()
        if not is_cookies_type:
            raise Exception(f"Object is not a valid type {type(self.cookies)} "
                            f"Cookies: {self.cookies}")

        is_cookies = self.is_cookies()
        if not is_cookies:
            raise Exception(f"Cookies are empty {self.cookies}")

    def is_cookies(self):
        return True if self.cookies else False

    def is_cookies_valid_type(self):
        return True if isinstance(self.cookies, list) else False

    def dict(self):

        new_cookies_object = {
            "id": self.id,
            "is_expired": self.is_expired,
            "is_working": self.is_working,
            "provider_sign": self.provider_sign,
            "cookies": self.cookies,
        }

        if self.id is None:
            new_cookies_object.pop("id")
            return new_cookies_object
        else:
            return new_cookies_object


@dataclass
class CookiesObjectToUpdate:
    id: int
    provider_sign: str

    def __post_init__(self):
        is_id_msg = self.is_id()
        if not is_id_msg:
            raise Exception(is_id_msg)

        is_provider = self.is_provider_sign()
        if not is_provider:
            raise Exception(is_provider)

    def is_id(self):
        return True if isinstance(self.id, int) else False

    def is_provider_sign(self):
        return True if isinstance(self.provider_sign, str) else False


@dataclass
class CookiesObjectToUpdateExpire(CookiesObjectToUpdate):
    is_expired: bool

    def __post_init__(self):
        super().__post_init__()
        is_expired = self.is_expire()
        if not is_expired:
            raise Exception(is_expired)

    def is_expire(self):
        return True if isinstance(self.is_expired, bool) else False

    def dict(self):
        new_cookies_object = {
            "id": self.id,
            "provider_sign": self.provider_sign,
            "is_expired": self.is_expired,
        }

        return new_cookies_object


@dataclass
class CookiesObjectToUpdateWorking(CookiesObjectToUpdate):
    is_working: bool

    def __post_init__(self):
        super().__post_init__()
        is_working = self.is_work()
        if not is_working:
            raise Exception(is_working)

    def is_work(self):
        return True if isinstance(self.is_working, bool) else False

    def dict(self):
        new_cookies_object = {
            "id": self.id,
            "provider_sign": self.provider_sign,
            "is_working": self.is_working,
        }

        return new_cookies_object
