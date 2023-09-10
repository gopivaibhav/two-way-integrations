from pydantic import BaseModel


# class CustomerBase(BaseModel):
#     email: str


class Customer(BaseModel):
    id: int
    email: str
    name: str
    class Config:
        orm_mode = True
