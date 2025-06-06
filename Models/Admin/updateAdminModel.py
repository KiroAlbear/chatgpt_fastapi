from pydantic import BaseModel


class UpdateAdminModel(BaseModel):
    adminUserName:str
    adminPassword:str
    secretKey:str
   
    maxLoginPerPeriod:int
    resetAFterDays:int


