from fastapi import HTTPException
import databases
import sqlalchemy

import random
import string
from Models.User.loginModel import LoginModel
from Models.User.registerModel import RegisterModel
from Models.User.enableDisableModel import EnableDisableUserModel
from Models.User.resetAllAdminUsersCodesModel import ResetAllAdminUsersCodesModel
from Models.User.getAdminUsersModel import GetAdminUsersModel
from Models.User.adminOrUserModel import AdminOrUserModel
from Models.User.userModel import UserModel
from Models.User.deleteUserModel import DeleteUserModel


from Models.generic_response import GenericResponse
from DataBaseTables.adminTable import AdminTable
from datetime import datetime, timedelta
import authenticator as authenticator

class UserTable():
    __DATABASE_URL = "sqlite:///./users.db"
    __systemDatabase = databases.Database(__DATABASE_URL)
    __metaData = sqlalchemy.MetaData()
    tableName = "users"
    email_ColumnName = "email"
    name_ColumnName = "name"
    phone_ColumnName = "phone"
    startDate_ColumnName = "startDate"
    endDate_ColumnName = "endDate"
    daysLeft = "daysLeft"
    
    userCode_ColumnName = "userCode"
    loginCounter_ColumnName = "loginCounter"
    lastLoginCode_ColumnName = "lastLoginCode"
    
    lastLoginDate_ColumnName = "lastLoginDate"
    firstLoginDate_ColumnName = "firstLoginDate"
    expiryDate_ColumnName = "expiryDate"
    isActive_ColumnName = "isActive"
    isMaximumCodesReached = "isMaximumCodesReached"

    datetime_format = "%Y-%m-%d"

  
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
        sqlalchemy.Column(self.name_ColumnName,sqlalchemy.String,nullable=True),
        sqlalchemy.Column(self.phone_ColumnName,sqlalchemy.String,nullable=True),
       

        sqlalchemy.Column(self.startDate_ColumnName, sqlalchemy.String, nullable=True),
        sqlalchemy.Column(self.endDate_ColumnName, sqlalchemy.String, nullable=True),

        sqlalchemy.Column(self.loginCounter_ColumnName,sqlalchemy.Integer, nullable=False, default=0),
        sqlalchemy.Column(self.lastLoginDate_ColumnName, sqlalchemy.String, nullable=True),
        sqlalchemy.Column(self.lastLoginCode_ColumnName, sqlalchemy.String, nullable=True),
        sqlalchemy.Column(self.firstLoginDate_ColumnName, sqlalchemy.String,nullable=True),
        sqlalchemy.Column(self.expiryDate_ColumnName, sqlalchemy.String,nullable=True ),
        sqlalchemy.Column(self.isActive_ColumnName, sqlalchemy.Boolean,nullable=False, default=True)

        )
        

        return usersTable
    

    async def generateCode(self,withGenericResponse = False):
        
        # while the code already exists in the database, generate a new code
        # generate 12 charecters and numbers with uppercase letters code
        generatedCode = None
        while True:
            characters = string.ascii_uppercase + string.digits
            generatedCode = ''.join(random.choice(characters) for _ in range(12))

            user_verification_query = "SELECT * FROM {} WHERE {} = '{}' ".format(
                self.tableName,

                self.userCode_ColumnName,
                generatedCode,

            )
            
            user_verification_record = await self.__systemDatabase.fetch_all(user_verification_query)
            if len(user_verification_record) == 0:
                break

        if withGenericResponse:
            return GenericResponse({"generatedCode": generatedCode}).to_dict()
        else:
            return generatedCode
    
    async def deleteUser(self, model:DeleteUserModel):
        await AdminTable().getAdminData(userName=model.email,password=model.password)
        
        query = "DELETE FROM {} WHERE {} = '{}' and {} = '{}'".format(
            self.tableName,

            self.userCode_ColumnName,
            model.userCode,

            self.email_ColumnName,
            model.email
        )
        
        result = await self.__systemDatabase.execute(query)
        if result is None:
            raise HTTPException(
                status_code = 400,
                detail = "User not found"
            )
        return await AdminTable().getAllAdminUsers(model=GetAdminUsersModel(email=model.email,password=model.password))
    
    async def deleteAllUsersOfAdmin(self, email:str):
       
        query = "DELETE FROM {} WHERE {} = '{}'".format(
            self.tableName,

            self.email_ColumnName,
            email
        )
        
        await self.__systemDatabase.execute(query)

    async def insertNewUser(self,userModel:RegisterModel):
        admin_data = await AdminTable().getAdminData(userName=userModel.email,password=None)

        user_verification_query = "SELECT * FROM {} WHERE {} = '{}' ".format(
            self.tableName,

            self.email_ColumnName,
            userModel.email,

        )
        user_verification_record = await self.__systemDatabase.fetch_all(user_verification_query)

        if admin_data[AdminTable.isFreeTrial_ColumnName] == True and len(user_verification_record) >= 1:
            raise HTTPException(
                status_code = 400,
                detail = "This account is in free trial, it is allowed to register only one user, please contact us to register more users"
            )

        generatedCode = await self.generateCode()
        
        query = self.__usersTable.insert().values(
        email = userModel.email,
        name = userModel.name,
        userCode = generatedCode,
        phone = userModel.phone,
       
        startDate = userModel.startDate,
        endDate = userModel.endDate,
        loginCounter = 0,
        lastLoginDate = None,
        firstLoginDate = None,
        expiryDate = None,
        isActive = True,
    )


        await self.__systemDatabase.execute(query)
        return await self.getUserData(userCode=generatedCode,email=userModel.email,WithGenericResponse=True)
        

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
    
        query = "UPDATE {} SET {} = {} WHERE {} = '{}' and {} = '{}'".format(
            self.tableName,


            self.isActive_ColumnName,
            model.isActive,

            self.userCode_ColumnName,
            model.userCode,

            self.email_ColumnName,
            model.email
        )
      
    
        await self.__systemDatabase.execute(query)
        return await self.getUserData(userCode=model.userCode,email=model.email, WithGenericResponse=True,checkIfUserIsActive=False)
        

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
            if user_record:
                return GenericResponse({
                    "isAdmin": False,
                }).to_dict()
        except Exception:
            print("User not found")
            raise HTTPException(
                status_code = 400,
                detail = "Wrong email or password, please try again"
            )
          
    

    async def resetUser(self,user:LoginModel):
        resetUserFirstAndExpiryDateQuery = "UPDATE {} SET {} = 0, {} = {}, {} = {} WHERE {} = '{}' and {} = '{}'".format(
        self.tableName,

        self.loginCounter_ColumnName,
    
        
        self.lastLoginDate_ColumnName,
        'NULL',

        self.expiryDate_ColumnName,
        'NULL',



        self.userCode_ColumnName,
        user.userCode,

        self.email_ColumnName,
        user.email,
        )
        await self.__systemDatabase.execute(resetUserFirstAndExpiryDateQuery)
       
        return await self.getUserData(userCode=user.userCode,email=user.email, WithGenericResponse=True)

    async def requestCodeForUser(self,user:LoginModel):
        admin_record =  await AdminTable().getAdminData(userName=user.email,password=None)

        maxLoginPerPeriodParam = admin_record[AdminTable.maxLoginPerPeriod_ColumnName] 
        resetAFterDaysParam = admin_record[AdminTable.resetAFterDays_ColumnName] 
         
        secretKey = admin_record[AdminTable.secretKey_ColumnName]

        currentDate = datetime.now()
        currentDateString = currentDate.strftime(self.datetime_format)

        maxUserLoginCounterPerPeriod = maxLoginPerPeriodParam ########### Change this value to set the maximum number of login attempts per period of time
        resetAFterDays = resetAFterDaysParam ########### Change this value to set the number of days after which the login counter resets

        resetAfterDateString = (currentDate + timedelta(days=resetAFterDays)).strftime(self.datetime_format)
        
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


        # userData = await self._handleUserNotExist(userCode= user.userCode,email=user.email,startingRowParam=sheetStartingRowNumber,
        #                                                                 usersCodeColumnZeroBasedParam=sheetUsersCodesColumnNumber,
        #                                                                 phoneColumnNumber=phoneColumnNumber,
        #                                                                 daysColumnZeroBasedParam = sheetDaysLeft,
        #                                                                 sheetUrlParam=sheetUrl)
            
        userData = await self.getUserData(userCode=user.userCode,email=user.email)
        # Check if the user is active


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

        if(expiryDateString == None):
          expiryDateString = currentDateString
            

        # firstLoginDate = datetime.strptime(firstLoginDateString, datetime_format)
        expiryDate = datetime.strptime(expiryDateString, self.datetime_format)
            
        
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
    
        
    def calculateDaysLeft(self, startDate:str, endDate:str):
              
        start_date = datetime.strptime(startDate, self.datetime_format)
        end_date = datetime.strptime(endDate, self.datetime_format)
        
        # Calculate the difference in days
        days_left = (end_date - start_date).days
        
        return days_left if days_left > 0 else 0
    
    
    async def getAllUsersForAdmin(self, email:str):
        await AdminTable().getAdminData(userName=email,password=None)

        
        query = "SELECT * FROM {} WHERE {} = '{}'".format(
            self.tableName,
            
            self.email_ColumnName,
            email
        
        )
        allUsers = await self.__systemDatabase.fetch_all(query)
        
        return [{
            self.email_ColumnName:row[self.email_ColumnName],
            self.name_ColumnName:row[self.name_ColumnName],
            self.phone_ColumnName:row[self.phone_ColumnName],
            self.daysLeft: self.calculateDaysLeft(row[self.startDate_ColumnName], row[self.endDate_ColumnName]),
            self.startDate_ColumnName:row[self.startDate_ColumnName],
            self.endDate_ColumnName:row[self.endDate_ColumnName],
            self.userCode_ColumnName:row[self.userCode_ColumnName],
            self.loginCounter_ColumnName:row[self.loginCounter_ColumnName],
            self.lastLoginDate_ColumnName:row[self.lastLoginDate_ColumnName],
            self.firstLoginDate_ColumnName:row[self.firstLoginDate_ColumnName],
            self.expiryDate_ColumnName:row[self.expiryDate_ColumnName],
            self.isActive_ColumnName:row[self.isActive_ColumnName],
        
        } for row in allUsers]
                
    async def getUserData(self, userCode:str, email:str, WithGenericResponse = False,checkIfUserIsActive = True):
        admin_record =  await AdminTable().getAdminData(userName=email,password=None)
        maxLoginPerPeriodParam = admin_record[AdminTable.maxLoginPerPeriod_ColumnName]
       

        query = "SELECT * FROM {} WHERE {} = '{}' and {} = '{}'".format(
        self.tableName,

        self.userCode_ColumnName,
        userCode,
        
        self.email_ColumnName,
        email
        )
        row = await self.__systemDatabase.fetch_one(query)

        if row is None:
            raise HTTPException(
                status_code = 400,
                detail = "User not found"
            )
        
        if checkIfUserIsActive:
            if (row[self.isActive_ColumnName] == False):
                raise HTTPException(
                    status_code = 400,
                    detail = "This user is disabled, please contact the admin to enable it"
                )
        
        # check if the user is expired
        startDateString = row[self.startDate_ColumnName]
        endDateString = row[self.endDate_ColumnName]

        daysLeft = self.calculateDaysLeft(startDateString, endDateString)

        if daysLeft <= 0:
            raise HTTPException(
                    status_code = 400,
                    detail = "This user subscription has expired"
                )

        

        isMaxReached = row[self.loginCounter_ColumnName] >= maxLoginPerPeriodParam

        userResponse = {
            self.userCode_ColumnName:row[self.userCode_ColumnName],
            self.email_ColumnName:row[self.email_ColumnName],
            self.name_ColumnName:row[self.name_ColumnName],
            self.phone_ColumnName:row[self.phone_ColumnName],
            self.startDate_ColumnName:row[self.startDate_ColumnName],
            self.endDate_ColumnName:row[self.endDate_ColumnName],
            self.daysLeft:daysLeft,
            self.lastLoginCode_ColumnName:row[self.lastLoginCode_ColumnName],
            self.loginCounter_ColumnName:row[self.loginCounter_ColumnName],
            self.lastLoginDate_ColumnName:row[self.lastLoginDate_ColumnName],
            self.firstLoginDate_ColumnName:row[self.firstLoginDate_ColumnName],
            self.expiryDate_ColumnName:row[self.expiryDate_ColumnName],
            self.isActive_ColumnName:row[self.isActive_ColumnName],
            self.isMaximumCodesReached:isMaxReached,
        }

        if WithGenericResponse:
            return GenericResponse(userResponse).to_dict()
        
        else:
            return userResponse
        
        
       

