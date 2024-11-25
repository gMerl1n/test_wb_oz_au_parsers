from dataclasses import dataclass


@dataclass
class Product:

    name: str
    full_price: int
    price_with_discount: int
    url: str
    sign: str
    in_stock: int

    def to_dict(self):
        return self.__dict__

    @classmethod
    def to_model(cls):
        return cls.__class__



