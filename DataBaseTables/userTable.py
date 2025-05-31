from fastapi import HTTPException
import databases
import sqlalchemy
from Models.loginModel import LoginModel
from Models.registerModel import RegisterModel
from datetime import datetime
import authenticator as authenticator



class UserTable():
    __DATABASE_URL = "sqlite:///./users.db"
    __systemDatabase = databases.Database(__DATABASE_URL)
    __metaData = sqlalchemy.MetaData()
    tableName = "users"
    phoneNumber_ColumnName = "phoneNumber"
    daysRemaining_ColumnName = "daysRemaining"
    loginCounter_ColumnName = "loginCounter"
    lastLoginDate_ColumnName = "lastLoginDate"
  
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
        sqlalchemy.Column(self.loginCounter_ColumnName,sqlalchemy.Integer),
        sqlalchemy.Column(self.lastLoginDate_ColumnName, sqlalchemy.String,))
        

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
        lastLoginDate = None
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
        

    
    async def requestCodeForUser(self,user:LoginModel):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            code = str(authenticator.add_new_secrets())
        except Exception as e:
            raise HTTPException(
                status_code = 500,
                detail = "Error generating code: {}".format(str(e))
            )
        
        
        
        query = "UPDATE {} SET {} = {} +1 WHERE {} = {}".format(
            self.tableName,

            self.loginCounter_ColumnName,
            self.loginCounter_ColumnName,

            self.phoneNumber_ColumnName,
            user.phoneNumber
        )

        updateDateQuery = "UPDATE {} SET {} = {} WHERE {} = {}".format(
        self.tableName,

        self.lastLoginDate_ColumnName,
        " '{}'".format(current_datetime),

        self.phoneNumber_ColumnName,
        user.phoneNumber
    )

        try:
            # await self.__systemDatabase.execute(query)
            await self.__systemDatabase.execute(updateDateQuery)
            return {
                "code": code,
            }
        except Exception as e:
            print("Error updating user data: {}".format(str(e)))
            raise HTTPException(
                status_code = 403,
                detail = "User does not exist: {}".format(str(e))
            )
    

    async def getUserData(self, userId):

        query = "SELECT {},{},{},{} FROM {} WHERE {}={}".format(
        self.phoneNumber_ColumnName,
        self.daysRemaining_ColumnName,
        self.loginCounter_ColumnName,
        self.lastLoginDate_ColumnName,

        self.tableName,

        self.phoneNumber_ColumnName,
        
        userId)
        row = await self.__systemDatabase.fetch_one(query)
        return {
            self.phoneNumber_ColumnName:row[0],
            self.daysRemaining_ColumnName:row[1],
            self.loginCounter_ColumnName:row[2],
            self.lastLoginDate_ColumnName:row[3]
        }

