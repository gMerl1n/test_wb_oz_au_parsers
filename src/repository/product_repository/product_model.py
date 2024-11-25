import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Integer, TIMESTAMP
from settings.base import Base
from datetime import datetime


class Product(Base):

    __tablename__ = "products"

    product_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    full_price = Column(Integer)
    price_with_discount = Column(Integer)
    url = Column(String)
    in_stock = Column(Integer)
    provider = Column(String)
    update_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)

