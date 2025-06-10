from pydantic import BaseModel


class RegisterAdminModelSuperAdmin(BaseModel):
    superAdminPassword:str
    adminUserName:str
    adminPassword:str
    secretKey:str
    startDate:str
    endDate:str
   
    maxLoginPerPeriod:int
    resetAFterDays:int


