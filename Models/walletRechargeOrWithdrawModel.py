from pydantic import BaseModel


from pydantic import BaseModel

class WalletRechargeOrWithdrawModel(BaseModel):
    id:int 
    value:int