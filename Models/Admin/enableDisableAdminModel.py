from pydantic import BaseModel


class EnableDisableAdminModel(BaseModel):
    creatorPassword:str
    adminUserName:str
    isActive:bool = False  # Default to False, can be set to True if needed



