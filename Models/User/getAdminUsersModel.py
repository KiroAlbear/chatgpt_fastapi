from pydantic import BaseModel

class GetAdminUsersModel(BaseModel):
    email:str
   