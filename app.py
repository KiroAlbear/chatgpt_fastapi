from fastapi import  FastAPI
from DataBaseTables.userTable import UserTable
from Models.loginModel import LoginModel
from Models.registerModel import RegisterModel
from Models.walletRechargeOrWithdrawModel import WalletRechargeOrWithdrawModel
import databases




DATABASE_URL = "sqlite:///./users.db"
usersDatabase = databases.Database(DATABASE_URL)

userTableFunctions =  UserTable()

userTableFunctions.createAndReturnUserTable()


fastapi = FastAPI()


@fastapi.on_event("startup")
async def connect():
    await usersDatabase.connect()

@fastapi.on_event("shutdown")
async def shutdown():
    await usersDatabase.disconnect()

## User APIS
######################################################################################

# @app.get("/Users")
# async def getAllUsers():
#     query =  register.select()
#     allUsers = await usersDatabase.fetch_all(query)
#     return allUsers



@fastapi.post('/registerUser')
async def addUser(r:RegisterModel):
    return await userTableFunctions.insertNewUser(r)

@fastapi.post('/loginUser')
async def loginUser(r:LoginModel):
    return await userTableFunctions.loginUser(r)

## Provider APIS
######################################################################################


