from pydantic import BaseModel


class RegisterAdminModel(BaseModel):
    adminUserName:str
    adminPassword:str
    secretKey:str