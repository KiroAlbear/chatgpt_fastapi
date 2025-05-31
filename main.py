from fastapi import FastAPI
from DataBaseTables.userTable import UserTable
from Models.loginModel import LoginModel
from Models.registerModel import RegisterModel
from Models.walletRechargeOrWithdrawModel import WalletRechargeOrWithdrawModel
import databases




DATABASE_URL = "sqlite:///./users.db"
usersDatabase = databases.Database(DATABASE_URL)

userTableFunctions =  UserTable()

userTableFunctions.createAndReturnUserTable()


app = FastAPI()


@app.on_event("startup")
async def connect():
    await usersDatabase.connect()

@app.on_event("shutdown")
async def shutdown():
    await usersDatabase.disconnect()

## User APIS
######################################################################################

# @app.get("/Users")
# async def getAllUsers():
#     query =  register.select()
#     allUsers = await usersDatabase.fetch_all(query)
#     return allUsers



@app.post('/registerUser')
async def addUser(r:RegisterModel):
    return await userTableFunctions.insertNewUser(r)

@app.post('/loginUser')
async def loginUser(r:LoginModel):
    return await userTableFunctions.loginUser(r)

## Provider APIS
######################################################################################


