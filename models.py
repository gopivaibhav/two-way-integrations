from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
import json
from json import JSONEncoder
from database import Base


class Customer(Base, JSONEncoder): # Older className is User, users
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    # items = relationship("Item", back_populates="owner")
    def toDict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# class Product(Base):
#     __tablename__ = "products"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)


# class Item(Base):
#     __tablename__ = "items"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)
#     owner_id = Column(Integer, ForeignKey("users.id"))

#     owner = relationship("User", back_populates="items")