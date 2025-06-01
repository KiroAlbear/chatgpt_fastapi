from pydantic import BaseModel


class RegisterAdminModel(BaseModel):
    creatorPassword:str
    adminUserName:str
    adminPassword:str
    secretKey:str
    sheetUrl:str
    sheetStartingRowNumber:int
    sheetUsersCodesColumnNumber:int
    sheetDaysLeftColumnNumber:int
    maxLoginPerPeriod:int
    resetAFterDays:int


