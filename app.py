from fastapi import  FastAPI
from DataBaseTables.userTable import UserTable
from Models.loginModel import LoginModel
from Models.registerModel import RegisterModel
from Models.walletRechargeOrWithdrawModel import WalletRechargeOrWithdrawModel
import databases
from starlette.middleware.cors import CORSMiddleware


DATABASE_URL = "sqlite:///./users.db"
usersDatabase = databases.Database(DATABASE_URL)

userTableFunctions =  UserTable()

userTableFunctions.createAndReturnUserTable()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post('/registerUser')
async def addUser(r:RegisterModel):
    return await userTableFunctions.insertNewUser(r)

@app.post('/loginUser')
async def loginUser(r:LoginModel):
    return await userTableFunctions.loginUser(r)

## Provider APIS
######################################################################################


