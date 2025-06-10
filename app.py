from fastapi import  FastAPI
from DataBaseTables.userTable import UserTable
from DataBaseTables.adminTable import AdminTable
from Models.User.loginModel import LoginModel
from Models.User.registerModel import RegisterModel
from Models.User.enableDisableModel import EnableDisableUserModel
from Models.User.getAdminUsersModel import GetAdminUsersModel
from Models.User.resetAllAdminUsersCodesModel import ResetAllAdminUsersCodesModel
from Models.User.adminOrUserModel import AdminOrUserModel
from Models.User.deleteUserModel import DeleteUserModel



from Models.Admin.updateAdminModelSuperAdmin import UpdateAdminModelSuperAdmin
from Models.Admin.updateAdminModel import UpdateAdminModel
from Models.Admin.enableDisableAdminModel import EnableDisableAdminModel
from Models.Admin.getAdminData import GetAdminDataModel
from Models.Admin.registerAdminModel import RegisterAdminModel
from Models.Admin.registerAdminModelSuperAdmin import RegisterAdminModelSuperAdmin
import databases


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

@app.post('/addNewAdminSuperAdmin')
async def addNewAdminSuperAdmin(r:RegisterAdminModelSuperAdmin):
    return await adminTableFunctions.addNewAdminSuperAdmin(r)

@app.post('/addNewAdmin')
async def addNewAdmin(r:RegisterAdminModel):
    return await adminTableFunctions.addNewAdmin(r)


@app.get('/deleteAdminSuperAdmin')
async def deleteAdmin(email: str, superAdminPassword: str):
    return await adminTableFunctions.deleteAdminSuperAdmin(email, superAdminPassword)

@app.post('/updateAdminSuperAdmin')
async def UpdateAdmin(r:UpdateAdminModelSuperAdmin):
    return await adminTableFunctions.updateAdminSuperAdmin(r)


@app.post('/updateAdmin')
async def UpdateAdmin(r:UpdateAdminModel):
    return await adminTableFunctions.updateAdmin(r)

@app.post('/enableDisableAdmin')
async def enableDisableAdmin(r:EnableDisableAdminModel):
    return await adminTableFunctions.enableDisableAdmin(r)

@app.post('/registerUser')
async def registerUser(r:RegisterModel):
    return await userTableFunctions.insertNewUser(r)

@app.post('/deleteUser')
async def deleteUser(r:DeleteUserModel):
    return await userTableFunctions.deleteUser(r)

@app.post('/getAllAdminUsers')
async def getAllAdminUsers(r:GetAdminUsersModel):
    return await adminTableFunctions.getAllAdminUsers(r)

@app.post('/getAdminProfileData')
async def getAdminProfileData(r:GetAdminDataModel):
    return await adminTableFunctions.getAdminData(r.email, r.password,withGenericResponse= True)

# @app.post('/registerUser')
# async def addUser(r:RegisterModel):
#     return await userTableFunctions.insertNewUser(r)

@app.get('/getCode')
async def getCode():
    return await userTableFunctions.generateCode(withGenericResponse=True)

@app.post('/getUserOrAdminData')
async def getUserOrAdminData(r:AdminOrUserModel):
    return await userTableFunctions.getUserOrAdminData(r)

@app.post('/requestUserCode')
async def requestUserCode(r:LoginModel):
    return await userTableFunctions.requestCodeForUser(r)

@app.post('/enableDisableUser')
async def enableDisableUser(r:EnableDisableUserModel):
    return await userTableFunctions.enableDisableUser(r)

@app.post('/resetUser')
async def resetUser(r:LoginModel):
    return await userTableFunctions.resetUser(r)

@app.post('/enableDisableAllAdminUsers')
async def enableDisableAllAdminUsers(r:ResetAllAdminUsersCodesModel):
    return await userTableFunctions.enableDisableAllAdminUsers(r)

# @app.post('/getSpreadSheetData')
# async def getSpreadSheetData():
#     return await spreadsheet.scrapeDataFromSpreadSheet()


## Provider APIS
######################################################################################


