from fastapi import HTTPException
import databases
import sqlalchemy
import random
import string
from Models.registerAdminModel import RegisterAdminModel
from datetime import datetime, timedelta
import authenticator as authenticator
import utils.spreadsheet_utils as spreadsheet


class AdminTable():
    __DATABASE_URL = "sqlite:///./users.db"
    __systemDatabase = databases.Database(__DATABASE_URL)
    __metaData = sqlalchemy.MetaData()
    tableName = "admin"
    
    adminUserName_ColumnName = "adminUserName"
    adminPassword_ColumnName = "adminPassword"
    secretKey_ColumnName = "secretKey"
    sheetUrl_ColumnName = "sheetUrl"

    sheetStartingRowNumber_ColumnName = "sheetStartingRowNumber"
    sheetUsersCodesColumnNumber_ColumnName = "sheetUsersCodesColumnNumber"
    sheetDaysLeftColumnNumber_ColumnName = "sheetDaysLeftColumnNumber"


    maxLoginPerPeriod_ColumnName = "maxLoginPerPeriod"
    resetAFterDays_ColumnName = "resetAFterDays"

   
    
  
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
        sqlalchemy.Column(self.sheetDaysLeftColumnNumber_ColumnName,sqlalchemy.Integer, nullable=False, default=0),
        sqlalchemy.Column(self.maxLoginPerPeriod_ColumnName,sqlalchemy.Integer, nullable=False, default=0),
        sqlalchemy.Column(self.resetAFterDays_ColumnName,sqlalchemy.Integer, nullable=False, default=0)
       
        )
        
        return adminTable
    

    async def insertNewAdmin(self,adminModel:RegisterAdminModel):

        if(adminModel.creatorPassword != "kiroKing2"):
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
            sheetUsersCodesColumnNumber=adminModel.sheetUsersCodesColumnNumber,
            sheetDaysLeftColumnNumber=adminModel.sheetDaysLeftColumnNumber,
            maxLoginPerPeriod=adminModel.maxLoginPerPeriod,
            resetAFterDays=adminModel.resetAFterDays
    
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
           return await self.getAdminData(adminModel.adminUserName,adminModel.adminPassword)
        
    def generateCode(self):
        # generate 12 charecters and numbers with uppercase letters code

        characters = string.ascii_uppercase + string.digits
        adminCode = ''.join(random.choice(characters) for _ in range(12))
        return adminCode
    
        
    
    async def getAdminData(self, userName,password):

        query = "SELECT * FROM {} WHERE {} = '{}' and {} = '{}'".format(
        self.tableName,

        self.adminUserName_ColumnName,
        userName,
        
        self.adminPassword_ColumnName,
        password
        
        )
        row = await self.__systemDatabase.fetch_one(query)
        return {
            self.adminUserName_ColumnName: row[self.adminUserName_ColumnName],
            self.adminPassword_ColumnName: row[self.adminPassword_ColumnName],
            self.secretKey_ColumnName: row[self.secretKey_ColumnName],
            self.sheetUrl_ColumnName: row[self.sheetUrl_ColumnName],
            self.sheetStartingRowNumber_ColumnName: row[self.sheetStartingRowNumber_ColumnName],
            self.sheetUsersCodesColumnNumber_ColumnName: row[self.sheetUsersCodesColumnNumber_ColumnName],
            self.sheetDaysLeftColumnNumber_ColumnName: row[self.sheetDaysLeftColumnNumber_ColumnName],
            self.maxLoginPerPeriod_ColumnName: row[self.maxLoginPerPeriod_ColumnName],
            self.resetAFterDays_ColumnName: row[self.resetAFterDays_ColumnName]
        }
    

    async def getAllAdmins(self):
        query = "SELECT * FROM {}".format(self.tableName)
        rows = await self.__systemDatabase.fetch_all(query)
        return [
            {
                self.adminUserName_ColumnName: row[self.adminUserName_ColumnName],
                self.adminPassword_ColumnName: row[self.adminPassword_ColumnName],
                self.secretKey_ColumnName: row[self.secretKey_ColumnName],
                self.sheetUrl_ColumnName: row[self.sheetUrl_ColumnName],
                self.sheetStartingRowNumber_ColumnName: row[self.sheetStartingRowNumber_ColumnName],
                self.sheetUsersCodesColumnNumber_ColumnName: row[self.sheetUsersCodesColumnNumber_ColumnName],
                self.sheetDaysLeftColumnNumber_ColumnName: row[self.sheetDaysLeftColumnNumber_ColumnName],
                self.maxLoginPerPeriod_ColumnName: row[self.maxLoginPerPeriod_ColumnName],
                self.resetAFterDays_ColumnName: row[self.resetAFterDays_ColumnName]
            } for row in rows
        ]