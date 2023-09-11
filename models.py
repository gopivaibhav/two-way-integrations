from sqlalchemy import Column, Integer, String
from json import JSONEncoder
from database import Base


class Customer(Base, JSONEncoder):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    def toDict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}