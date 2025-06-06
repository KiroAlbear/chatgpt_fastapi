
from pydantic import BaseModel


class UserModel():
    userCode:str
    email:str
    userPhone:str
    startDate:str
    endDate:str
    expiryDate:str
    daysLeft:int 
    lastLoginDate:str
    firstLoginDate:str
    loginCount:str 
    isActive: bool
    isMaximumCodesReached: bool 

    def __init__(self, userCode: str,
                  userPhone: str,
                  email:str,
                  expiryDate: str,
                  startDate: str ,
                  endDate: str,
                  daysLeft: int,
                  lastLoginDate: str,
                  loginCount: str,
                  isActive: bool,
                  firstLoginDate: str,
                  isMaximumCodesReached: bool = False,
                ):

        self.userCode = userCode
        self.email = email
        self.userPhone = userPhone
        self.expiryDate = expiryDate
        self.daysLeft = daysLeft
        self.lastLoginDate = lastLoginDate
        self.firstLoginDate = firstLoginDate
        self.loginCount = loginCount
        self.isActive = isActive
        self.isMaximumCodesReached = isMaximumCodesReached
        self.startDate = startDate
        self.endDate = endDate
        