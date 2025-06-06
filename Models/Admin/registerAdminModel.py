from pydantic import BaseModel


class RegisterAdminModel(BaseModel):
    creatorPassword:str
    adminUserName:str
    adminPassword:str
    secretKey:str
    startDate:str
    endDate:str
   
    maxLoginPerPeriod:int
    resetAFterDays:int


