import typing
import requests
from bs4 import BeautifulSoup

async def scrapeDataFromSpreadSheet(startingRowParam: int , usersCodeColumnZeroBasedParam: int, daysColumnZeroBasedParam:int, sheetUrlParam:str):
    
    startingRow = startingRowParam ########### Change this value to set the starting row of the data in the Google Spreadsheet
    
    usersCodeColumnZeroBased = usersCodeColumnZeroBasedParam - 1 ########### Change this value to set the zero-based index of the phone column in the Google Spreadsheet

    daysColumnZeroBased = daysColumnZeroBasedParam - 1 ########### Change this value to set the zero-based index of the days column in the Google Spreadsheet
    

    ########### Change this value to set the URL of the Google Spreadsheet
    html = requests.get(sheetUrlParam) 
    
    html = html.text
    soup = BeautifulSoup(html, 'lxml')
    salas_cine = soup.find_all('table')[0]
    rows = [[td.text for td in row.find_all("td")] for row in salas_cine.find_all('tr')]
    columns = [td.text for td in salas_cine.find_all('th')]
    
    # return the rows of the first and second columns in the specified range
    # if startingRow < len(rows) and endingRow < len(rows):
    phoneList = [rows[i][usersCodeColumnZeroBased].replace("\"","") for i in range(startingRow, len(rows)-1)]
    daysList = [rows[j][daysColumnZeroBased] for j in range(startingRow, len(rows) -1 )]

    print("Phone Length:", len(phoneList))
    print("Phone List:", phoneList)
    # remove negative values from the days list and remove the corresponding phone numbers
    filteredData = [(phone, days) for phone, days in zip(phoneList, daysList) if days.isdigit() and int(days) >= 0]

    

    return {
        "data":
            { 
                "availableUser": filteredData
            }
        }
    
    
    