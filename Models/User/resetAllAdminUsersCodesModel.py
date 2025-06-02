
from pydantic import BaseModel


class ResetAllAdminUsersCodesModel(BaseModel):
    email:str