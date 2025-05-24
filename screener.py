from pyfinviz.screener import Screener
from google.oauth2 import service_account
import time



import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

def connect_sheet():
    key_path = "/Users/js2009au/Projects/IBKR/creds.json"

    scoped_credentials = service_account.Credentials.from_service_account_file(key_path, scopes = [ 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive' ],)

    file = gspread.authorize(scoped_credentials) # authenticate the JSON key with gspread

    spreadsheet = file.open("TFT Automation")

    sheet = spreadsheet.worksheet("Finviz") #replace sheet_name with the name that corresponds to yours, e.g, it can be sheet1
    
    return [sheet,spreadsheet]

# Select the first worksheet
[worksheet,spreadsheet] = connect_sheet()

# with no params (default screener table)
pages = 500
screener = Screener(pages=[x for x in range(1, pages)])
# with params (The first 3 pages of "STOCKS ONLY" where Analyst recommend a strong buy)
options = [Screener.IndustryOption.STOCKS_ONLY_EX_FUNDS, Screener.AnalystRecomOption.STRONG_BUY_1]

# available variables:
print(screener.main_url)  # scraped URL

worksheet.clear()
for i in range(1,pages):

    big_rows = []
    df = screener.data_frames[i]
    # Write the DataFrame to the Google Sheet
    #worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    # Append each row of the DataFrame to the Google Sheet
    for index, row in df.iterrows():
        big_rows.append(row.values.tolist())

    worksheet.append_rows(big_rows)
    print("Program will pause for 5 seconds...")
    time.sleep(5)  # Sleep for 5 seconds
    print("Program resumed after 5 seconds.")


    print("DataFrame written to Google Sheet successfully!")

