
from pydantic import BaseModel


class RegisterModel(BaseModel):
    userCode:str
    email:str

