from fastapi import  FastAPI
from DataBaseTables.userTable import UserTable
from Models.loginModel import LoginModel
from Models.registerModel import RegisterModel
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

@app.post('/getUserCode')
async def getUserCode(r:LoginModel):
    return await userTableFunctions.requestCodeForUser(r)

## Provider APIS
######################################################################################


