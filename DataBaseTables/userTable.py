from fastapi import HTTPException
import databases
import sqlalchemy
from Models.loginModel import LoginModel
from Models.registerModel import RegisterModel
from datetime import datetime, timedelta
import authenticator as authenticator
import utils.spreadsheet_utils as spreadsheet



class UserTable():
    __DATABASE_URL = "sqlite:///./users.db"
    __systemDatabase = databases.Database(__DATABASE_URL)
    __metaData = sqlalchemy.MetaData()
    tableName = "users"
    phoneNumber_ColumnName = "phoneNumber"
    
    loginCounter_ColumnName = "loginCounter"
    lastLoginDate_ColumnName = "lastLoginDate"
    firstLoginDate_ColumnName = "firstLoginDate"
    expiryDate_ColumnName = "expiryDate"
  
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
        sqlalchemy.Column(self.loginCounter_ColumnName,sqlalchemy.Integer, nullable=False, default=0),
        sqlalchemy.Column(self.lastLoginDate_ColumnName, sqlalchemy.String, nullable=True),
        sqlalchemy.Column(self.firstLoginDate_ColumnName, sqlalchemy.String,nullable=True),
        sqlalchemy.Column(self.expiryDate_ColumnName, sqlalchemy.String,nullable=True )  # Optional expiry date
        )
        

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
        lastLoginDate = None,
        firstLoginDate = None,
        expiryDate = None
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
    
        datetime_format = "%Y-%m-%d"
        currentDate = datetime.now()
        currentDateString = currentDate.strftime(datetime_format)

        maxUserLoginCounterPerPeriod = 2 ########### Change this value to set the maximum number of login attempts per period of time
        resetAFterDays = 1 ########### Change this value to set the number of days after which the login counter resets

        resetAfterDateString = (currentDate + timedelta(days=resetAFterDays)).strftime(datetime_format)
        
        code = None
        try:
            code = str(authenticator.add_new_secrets())
           
        except Exception as e:
            raise HTTPException(
                status_code = 400,
                detail = "Error generating code: {}".format(str(e))
            )
        
        
        
        incrementUserLoginQuery = "UPDATE {} SET {} = {} +1, {} = {} WHERE {} = '{}'".format(
            self.tableName,

            self.loginCounter_ColumnName,
            self.loginCounter_ColumnName,

             self.lastLoginDate_ColumnName,
            "'{}'".format(currentDateString),

            self.phoneNumber_ColumnName,
            user.phoneNumber
        )

        
        resetUserFirstAndExpiryDateQuery = "UPDATE {} SET {} = 1, {} = {}, {} = {}, {} = {} WHERE {} = '{}'".format(
            self.tableName,

            self.loginCounter_ColumnName,
        
            
             self.lastLoginDate_ColumnName,
            "'{}'".format(currentDateString),

            self.expiryDate_ColumnName,
            "'{}'".format(resetAfterDateString),

            self.firstLoginDate_ColumnName,
            "'{}'".format(currentDateString),

            self.phoneNumber_ColumnName,
            user.phoneNumber
        )


        userData = await self._handleUserNotExist( user.phoneNumber)
            
        
        
        # If the user has never logged in, set the first login date and expiry date
        if (userData[self.lastLoginDate_ColumnName] == None or userData[self.firstLoginDate_ColumnName] == None or userData[self.expiryDate_ColumnName] == None):
            try:
                print("User has never logged in, setting first login date and expiry date")
                await self.__systemDatabase.execute(resetUserFirstAndExpiryDateQuery)
                return {
                    "code": code
                }
            except Exception as e:
                raise HTTPException(
                    status_code = 400,
                    detail = "Error resetting user dates: {}".format(str(e))
                )

        # firstLoginDateString = userData[self.lastLoginDate_ColumnName]
        expiryDateString = userData[self.expiryDate_ColumnName]

        # firstLoginDate = datetime.strptime(firstLoginDateString, datetime_format)
        expiryDate = datetime.strptime(expiryDateString, datetime_format)


        
            
        
        # if user has exceeded the maximum login per time period, raise an error
        if userData[self.loginCounter_ColumnName] >= maxUserLoginCounterPerPeriod and currentDate < expiryDate:
            raise HTTPException(
                status_code = 400,
                detail = "You have exceeded the maximum login attempts"
            )
        
        # If the user passed expiration period, reset the login counter and set the first login date and expiry date
        if currentDate >= expiryDate:
            try:
                print("User passed expiration period, resetting login counter and setting first login date and expiry date")
                await self.__systemDatabase.execute(resetUserFirstAndExpiryDateQuery)
                return {
                    "code": code
                }
            except Exception as e:
                raise HTTPException(
                    status_code = 400,
                    detail = "Error resetting user dates: {}".format(str(e))
                )
    

        try:
            await self.__systemDatabase.execute(incrementUserLoginQuery)
            # check if the user has exceeded the login counter limit
           
            return {
                "code": code
            }
        except Exception as e:
           
            raise HTTPException(
                status_code = 400,
                detail = "User does not exist: {}".format(str(e))
            )
    
    async def _handleUserNotExist(self, phoneNumber):
       

        userData = None

        try:
            userData = await self.getUserData(phoneNumber)
        except Exception as e:
            userSheetData = await spreadsheet.scrapeDataFromSpreadSheet()
            userSheetItem = [item for item in userSheetData["data"]["availableUser"] if item[0] == phoneNumber]
            print("sheet user:", userSheetItem)

            if userSheetItem == []:
                raise HTTPException(
                    status_code = 400,
                    detail = "This Phone Number is not found in the sheet"
                )
            elif userData == None:
                try:
                    print("User does not exist, inserting new user")
                    userData = await self.insertNewUser(RegisterModel(phoneNumber = phoneNumber))
                except Exception as e:
                    raise HTTPException(
                        status_code = 400,
                        detail = "Error inserting new user: {}".format(str(e))
                    )
        return userData
        
                
    async def getUserData(self, userId):

        query = "SELECT * FROM {} WHERE {} = '{}'".format(
        self.tableName,

        self.phoneNumber_ColumnName,
        
        userId)
        row = await self.__systemDatabase.fetch_one(query)
        return {
            self.phoneNumber_ColumnName:row[0],
            self.loginCounter_ColumnName:row[1],
            self.lastLoginDate_ColumnName:row[2],
            self.firstLoginDate_ColumnName:row[3],
            self.expiryDate_ColumnName:row[4]
        }

