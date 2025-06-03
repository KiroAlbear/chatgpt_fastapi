from pydantic import BaseModel

class EnableDisableUserModel(BaseModel):
    userCode: str
    email:str
    isActive: bool