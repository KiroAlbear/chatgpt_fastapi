
from pydantic import BaseModel


class UserModel():
    userCode:str
    userPhone:str
    expiryDate:str
    daysLeft:int 
    lastLoginDate:str
    firstLoginDate:str
    loginCount:str 
    isActive: bool 

    def __init__(self, userCode: str, userPhone: str, expiryDate: str, daysLeft: int, lastLoginDate: str, loginCount: str, isActive: bool, firstLoginDate: str ):
        self.userCode = userCode
        self.userPhone = userPhone
        self.expiryDate = expiryDate
        self.daysLeft = daysLeft
        self.lastLoginDate = lastLoginDate
        self.firstLoginDate = firstLoginDate
        self.loginCount = loginCount
        self.isActive = isActive
        