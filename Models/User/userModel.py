
from pydantic import BaseModel


class UserModel():
    userCode:str
    userPhone:str
    expiryDate:str
    daysLeft:int 
    lastLoginDate:str
    loginCount:str 

    def __init__(self, userCode: str, userPhone: str, expiryDate: str, daysLeft: int, lastLoginDate: str, loginCount: str):
        self.userCode = userCode
        self.userPhone = userPhone
        self.expiryDate = expiryDate
        self.daysLeft = daysLeft
        self.lastLoginDate = lastLoginDate
        self.loginCount = loginCount
        