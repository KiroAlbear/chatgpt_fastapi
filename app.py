from fastapi import  FastAPI
from DataBaseTables.userTable import UserTable
from DataBaseTables.adminTable import AdminTable
from Models.loginModel import LoginModel
from Models.registerModel import RegisterModel
from Models.registerAdminModel import RegisterAdminModel
import databases
import utils.spreadsheet_utils as spreadsheet



USERS_DATABASE_URL = "sqlite:///./users.db"
usersDatabase = databases.Database(USERS_DATABASE_URL)

userTableFunctions =  UserTable()
userTableFunctions.createAndReturnUserTable()

adminTableFunctions = AdminTable()
adminTableFunctions.createAndReturnAdminTable()


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

@app.post('/registerAdmin')
async def addAdmin(r:RegisterAdminModel):
    return await adminTableFunctions.insertNewAdmin(r)

@app.get('/generateCode')
async def generateCode():
    return  adminTableFunctions.generateCode()

@app.post('/registerUser')
async def addUser(r:RegisterModel):
    return await userTableFunctions.insertNewUser(r)

@app.post('/getUserCode')
async def getUserCode(r:LoginModel):
    return await userTableFunctions.requestCodeForUser(r)

@app.post('/getSpreadSheetData')
async def getSpreadSheetData():
    return await spreadsheet.scrapeDataFromSpreadSheet()

## Provider APIS
######################################################################################


