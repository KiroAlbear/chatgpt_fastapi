from pydantic import BaseModel


class RegisterAdminUserModel(BaseModel):
    adminUserName:str
    adminPassword:str
    secretKey:str
    maxLoginPerPeriod:int
    resetAFterDays:int


