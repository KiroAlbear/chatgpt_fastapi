from pydantic import BaseModel


class UpdateAdminModelSuperAdmin(BaseModel):
    superAdminPassword:str
    adminUserName:str
    secretKey:str
    startDate:str
    endDate:str
    maxLoginPerPeriod:int
    resetAFterDays:int
    isActive:bool
    isFreeTrial:bool


