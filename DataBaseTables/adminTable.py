from fastapi import HTTPException
import databases
import sqlalchemy
from Models.Admin.registerAdminModel import RegisterAdminModel
from Models.Admin.updateAdminModel import UpdateAdminModel
from Models.Admin.enableDisableAdminModel import EnableDisableAdminModel
from Models.Admin.registerAdminUserModel import RegisterAdminUserModel
from Models.generic_response import GenericResponse
from Models.User.userModel import UserModel
import DataBaseTables.userTable as userTable
from Models.User.getAdminUsersModel import GetAdminUsersModel


from datetime import datetime, timedelta
import authenticator as authenticator



class AdminTable():
    __DATABASE_URL = "sqlite:///./users.db"
    __systemDatabase = databases.Database(__DATABASE_URL)
    __metaData = sqlalchemy.MetaData()
    tableName = "admin"
    creatorPassword = "kiroKing2"
    
    adminUserName_ColumnName = "adminUserName"
    adminPassword_ColumnName = "adminPassword"
    secretKey_ColumnName = "secretKey"
   

    startDate_ColumnName = "startDate"
    endDate_ColumnName = "endDate"
    daysLeft = "daysLeft"



    maxLoginPerPeriod_ColumnName = "maxLoginPerPeriod"
    resetAFterDays_ColumnName = "resetAFterDays"
    isActive_ColumnName = "isActive"
    isFreeTrial_ColumnName = "isFreeTrial"

    datetime_format = "%Y-%m-%d"

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
        sqlalchemy.Column(self.startDate_ColumnName, sqlalchemy.String, nullable=True),
        sqlalchemy.Column(self.endDate_ColumnName, sqlalchemy.String, nullable=True),

        sqlalchemy.Column(self.maxLoginPerPeriod_ColumnName,sqlalchemy.Integer, nullable=False, default=0),
        sqlalchemy.Column(self.resetAFterDays_ColumnName,sqlalchemy.Integer, nullable=False, default=0),
        sqlalchemy.Column(self.isActive_ColumnName, sqlalchemy.Boolean,nullable=False, default=True),
        sqlalchemy.Column(self.isFreeTrial_ColumnName, sqlalchemy.Boolean,nullable=False, default=True),
       
        )
        
        return adminTable
    

    async def addNewAdmin(self,adminModel:RegisterAdminUserModel):
        start_date = datetime.now()
        end_date = start_date + timedelta(days=2)

        start_date_str = start_date.strftime(self.datetime_format)
        end_date_str = end_date.strftime(self.datetime_format)

        query = self.__adminTable.insert().values(
            adminUserName=adminModel.adminUserName.strip(),
            adminPassword=adminModel.adminPassword.strip(),
            secretKey=adminModel.secretKey.strip(),
            startDate=start_date_str,
            endDate=end_date_str,
            maxLoginPerPeriod=adminModel.maxLoginPerPeriod,
            resetAFterDays=adminModel.resetAFterDays,
            isActive=True,
            isFreeTrial=True
           
    
    )
        ###################################################################################################
        # Check if the adminUserName already exists with user name or secret key
        adminUserName_verification_query = "SELECT * FROM {} WHERE {}= '{}' OR {}= '{}'".format(
           self.tableName,

           self.adminUserName_ColumnName,
           adminModel.adminUserName,

           self.secretKey_ColumnName,
           adminModel.secretKey,
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
           return await self.getAdminData(userName=adminModel.adminUserName,password=adminModel.adminPassword ,withGenericResponse=True)


    async def insertNewAdmin(self,adminModel:RegisterAdminModel):

        if(adminModel.creatorPassword != self.creatorPassword):
            raise HTTPException(
             status_code = 400,
             detail = "Creator password is incorrect"
            )

        query = self.__adminTable.insert().values(
            adminUserName=adminModel.adminUserName.strip(),
            adminPassword=adminModel.adminPassword.strip(),
            secretKey=adminModel.secretKey.strip(),
            startDate=adminModel.startDate,
            endDate=adminModel.endDate,
            maxLoginPerPeriod=adminModel.maxLoginPerPeriod,
            resetAFterDays=adminModel.resetAFterDays,
            isActive=True,
            isFreeTrial=False
           
    
    )
        ###################################################################################################

        adminUserName_verification_query = "SELECT * FROM {} WHERE {}= '{}' OR {}= '{}'".format(
           self.tableName,

           self.adminUserName_ColumnName,
           adminModel.adminUserName,

           self.secretKey_ColumnName,
           adminModel.secretKey,
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
           return await self.getAdminData(userName=adminModel.adminUserName,password=adminModel.adminPassword ,withGenericResponse=True)
        
    async def deleteAdmin(self,email:str,creatorPassword:str):
        if(creatorPassword != self.creatorPassword):
            raise HTTPException(
                status_code=400,
                detail="Creator password is incorrect"
            )

        query = "DELETE FROM {} WHERE {} = '{}'".format(
            self.tableName,
            
            self.adminUserName_ColumnName,

            email.strip(),
           
        )
        await userTable.UserTable().deleteAllUsersOfAdmin(email=email)
        await self.__systemDatabase.execute(query)
        return GenericResponse({"message": "Admin deleted successfully"}).to_dict()
    

    async def enableDisableAdmin(self,adminModel:EnableDisableAdminModel):

        if(adminModel.creatorPassword != self.creatorPassword):
            raise HTTPException(
                status_code=400,
                detail="Creator password is incorrect"
            )

       

        query = "UPDATE {} SET {} = {} WHERE {} = '{}'".format(
            self.tableName,
            self.isActive_ColumnName,
            adminModel.isActive,

            self.adminUserName_ColumnName,
            adminModel.adminUserName
        )
        await self.__systemDatabase.execute(query)
        return await self.getAdminData(userName=adminModel.adminUserName,password=None)
        
    async def updateAdmin(self,adminModel:UpdateAdminModel):

        await self.getAdminData(userName=adminModel.adminUserName,password=adminModel.adminPassword)

        query = "UPDATE {} SET  {} = '{}', {} = '{}', {} = '{}' WHERE {} = '{}' and {} = '{}'".format(
            self.tableName,

            self.secretKey_ColumnName,
            adminModel.secretKey.strip(),


            self.maxLoginPerPeriod_ColumnName,
            adminModel.maxLoginPerPeriod,

            self.resetAFterDays_ColumnName,
            adminModel.resetAFterDays,


            self.adminUserName_ColumnName,
            adminModel.adminUserName.strip(),

            self.adminPassword_ColumnName,
            adminModel.adminPassword.strip()
        )
        await self.__systemDatabase.execute(query)
        return await self.getAdminData(userName=adminModel.adminUserName,password=adminModel.adminPassword, withGenericResponse=True)

        
    

    async def getAllAdminUsers(self,model:GetAdminUsersModel):
        userTableClass = userTable.UserTable()
        admin_record =  await self.getAdminData(userName=model.email,password=model.password)

        
        admin_email = admin_record[self.adminUserName_ColumnName]
       
  
        maxLoginPerPeriod = admin_record[self.maxLoginPerPeriod_ColumnName]

        
        userData = await userTableClass.getAllUsersForAdmin(email=model.email)

        # if userData is None or len(userData) == 0:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="No users found for this admin"
        #     )

        usersList = []
        for user in userData:
            startDateString = user[userTableClass.startDate_ColumnName]
            endDateString = user[userTableClass.endDate_ColumnName]
            # Calculate the difference in days
            daysLeft = userTable.UserTable().calculateDaysLeft(startDate=startDateString, endDate=endDateString)
            userModel = UserModel(
                        userCode=user[userTableClass.userCode_ColumnName],
                        userPhone=user[userTableClass.phone_ColumnName],
                        daysLeft=daysLeft,
                        email=admin_email,
                        name=user[userTableClass.name_ColumnName],
                        expiryDate = user[userTableClass.expiryDate_ColumnName],
                        startDate = startDateString,
                        endDate = endDateString,
                        lastLoginDate = user[userTableClass.lastLoginDate_ColumnName],
                        firstLoginDate = user[userTableClass.firstLoginDate_ColumnName],
                        loginCount = user[userTableClass.loginCounter_ColumnName],
                        isActive = user[userTableClass.isActive_ColumnName],
                        isMaximumCodesReached = user[userTableClass.loginCounter_ColumnName] >= maxLoginPerPeriod
                        
                      
                    )
            
            usersList.append(userModel)

        return GenericResponse({"usersList":usersList}).to_dict()
                   

        
        
    
    async def getAdminData(self, userName,password,withGenericResponse=False):
        query = None
        if password == None:
            query = "SELECT * FROM {} WHERE {} = '{}' ".format(
            self.tableName,

            self.adminUserName_ColumnName,
            userName,
                    
            )
        else:
            query = "SELECT * FROM {} WHERE {} = '{}' and {} = '{}'".format(
            self.tableName,

            self.adminUserName_ColumnName,
            userName,

            self.adminPassword_ColumnName,
            password
                    
            )

        row = await self.__systemDatabase.fetch_one(query)

        if row is None:
            raise HTTPException(
                status_code=400,
                detail="Admin is not found"
            )

        if row[self.isActive_ColumnName] == 0:
            raise HTTPException(
                status_code=400,
                detail="Admin is disabled"
            )
        
        startDateString = row[self.startDate_ColumnName]
        endDateString = row[self.endDate_ColumnName]

        # Calculate the difference in days
        days_left =  userTable.UserTable().calculateDaysLeft(startDate=startDateString, endDate=endDateString) 

        if days_left < 0:
            raise HTTPException(
                status_code=400,
                detail="Admin subscription has expired"
            )
        
        adminData = {
            self.adminUserName_ColumnName: row[self.adminUserName_ColumnName],
            self.adminPassword_ColumnName: row[self.adminPassword_ColumnName],
            self.secretKey_ColumnName: row[self.secretKey_ColumnName],
            self.startDate_ColumnName: row[self.startDate_ColumnName],
            self.endDate_ColumnName: row[self.endDate_ColumnName],
            self.daysLeft: days_left,
            self.maxLoginPerPeriod_ColumnName: row[self.maxLoginPerPeriod_ColumnName],
            self.resetAFterDays_ColumnName: row[self.resetAFterDays_ColumnName],
            self.isActive_ColumnName: row[self.isActive_ColumnName],
            self.isFreeTrial_ColumnName: row[self.isFreeTrial_ColumnName]
        }

        if withGenericResponse:
            return GenericResponse(adminData).to_dict()
        else:
            return adminData
        
    

    async def getAllAdmins(self):
        query = "SELECT * FROM {}".format(self.tableName)
        rows = await self.__systemDatabase.fetch_all(query)
        return GenericResponse({"admins":[
            {
            self.adminUserName_ColumnName: row[self.adminUserName_ColumnName],
            self.adminPassword_ColumnName: row[self.adminPassword_ColumnName],
            self.secretKey_ColumnName: row[self.secretKey_ColumnName],
            self.startDate_ColumnName: row[self.startDate_ColumnName],
            self.endDate_ColumnName: row[self.endDate_ColumnName],
            self.daysLeft: userTable.UserTable().calculateDaysLeft(startDate=ow[self.startDate_ColumnName], endDate=row[self.endDate_ColumnName]),
            self.maxLoginPerPeriod_ColumnName: row[self.maxLoginPerPeriod_ColumnName],
            self.resetAFterDays_ColumnName: row[self.resetAFterDays_ColumnName],
            self.isActive_ColumnName: row[self.isActive_ColumnName] 
        } for row in rows
        ]}).to_dict()
