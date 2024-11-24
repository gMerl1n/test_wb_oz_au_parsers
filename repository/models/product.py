import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey
from app.settings.base import Base
from datetime import datetime


class Product(Base):

    __tablename__ = "products"

    product_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True, default=None)
    name = Column(String, nullable=False)
    full_price = Column(Integer)
    price_with_discount = Column(Integer)
    url = Column(String)
    in_stock = Column(String)
    provider = Column(String)
    update_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.timestamp)


class Category(Base):

    __tablename__ = "categories"

    category_id =Column(Integer, primary_key=True, index=True, unique=True)
    category_name = Column(String, nullable=False)
    update_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.timestamp)