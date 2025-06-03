from fastapi import  FastAPI
from DataBaseTables.userTable import UserTable
from DataBaseTables.adminTable import AdminTable
from Models.User.loginModel import LoginModel
from Models.User.registerModel import RegisterModel
from Models.User.enableDisableModel import EnableDisableUserModel
from Models.User.getAdminUsersModel import GetAdminUsersModel
from Models.User.resetAllAdminUsersCodesModel import ResetAllAdminUsersCodesModel

from Models.Admin.registerAdminModel import RegisterAdminModel
from Models.Admin.updateAdminModel import UpdateAdminModel
from Models.Admin.enableDisableAdminModel import EnableDisableAdminModel
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

@app.post('/updateAdmin')
async def UpdateAdmin(r:UpdateAdminModel):
    return await adminTableFunctions.updateAdmin(r)

@app.post('/enableDisableAdmin')
async def enableDisableAdmin(r:EnableDisableAdminModel):
    return await adminTableFunctions.enableDisableAdmin(r)

@app.get('/generateCode')
async def generateCode():
    return  adminTableFunctions.generateCode()

@app.post('/getAllAdminUsers')
async def getAllAdminUsers(r:GetAdminUsersModel):
    return await adminTableFunctions.getAllAdminUsers(r)

# @app.post('/registerUser')
# async def addUser(r:RegisterModel):
#     return await userTableFunctions.insertNewUser(r)

@app.post('/requestUserCode')
async def requestUserCode(r:LoginModel):
    return await userTableFunctions.requestCodeForUser(r)

@app.post('/enableDisableUser')
async def enableDisableUser(r:EnableDisableUserModel):
    return await userTableFunctions.enableDisableUser(r)

@app.post('/enableAllAdminUsers')
async def enableAllAdminUsers(r:ResetAllAdminUsersCodesModel):
    return await userTableFunctions.enableAllAdminUsers(r)

# @app.post('/getSpreadSheetData')
# async def getSpreadSheetData():
#     return await spreadsheet.scrapeDataFromSpreadSheet()

## Provider APIS
######################################################################################


