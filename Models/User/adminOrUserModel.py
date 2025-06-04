from pydantic import BaseModel

class AdminOrUserModel(BaseModel):
    email:str
    password:str
