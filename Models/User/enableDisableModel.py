from pydantic import BaseModel

class EnableModel(BaseModel):
    userCode: str
    email:str
    isActive: bool