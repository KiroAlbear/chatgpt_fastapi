from pydantic import BaseModel


class EnableDisableAdminModel(BaseModel):
    superAdminPassword:str
    adminUserName:str
    isActive:bool = False  # Default to False, can be set to True if needed



