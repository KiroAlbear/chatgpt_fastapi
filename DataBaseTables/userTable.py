from fastapi import HTTPException
import databases
import sqlalchemy
from Models.User.loginModel import LoginModel
from Models.User.registerModel import RegisterModel
from Models.User.enableDisableModel import EnableDisableUserModel
from Models.User.resetAllAdminUsersCodesModel import ResetAllAdminUsersCodesModel
from Models.User.getAdminUsersModel import GetAdminUsersModel
from Models.User.adminOrUserModel import AdminOrUserModel

from Models.generic_response import GenericResponse
from DataBaseTables.adminTable import AdminTable
from datetime import datetime, timedelta
import authenticator as authenticator
import utils.spreadsheet_utils as spreadsheet



class UserTable():
    __DATABASE_URL = "sqlite:///./users.db"
    __systemDatabase = databases.Database(__DATABASE_URL)
    __metaData = sqlalchemy.MetaData()
    tableName = "users"
    email_ColumnName = "email"
    phone_ColumnName = "phone"
    userCode_ColumnName = "userCode"
    loginCounter_ColumnName = "loginCounter"
    lastLoginCode_ColumnName = "lastLoginCode"
    
    lastLoginDate_ColumnName = "lastLoginDate"
    firstLoginDate_ColumnName = "firstLoginDate"
    expiryDate_ColumnName = "expiryDate"
    isActive_ColumnName = "isActive"
  
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
        sqlalchemy.Column(self.userCode_ColumnName,sqlalchemy.String,primary_key=True),
        sqlalchemy.Column(self.email_ColumnName,sqlalchemy.String,nullable=True),
        sqlalchemy.Column(self.phone_ColumnName,sqlalchemy.String,nullable=True),
        sqlalchemy.Column(self.loginCounter_ColumnName,sqlalchemy.Integer, nullable=False, default=0),

        sqlalchemy.Column(self.lastLoginDate_ColumnName, sqlalchemy.String, nullable=True),
        sqlalchemy.Column(self.lastLoginCode_ColumnName, sqlalchemy.String, nullable=True),
        sqlalchemy.Column(self.firstLoginDate_ColumnName, sqlalchemy.String,nullable=True),
        sqlalchemy.Column(self.expiryDate_ColumnName, sqlalchemy.String,nullable=True ),
        sqlalchemy.Column(self.isActive_ColumnName, sqlalchemy.Boolean,nullable=False, default=True)

        )
        

        return usersTable
    

    async def insertNewUser(self,userModel:RegisterModel):
        query = self.__usersTable.insert().values(
        email = userModel.email,
        userCode = userModel.userCode,
        phone = userModel.phone,
        loginCounter = 0,
        lastLoginDate = None,
        firstLoginDate = None,
        expiryDate = None,
        isActive = True,
    )
        ###################################################################################################

        user_verification_query = "SELECT * FROM {} WHERE {} = '{}' and {} = '{}'".format(
           self.tableName,

           self.userCode_ColumnName,
           userModel.userCode,

           self.email_ColumnName,
           userModel.email
        )
        user_verification_record = await self.__systemDatabase.fetch_all(user_verification_query)

        ###################################################################################################

        
     
        if(len(user_verification_record) > 0):
            raise HTTPException(
             status_code = 400,
             detail = "This User already exists"
            )

        
        else:
           await self.__systemDatabase.execute(query)
           return await self.getUserData(userCode=userModel.userCode,email=userModel.email)
        

    async def enableDisableAllAdminUsers(self,model:ResetAllAdminUsersCodesModel):
        await AdminTable().getAdminData(userName=model.email,password=model.password)

        query = "UPDATE {} SET {} = {}, {} = {}, {} = {}, {} = {} WHERE {} = '{}'".format(
                    self.tableName,

                    self.loginCounter_ColumnName,
                    0,

                    self.lastLoginDate_ColumnName,
                    'NULL',

                    self.expiryDate_ColumnName,
                    'NULL',

                    self.isActive_ColumnName,
                    model.isActive,


                    self.email_ColumnName,
                    model.email
                )
        await self.__systemDatabase.execute(query)
        return await AdminTable().getAllAdminUsers(model=GetAdminUsersModel(email=model.email,password=model.password))

    async def enableDisableUser(self,model:EnableDisableUserModel):
    
        query = "UPDATE {} SET {} = {}, {} = {}, {} = {} WHERE {} = '{}' and {} = '{}'".format(
            self.tableName,

            self.loginCounter_ColumnName,
            0,

            self.expiryDate_ColumnName,
            'NULL',

            self.isActive_ColumnName,
            model.isActive,

            self.userCode_ColumnName,
            model.userCode,

            self.email_ColumnName,
            model.email
        )
      
    
        await self.__systemDatabase.execute(query)
        return await self.getUserData(userCode=model.userCode,email=model.email, WithGenericResponse=True)
        

    async def getUserOrAdminData(self, model:AdminOrUserModel):

        try:
            admin_record = await AdminTable().getAdminData(userName=model.email,password=model.password)
            if admin_record:
                return GenericResponse({
                    "isAdmin": True,
                }).to_dict()
        except Exception:
            print("Admin not found, checking for user")
            # If admin not found, check for user


        
        try:
            user_record = await self.getUserData(userCode=model.password, email=model.email)
            return GenericResponse({
                "isAdmin": False,
            }).to_dict()
        except Exception:
            print("User not found")
            raise HTTPException(
                status_code = 400,
                detail = "Invalid credentials, please try again"
            )
          
        



    async def checkAndReturnAdmin(self,email):
        admin_record = None
        try:
            admin_record = await AdminTable().getAdminData(userName=email,password=None)
        except Exception:
             raise HTTPException(
                status_code = 400,
                detail = "Admin not found"
            )

        if not admin_record:
            raise HTTPException(
                status_code = 400,
                detail = "Admin not found"
            )
        
        return admin_record
        



        

    async def requestCodeForUser(self,user:LoginModel):
        admin_record = await self.checkAndReturnAdmin(user.email)


        sheetStartingRowNumber = admin_record[AdminTable.sheetStartingRowNumber_ColumnName]
        sheetUsersCodesColumnNumber = admin_record[AdminTable.sheetUsersCodesColumnNumber_ColumnName] 
        sheetDaysLeft = admin_record[AdminTable.sheetDaysLeftColumnNumber_ColumnName] 
        maxLoginPerPeriodParam = admin_record[AdminTable.maxLoginPerPeriod_ColumnName] 
        resetAFterDaysParam = admin_record[AdminTable.resetAFterDays_ColumnName] 
        phoneColumnNumber = admin_record[AdminTable.sheetPhoneColumnNumber_ColumnName]
        

        sheetUrl = admin_record[AdminTable.sheetUrl_ColumnName]
        secretKey = admin_record[AdminTable.secretKey_ColumnName]



        datetime_format = "%Y-%m-%d"
        currentDate = datetime.now()
        currentDateString = currentDate.strftime(datetime_format)

        maxUserLoginCounterPerPeriod = maxLoginPerPeriodParam ########### Change this value to set the maximum number of login attempts per period of time
        resetAFterDays = resetAFterDaysParam ########### Change this value to set the number of days after which the login counter resets

        resetAfterDateString = (currentDate + timedelta(days=resetAFterDays)).strftime(datetime_format)
        
        code = None
        try:
            code = str(authenticator.add_new_secrets(secretKeyParam=secretKey))
           
        except Exception as e:
            raise HTTPException(
                status_code = 400,
                detail = "Error generating code: {}".format(str(e))
            )
        
        
        
        incrementUserLoginQuery = "UPDATE {} SET {} = {} +1, {} = {}, {} = {} WHERE {} = '{}' and {} = '{}'".format(
            self.tableName,

            self.loginCounter_ColumnName,
            self.loginCounter_ColumnName,

            self.lastLoginDate_ColumnName,
            "'{}'".format(currentDateString),

            self.lastLoginCode_ColumnName,
            "'{}'".format(code),

            self.email_ColumnName,
            user.email,

            self.userCode_ColumnName,
            user.userCode
        )

        
        resetUserFirstAndExpiryDateQuery = "UPDATE {} SET {} = 1, {} = {}, {} = {}, {} = {}, {} = {} WHERE {} = '{}' and {} = '{}'".format(
            self.tableName,

            self.loginCounter_ColumnName,
        
            
             self.lastLoginDate_ColumnName,
            "'{}'".format(currentDateString),

            self.expiryDate_ColumnName,
            "'{}'".format(resetAfterDateString),

            self.firstLoginDate_ColumnName,
            "'{}'".format(currentDateString),

            self.lastLoginCode_ColumnName,
            "'{}'".format(code),

            self.userCode_ColumnName,
            user.userCode,

            self.email_ColumnName,
            user.email,
        )


        userData = await self._handleUserNotExist(userCode= user.userCode,email=user.email,startingRowParam=sheetStartingRowNumber,
                                                                        usersCodeColumnZeroBasedParam=sheetUsersCodesColumnNumber,
                                                                        phoneColumnNumber=phoneColumnNumber,
                                                                        daysColumnZeroBasedParam = sheetDaysLeft,
                                                                        sheetUrlParam=sheetUrl)
            

        # Check if the user is active
        if (userData[self.isActive_ColumnName] == False):
            raise HTTPException(
                status_code = 400,
                detail = "This user is disabled, please contact the admin to enable it"
            )

        # If the user has never logged in, set the first login date and expiry date
        if (userData[self.firstLoginDate_ColumnName] == None and userData[self.expiryDate_ColumnName] == None):
            try:
                print("User has never logged in, setting first login date and expiry date")
                await self.__systemDatabase.execute(resetUserFirstAndExpiryDateQuery)
                return GenericResponse({"code":code}).to_dict()
                
                
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
                return GenericResponse({"code":code}).to_dict()
            except Exception as e:
                raise HTTPException(
                    status_code = 400,
                    detail = "Error resetting user dates: {}".format(str(e))
                )
    

        try:

            await self.__systemDatabase.execute(incrementUserLoginQuery)
            return GenericResponse({"code":code}).to_dict()
        
        except Exception as e:
           
            raise HTTPException(
                status_code = 400,
                detail = "User does not exist: {}".format(str(e))
            )
    
    async def _handleUserNotExist(self, userCode,email, phoneColumnNumber,startingRowParam, usersCodeColumnZeroBasedParam, daysColumnZeroBasedParam, sheetUrlParam):
       

        userData = None

        try:
            userData = await self.getUserData(userCode=userCode,email=email)
        except Exception as e:
            userSheetData = await spreadsheet.scrapeDataFromSpreadSheet(startingRowParam=startingRowParam,
                                                                        usersCodeColumnZeroBasedParam=usersCodeColumnZeroBasedParam,
                                                                        daysColumnZeroBasedParam = daysColumnZeroBasedParam,
                                                                        sheetUrlParam=sheetUrlParam,phoneColumnNumberParam=phoneColumnNumber)
            userSheetItem = [item for item in userSheetData if item[0] == userCode]
            print("sheet user:", userSheetItem)

            if userSheetItem == []:
                raise HTTPException(
                    status_code = 400,
                    detail = "This Phone Number is not found in the sheet"
                )
            elif userData == None:
                try:
                    print("User does not exist, inserting new user")
                    userPhone = userSheetItem[0][1]
                    userData = await self.insertNewUser(RegisterModel(userCode = userCode,email= email,phone=userPhone))
                except Exception as e:
                    raise HTTPException(
                        status_code = 400,
                        detail = "Error inserting new user: {}".format(str(e))
                    )
        return userData
        
    
    async def getAllUsersForAdmin(self, email:str):
        await self.checkAndReturnAdmin(email)

        
        query = "SELECT * FROM {} WHERE {} = '{}'".format(
            self.tableName,
            
            self.email_ColumnName,
            email
        
        )
        allUsers = await self.__systemDatabase.fetch_all(query)
        
        return [{
            self.email_ColumnName:row[self.email_ColumnName],
            
            self.userCode_ColumnName:row[self.userCode_ColumnName],
            self.loginCounter_ColumnName:row[self.loginCounter_ColumnName],
            self.lastLoginDate_ColumnName:row[self.lastLoginDate_ColumnName],
            self.firstLoginDate_ColumnName:row[self.firstLoginDate_ColumnName],
            self.expiryDate_ColumnName:row[self.expiryDate_ColumnName],
            self.isActive_ColumnName:row[self.isActive_ColumnName],
        
        } for row in allUsers]
                
    async def getUserData(self, userCode:str, email:str, WithGenericResponse = False):

        query = "SELECT * FROM {} WHERE {} = '{}' and {} = '{}'".format(
        self.tableName,

        self.userCode_ColumnName,
        userCode,
        
        self.email_ColumnName,
        email
        )
        row = await self.__systemDatabase.fetch_one(query)
        if WithGenericResponse:
            return GenericResponse({
            self.email_ColumnName:row[self.email_ColumnName],
            self.phone_ColumnName:row[self.phone_ColumnName],
            self.lastLoginCode_ColumnName:row[self.lastLoginCode_ColumnName],
            self.loginCounter_ColumnName:row[self.loginCounter_ColumnName],
            self.lastLoginDate_ColumnName:row[self.lastLoginDate_ColumnName],
            self.firstLoginDate_ColumnName:row[self.firstLoginDate_ColumnName],
            self.expiryDate_ColumnName:row[self.expiryDate_ColumnName],
             self.isActive_ColumnName:row[self.isActive_ColumnName]
        }).to_dict()
        
        else:
            return {
                self.email_ColumnName:row[self.email_ColumnName],
                self.phone_ColumnName:row[self.phone_ColumnName],
                self.lastLoginCode_ColumnName:row[self.lastLoginCode_ColumnName],
                self.loginCounter_ColumnName:row[self.loginCounter_ColumnName],
                self.lastLoginDate_ColumnName:row[self.lastLoginDate_ColumnName],
                self.firstLoginDate_ColumnName:row[self.firstLoginDate_ColumnName],
                self.expiryDate_ColumnName:row[self.expiryDate_ColumnName],
                 self.isActive_ColumnName:row[self.isActive_ColumnName]
            }
        
        
       

