
from pydantic import BaseModel


class RegisterModel(BaseModel):
    name:str
    startDate:str
    endDate:str
    email:str
    phone:str

