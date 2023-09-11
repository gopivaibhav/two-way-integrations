from pydantic import BaseModel
import json

# class CustomerBase(BaseModel):
#     email: str


class Customer(BaseModel):
    email: str
    name: str
    class Config:
        orm_mode = True
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
