from sqlalchemy import Column, String, Integer, DateTime
from config.base import Base
from datetime import datetime


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, nullable=False)
    full_price = Column(Integer)
    price_with_discount = Column(Integer)
    url = Column(String)
    sign = Column(String)
    in_stock = Column(Integer, nullable=True)
    update_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
