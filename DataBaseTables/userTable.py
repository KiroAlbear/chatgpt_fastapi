from fastapi import HTTPException
import databases
import sqlalchemy
from Models.loginModel import LoginModel
from Models.registerModel import RegisterModel
from Models.walletRechargeOrWithdrawModel import WalletRechargeOrWithdrawModel




class UserTable():
    __DATABASE_URL = "sqlite:///./users.db"
    __systemDatabase = databases.Database(__DATABASE_URL)
    __metaData = sqlalchemy.MetaData()
    tableName = "users"
    phoneNumber_ColumnName = "phoneNumber"
    daysRemaining_ColumnName = "daysRemaining"
    loginCounter_ColumnName = "loginCounter"
  
    __usersTable = 0

    def createAndReturnUserTable(self):
        
        self.__usersTable = self.__getUsersTable()
    
        engine = sqlalchemy.create_engine(
        self.__DATABASE_URL,connect_args={"check_same_thread": False}
        )
        self.__metaData.create_all(engine)
        return self.__usersTable

    def __getUsersTable(self):
        usersTable = sqlalchemy.Table(
        self.tableName,
        self.__metaData,
        sqlalchemy.Column(self.phoneNumber_ColumnName,sqlalchemy.String,primary_key = True),
        sqlalchemy.Column(self.daysRemaining_ColumnName,sqlalchemy.Integer),
        sqlalchemy.Column(self.loginCounter_ColumnName,sqlalchemy.Integer),)

        return usersTable

    # async def loginUser(self,userloginModel:LoginModel):
        
    #     verification_query = "SELECT * FROM {} WHERE {}='{}' and {} = '{}'".format(

    #         self.tableName,

    #         self.email_ColumnName,
    #         userloginModel.email,

    #         self.password_ColumnName,
    #         userloginModel.password
    #     )

    #     record = await self.__systemDatabase.fetch_one(verification_query)
    #     if(record != None):
    #         return record
    #     else:
    #         raise HTTPException(
    #          status_code = 400,
    #          detail = "Wrong email or password"
    #         )

    async def insertNewUser(self,userModel:RegisterModel):
        query = self.__usersTable.insert().values(
        phoneNumber = userModel.phoneNumber,
        loginCounter = 0,
        daysRemaining = 0,
    )
        ###################################################################################################

        phone_verification_query = "SELECT * FROM {} WHERE {}= '{}'".format(
           self.tableName,

           self.phoneNumber_ColumnName,
           userModel.phoneNumber,
        )
        phone_verification_record = await self.__systemDatabase.fetch_all(phone_verification_query)

        ###################################################################################################

        
     
        if(len(phone_verification_record) > 0):
            raise HTTPException(
             status_code = 400,
             detail = "This Phone Number already exists"
            )

        
        else:
           await self.__systemDatabase.execute(query)
           return await self.getUserData(userModel.phoneNumber)
    


    async def getUserData(self, userId):

        query = "SELECT {},{},{} FROM {} WHERE {}={}".format(
        self.phoneNumber_ColumnName,
        self.daysRemaining_ColumnName,
        self.loginCounter_ColumnName,

        self.tableName,

        self.phoneNumber_ColumnName,
        
        userId)
        row = await self.__systemDatabase.fetch_one(query)
        return {
            self.phoneNumber_ColumnName:row[0],
            self.daysRemaining_ColumnName:row[1],
            self.loginCounter_ColumnName:row[2],
        }

