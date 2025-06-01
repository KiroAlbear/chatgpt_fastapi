import typing
import requests
from bs4 import BeautifulSoup

async def scrapeDataFromSpreadSheet():
    
    startingRow = 6 ########### Change this value to set the starting row of the data in the Google Spreadsheet
    
    usersCodeColumnZeroBased = 16 - 1 ########### Change this value to set the zero-based index of the phone column in the Google Spreadsheet

    daysColumnZeroBased = 12 - 1 ########### Change this value to set the zero-based index of the days column in the Google Spreadsheet
    
    daysColumnName = "Days"
    phoneColumnName = "Phone"

    ########### Change this value to set the URL of the Google Spreadsheet
    html = requests.get('https://docs.google.com/spreadsheets/d/1acFuo3GuvEftzk13J8oKhsAIMg6DVHl1/edit?usp=sharing&ouid=116524698235408728905&rtpof=true&sd=true') 
    
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
    
    
    