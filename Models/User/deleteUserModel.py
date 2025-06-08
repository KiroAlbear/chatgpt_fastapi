from pydantic import BaseModel

class DeleteUserModel(BaseModel):
    userCode: str
    email:str
    password:str
