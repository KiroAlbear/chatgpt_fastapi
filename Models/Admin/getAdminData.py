from pydantic import BaseModel

class GetAdminDataModel(BaseModel):
    email:str
    password:str
   