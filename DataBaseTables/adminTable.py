from fastapi import HTTPException
import databases
import sqlalchemy
import random
import string
from Models.Admin.registerAdminModel import RegisterAdminModel
from Models.Admin.updateAdminModel import UpdateAdminModel
from Models.Admin.enableDisableAdminModel import EnableDisableAdminModel
from Models.generic_response import GenericResponse
from Models.User.userModel import UserModel
import DataBaseTables.userTable as userTable
from Models.User.getAdminUsersModel import GetAdminUsersModel


from datetime import datetime, timedelta
import authenticator as authenticator
import utils.spreadsheet_utils as spreadsheet


class AdminTable():
    __DATABASE_URL = "sqlite:///./users.db"
    __systemDatabase = databases.Database(__DATABASE_URL)
    __metaData = sqlalchemy.MetaData()
    tableName = "admin"
    creatorPassword = "kiroKing2"
    
    adminUserName_ColumnName = "adminUserName"
    adminPassword_ColumnName = "adminPassword"
    secretKey_ColumnName = "secretKey"
    sheetUrl_ColumnName = "sheetUrl"


    sheetStartingRowNumber_ColumnName = "sheetStartingRowNumber"
    sheetUsersCodesColumnNumber_ColumnName = "sheetUsersCodesColumnNumber"
    sheetPhoneColumnNumber_ColumnName = "sheetPhoneColumnNumber"
    sheetDaysLeftColumnNumber_ColumnName = "sheetDaysLeftColumnNumber"


    maxLoginPerPeriod_ColumnName = "maxLoginPerPeriod"
    resetAFterDays_ColumnName = "resetAFterDays"
    isActive_ColumnName = "isActive"

   
    
  
    __adminTable = 0

    def createAndReturnAdminTable(self):
        
        self.__adminTable = self.__getAdminTable()
    
        engine = sqlalchemy.create_engine(
        self.__DATABASE_URL,connect_args={"check_same_thread": False}
        )
        self.__metaData.create_all(engine)
        return self.__adminTable

    def __getAdminTable(self):
        adminTable = sqlalchemy.Table(
        self.tableName,
        self.__metaData,
        sqlalchemy.Column(self.adminUserName_ColumnName,sqlalchemy.String,primary_key=True),
        sqlalchemy.Column(self.adminPassword_ColumnName, sqlalchemy.String, nullable=True),
        sqlalchemy.Column(self.secretKey_ColumnName, sqlalchemy.String, nullable=True),
        sqlalchemy.Column(self.sheetUrl_ColumnName, sqlalchemy.String, nullable=True),
        sqlalchemy.Column(self.sheetStartingRowNumber_ColumnName, sqlalchemy.Integer, nullable=False, default=0),
        sqlalchemy.Column(self.sheetUsersCodesColumnNumber_ColumnName, sqlalchemy.Integer, nullable=False, default=0 ),

        sqlalchemy.Column(self.sheetPhoneColumnNumber_ColumnName, sqlalchemy.Integer, nullable=False, default=0 ),
        sqlalchemy.Column(self.sheetDaysLeftColumnNumber_ColumnName,sqlalchemy.Integer, nullable=False, default=0),
        sqlalchemy.Column(self.maxLoginPerPeriod_ColumnName,sqlalchemy.Integer, nullable=False, default=0),
        sqlalchemy.Column(self.resetAFterDays_ColumnName,sqlalchemy.Integer, nullable=False, default=0),
        sqlalchemy.Column(self.isActive_ColumnName, sqlalchemy.Boolean,nullable=False, default=True)
       
        )
        
        return adminTable
    

    async def insertNewAdmin(self,adminModel:RegisterAdminModel):

        if(adminModel.creatorPassword != self.creatorPassword):
            raise HTTPException(
             status_code = 400,
             detail = "Creator password is incorrect"
            )

        query = self.__adminTable.insert().values(
            adminUserName=adminModel.adminUserName,
            adminPassword=adminModel.adminPassword,
            secretKey=adminModel.secretKey,
            sheetUrl=adminModel.sheetUrl,
            sheetStartingRowNumber=adminModel.sheetStartingRowNumber,
            sheetPhoneColumnNumber=adminModel.sheetPhoneColumnNumber,
            sheetUsersCodesColumnNumber=adminModel.sheetUsersCodesColumnNumber,
            sheetDaysLeftColumnNumber=adminModel.sheetDaysLeftColumnNumber,
            maxLoginPerPeriod=adminModel.maxLoginPerPeriod,
            resetAFterDays=adminModel.resetAFterDays,
            isActive=True
           
    
    )
        ###################################################################################################

        adminUserName_verification_query = "SELECT * FROM {} WHERE {}= '{}'".format(
           self.tableName,

           self.adminUserName_ColumnName,
           adminModel.adminUserName,
        )
        adminUserName_verification_record = await self.__systemDatabase.fetch_all(adminUserName_verification_query)

        ###################################################################################################

        
     
        if(len(adminUserName_verification_record) > 0):
            raise HTTPException(
             status_code = 400,
             detail = "This Admin already exists"
            )

        
        else:
           await self.__systemDatabase.execute(query)
           return await self.getAdminData(adminModel.adminUserName,True)
        
    async def enableDisableAdmin(self,adminModel:EnableDisableAdminModel):

        if(adminModel.creatorPassword != self.creatorPassword):
            raise HTTPException(
                status_code=400,
                detail="Creator password is incorrect"
            )

        verify_query = "SELECT * FROM {} WHERE {} = '{}' ".format(
            self.tableName,
            self.adminUserName_ColumnName,
            adminModel.adminUserName
        )
        verify_record = await self.__systemDatabase.fetch_one(verify_query)
        if not verify_record:
            raise HTTPException(
                status_code=400,
                detail="Admin does not exist"
            )
        query = "UPDATE {} SET {} = {} WHERE {} = '{}'".format(
            self.tableName,
            self.isActive_ColumnName,
            adminModel.isActive,

            self.adminUserName_ColumnName,
            adminModel.adminUserName
        )
        await self.__systemDatabase.execute(query)
        return await self.getAdminData(adminModel.adminUserName,True)
        
    async def updateAdmin(self,adminModel:UpdateAdminModel):

        verify_query = "SELECT * FROM {} WHERE {} = '{}' and {} = '{}' ".format(
            self.tableName,

            self.adminUserName_ColumnName,
            adminModel.adminUserName,

            self.adminPassword_ColumnName,
            adminModel.adminPassword
        )
        verify_record = await self.__systemDatabase.fetch_one(verify_query)
        if not verify_record:
            raise HTTPException(
                status_code=400,
                detail="Admin credentials are incorrect"
            )
        query = "UPDATE {} SET  {} = '{}', {} = '{}', {} = '{}', {} = {}, {} = {}, {} = {}, {} = {}, {} = '{}' WHERE {} = '{}' and {} = '{}'".format(
            self.tableName,

            self.secretKey_ColumnName,
              adminModel.secretKey,

            self.sheetUrl_ColumnName,
              adminModel.sheetUrl,

            self.sheetStartingRowNumber_ColumnName,
              adminModel.sheetStartingRowNumber,

            self.sheetUsersCodesColumnNumber_ColumnName,
              adminModel.sheetUsersCodesColumnNumber,

            self.sheetDaysLeftColumnNumber_ColumnName,
              adminModel.sheetDaysLeftColumnNumber,

            self.maxLoginPerPeriod_ColumnName,
              adminModel.maxLoginPerPeriod,

            self.resetAFterDays_ColumnName,
              adminModel.resetAFterDays,


            self.sheetPhoneColumnNumber_ColumnName,
              adminModel.sheetPhoneColumnNumber,


            self.adminUserName_ColumnName,
            adminModel.adminUserName,

            self.adminPassword_ColumnName,
            adminModel.adminPassword
        )
        await self.__systemDatabase.execute(query)
        return await self.getAdminData(adminModel.adminUserName,True)

        
    

        
    def generateCode(self):
        # generate 12 charecters and numbers with uppercase letters code

        characters = string.ascii_uppercase + string.digits
        adminCode = ''.join(random.choice(characters) for _ in range(12))
        return GenericResponse({"systemCode":adminCode}).to_dict()
        
        
    


    async def getAllAdminUsers(self,model:GetAdminUsersModel):
        admin_record = await userTable.UserTable().checkAndReturnAdmin(email=model.email)

        

        sheetStartingRowNumber = admin_record[self.sheetStartingRowNumber_ColumnName]
        sheetUsersCodesColumnNumber = admin_record[self.sheetUsersCodesColumnNumber_ColumnName] 
        sheetPHoneColumnNumber = admin_record[self.sheetPhoneColumnNumber_ColumnName]
        sheetDaysLeft = admin_record[self.sheetDaysLeftColumnNumber_ColumnName] 
        sheetUrl = admin_record[self.sheetUrl_ColumnName]
        password = admin_record[self.adminPassword_ColumnName]

        if model.password != password:
            raise HTTPException(
                status_code=400,
                detail="Admin incorrect username or password"
            )


        sheetUserData =  await spreadsheet.scrapeDataFromSpreadSheet(startingRowParam=sheetStartingRowNumber,
                                                            usersCodeColumnZeroBasedParam=sheetUsersCodesColumnNumber,
                                                            phoneColumnNumberParam=sheetPHoneColumnNumber,
                                                            daysColumnZeroBasedParam = sheetDaysLeft,
                                                            sheetUrlParam=sheetUrl)

        if sheetUserData == []:
            raise HTTPException(
                status_code = 400,
                detail = "No Active users found in the sheet"
            )
        
        userData = await userTable.UserTable().getAllUsersForAdmin(email=model.email)

        usersList = []
        for sheetUser in sheetUserData:
            userModel = UserModel(
                        userCode=sheetUser[0],
                        userPhone=sheetUser[1],
                        daysLeft=sheetUser[2],
                        expiryDate=None,
                        lastLoginDate=None,
                        loginCount=None,
                        isActive=1
                        
                      
                    )
            
            for user in userData:
                if sheetUser[0] == user[userTable.UserTable.userCode_ColumnName]:
                    userModel.expiryDate = user[userTable.UserTable.expiryDate_ColumnName]
                    userModel.lastLoginDate = user[userTable.UserTable.lastLoginDate_ColumnName]
                    userModel.loginCount = user[userTable.UserTable.loginCounter_ColumnName]
                    userModel.isActive = user[userTable.UserTable.isActive_ColumnName]
                    break
            usersList.append(userModel)

        return GenericResponse({"usersList":usersList}).to_dict()
                   

        
        
    
    async def getAdminData(self, userName,withGenericResponse=False):

        query = "SELECT * FROM {} WHERE {} = '{}' ".format(
        self.tableName,

        self.adminUserName_ColumnName,
        userName,
        

        
        )
        row = await self.__systemDatabase.fetch_one(query)
        if withGenericResponse:
            return GenericResponse({
            self.adminUserName_ColumnName: row[self.adminUserName_ColumnName],
            self.adminPassword_ColumnName: row[self.adminPassword_ColumnName],
            self.secretKey_ColumnName: row[self.secretKey_ColumnName],
            self.sheetUrl_ColumnName: row[self.sheetUrl_ColumnName],
            self.sheetStartingRowNumber_ColumnName: row[self.sheetStartingRowNumber_ColumnName],
            self.sheetPhoneColumnNumber_ColumnName: row[self.sheetPhoneColumnNumber_ColumnName],
            self.sheetUsersCodesColumnNumber_ColumnName: row[self.sheetUsersCodesColumnNumber_ColumnName],
            self.sheetDaysLeftColumnNumber_ColumnName: row[self.sheetDaysLeftColumnNumber_ColumnName],
            self.maxLoginPerPeriod_ColumnName: row[self.maxLoginPerPeriod_ColumnName],
            self.resetAFterDays_ColumnName: row[self.resetAFterDays_ColumnName],
            self.isActive_ColumnName: row[self.isActive_ColumnName] 
        }).to_dict()
        else:
            return {
                self.adminUserName_ColumnName: row[self.adminUserName_ColumnName],
                self.adminPassword_ColumnName: row[self.adminPassword_ColumnName],
                self.secretKey_ColumnName: row[self.secretKey_ColumnName],
                self.sheetUrl_ColumnName: row[self.sheetUrl_ColumnName],
                self.sheetStartingRowNumber_ColumnName: row[self.sheetStartingRowNumber_ColumnName],
                self.sheetPhoneColumnNumber_ColumnName: row[self.sheetPhoneColumnNumber_ColumnName],
                self.sheetUsersCodesColumnNumber_ColumnName: row[self.sheetUsersCodesColumnNumber_ColumnName],
                self.sheetDaysLeftColumnNumber_ColumnName: row[self.sheetDaysLeftColumnNumber_ColumnName],
                self.maxLoginPerPeriod_ColumnName: row[self.maxLoginPerPeriod_ColumnName],
                self.resetAFterDays_ColumnName: row[self.resetAFterDays_ColumnName],
                self.isActive_ColumnName: row[self.isActive_ColumnName] 
            }
        
    

    async def getAllAdmins(self):
        query = "SELECT * FROM {}".format(self.tableName)
        rows = await self.__systemDatabase.fetch_all(query)
        return GenericResponse({"admins":[
            {
                self.adminUserName_ColumnName: row[self.adminUserName_ColumnName],
                self.adminPassword_ColumnName: row[self.adminPassword_ColumnName],
                self.secretKey_ColumnName: row[self.secretKey_ColumnName],
                self.sheetUrl_ColumnName: row[self.sheetUrl_ColumnName],
                self.sheetStartingRowNumber_ColumnName: row[self.sheetStartingRowNumber_ColumnName],
                self.sheetPhoneColumnNumber_ColumnName: row[self.sheetPhoneColumnNumber_ColumnName],
                self.sheetUsersCodesColumnNumber_ColumnName: row[self.sheetUsersCodesColumnNumber_ColumnName],
                self.sheetDaysLeftColumnNumber_ColumnName: row[self.sheetDaysLeftColumnNumber_ColumnName],
                self.maxLoginPerPeriod_ColumnName: row[self.maxLoginPerPeriod_ColumnName],
                self.resetAFterDays_ColumnName: row[self.resetAFterDays_ColumnName]
            } for row in rows
        ]}).to_dict()
