from pydantic import BaseModel


class UpdateAdminModel(BaseModel):
    adminUserName:str
    adminPassword:str
    secretKey:str
    sheetUrl:str
    sheetStartingRowNumber:int
    sheetUsersCodesColumnNumber:int
    sheetPhoneColumnNumber:int
    sheetDaysLeftColumnNumber:int
    maxLoginPerPeriod:int
    resetAFterDays:int


