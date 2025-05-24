from pytz import timezone
import gspread
from google.oauth2 import service_account
from bs4 import BeautifulSoup
import requests
import pandas_ta as ta
import pandas as pd
import yfinance as yf
import pandas_ta as ta
from datetime import datetime, timedelta
from datetime import date
from investing import retrieve_fred
from fear_and_greed import retrieve_fear_and_greed
import time

def get_all_finviz_stocks(sheet):
    worksheet = sheet.worksheet("Finviz") #replace sheet_name with the name that corresponds to yours, e.g, it can be sheet1
    rows = worksheet.get_all_values()

    big_list = []
    # Iterate through each row and print it
    for row in rows:
        if 'B' in row[6]:
            big_list.append(row[1])

    return big_list

def get_yesterday():
    # Get today's date
    today = datetime.now()

    # Calculate yesterday's date
    yesterday = today - timedelta(days=1)

    # Print yesterday's date
    return yesterday.date()

def income_stmt_balance_sheet(sheet):
    # write it to the sheet 
    microsoft = yf.Ticker('MSFT')
    shares_outstanding = microsoft.info['sharesOutstanding']

    df =  microsoft.income_stmt
    date_array = []
    for i in range(len(df.columns)):
        timestamp = df.columns[i]
        # Get the date part
        date_part = timestamp.date().year
        date_array.append(date_part)

    df = df.reset_index()
    # Iterate through each row using itertuples
    sheet = sheet.worksheet("MSFT") #replace sheet_name with the name that corresponds to yours, e.g, it can be sheet1
    sheet.clear()
    big_rows = []
    rowdata = []
    rowdata.append("Shares Outstanding")
    rowdata.append(f"{shares_outstanding}")
    big_rows.append(rowdata)
    sheet.append_rows(big_rows)

    big_rows = []
    calc_map = {}
    for row in df.itertuples(index=True):
        if (row[1] == 'Net Income' or row[1] == 'Stockholders Equity' or row[1] == 'Total Assets' or row[1] == 'Basic EPS'):
            rowdata = []
            rowdata.append(f"{row[1]}")
            rowdata.append(f"{row[2]}")
            rowdata.append(f"{row[3]}")
            rowdata.append(f"{row[4]}")
            rowdata.append(f"{row[5]}")
            calc_map[row[1]] = rowdata
            big_rows.append(rowdata)
            sheet.append_rows(big_rows)

    df =  microsoft.balance_sheet

    # Get total equity (usually found under 'Total Assets' - 'Total Liabilities')
    total_equity = df.loc['Total Assets'] - df.loc['Total Liabilities Net Minority Interest']
    rowdata.append("Total Equity")
    rowdata.append(f"{total_equity}")
    big_rows.append(rowdata)
    sheet.append_rows(big_rows)

    df = df.reset_index()
    # Iterate through each row using itertuples
    big_rows = []
    for row in df.itertuples(index=True):
        if (row[1] == 'Net Income' or row[1] == 'Stockholders Equity' or row[1] == 'Total Assets' or row[1] == 'Basic EPS'):
            rowdata = []
            rowdata.append(f"{row[1]}")
            rowdata.append(f"{row[2]}")
            rowdata.append(f"{row[3]}")
            rowdata.append(f"{row[4]}")
            rowdata.append(f"{row[5]}")
            calc_map[row[1]] = rowdata
            big_rows.append(rowdata)
            sheet.append_rows(big_rows)

    net_income_array = calc_map['Net Income']
    stock_equity_array = calc_map['Stockholders Equity']
    eps_array = calc_map['Basic EPS']

    rowdata = []
    big_rows = []
    rowdata.append("Return on Equity")
    for i in range(1, 5):
        roe = float(net_income_array[i])*100.0/float(stock_equity_array[i])
        rowdata.append(f"{roe}")
    big_rows.append(rowdata)
    sheet.append_rows(big_rows)

    # dividends
    df =  microsoft.dividends

    annual_dividends = df.resample('Y').sum()  # Resample to get annual dividends
    
    dividend_map = {}
    for key in annual_dividends.keys():
        date_part = key.date().year
        dividend_map[date_part] = annual_dividends[key]

    rowdata = []
    div_rowdata = []
    big_rows = []
    rowdata.append("Dividend Payout Ratio")
    div_rowdata.append("Dividend")
    if len(dividend_map) != 0:
        for i in range(4):
            dividend_val = dividend_map[date_array[i]]
            div_rowdata.append(dividend_val)
            # see the +1
            payout_ratio = dividend_val*100.0/float(eps_array[i+1])
            rowdata.append(payout_ratio)
        big_rows.append(rowdata)
        big_rows.append(div_rowdata)
        sheet.append_rows(big_rows)

def old_income_stmt_balance_sheet(sheet):
    # write it to the sheet 
    microsoft = yf.Ticker('MSFT')
    df =  microsoft.income_stmt
    df = df.reset_index()
    # Iterate through each row using itertuples
    sheet = sheet.worksheet("MSFT") #replace sheet_name with the name that corresponds to yours, e.g, it can be sheet1
    sheet.clear()
    big_rows = []
    for row in df.itertuples(index=True):
        rowdata = []
        rowdata.append(f"{row[1]}")
        rowdata.append(f"{row[2]}")
        rowdata.append(f"{row[3]}")
        rowdata.append(f"{row[4]}")
        rowdata.append(f"{row[5]}")
        big_rows.append(rowdata)

    sheet.append_rows(big_rows)

    df =  microsoft.balance_sheet
    df = df.reset_index()
    # Iterate through each row using itertuples
    big_rows = []
    for row in df.itertuples(index=True):
        rowdata = []
        rowdata.append(f"{row[1]}")
        rowdata.append(f"{row[2]}")
        rowdata.append(f"{row[3]}")
        rowdata.append(f"{row[4]}")
        rowdata.append(f"{row[5]}")
        big_rows.append(rowdata)
    sheet.append_rows(big_rows)

    # dividends
    df =  microsoft.dividends
    df = df.reset_index()
    # Iterate through each row using itertuples
    big_rows = []
    for row in df.itertuples(index=True):
        rowdata = []
        rowdata.append(f"{row[1]}")
        rowdata.append(f"{row[2]}")
        big_rows.append(rowdata)
    sheet.append_rows(big_rows)

def test_ticker(sheet):

    microsoft = yf.Ticker('MSFT')
    dict =  microsoft.info
    df = pd.DataFrame.from_dict(dict,orient='index')
    df = df.reset_index()
    # Iterate through each row using itertuples
    sheet = sheet.worksheet("MSFT") #replace sheet_name with the name that corresponds to yours, e.g, it can be sheet1
    sheet.clear()
    big_rows = []
    for row in df.itertuples(index=True):
        rowdata = []
        rowdata.append(float(f"{row[1]}"))
        rowdata.append(float(f"{row[2]}"))
        big_rows.append(rowdata)

    sheet.append_rows(big_rows)

def connect_sheet():
    key_path = "/Users/js2009au/Projects/IBKR/creds.json"

    scoped_credentials = service_account.Credentials.from_service_account_file(key_path, scopes = [ 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive' ],)

    file = gspread.authorize(scoped_credentials) # authenticate the JSON key with gspread

    spreadsheet = file.open("TFT Automation")

    sheet = spreadsheet.worksheet("Market Analysis") #replace sheet_name with the name that corresponds to yours, e.g, it can be sheet1
    
    return [sheet,spreadsheet]

def add_header(worksheet):
    rowdata = []
    # Get all values from the worksheet
    data = worksheet.get_all_values()

    # Count the number of filled rows
    filled_rows = sum(1 for row in data if any(cell.strip() for cell in row))

    if filled_rows == 0:
        rowdata = ["Date","SPY 50 day average","SPY last","Stoch(k)","Stoch(d)", "RSI","VIX","S5FI","Fred","Fear and Greed","Markets Risk","Other Risks"]
        worksheet.append_row(rowdata)

def clean_sheet(worksheet):
    rowdata = []
    # Get all values from the worksheet
    data = worksheet.get_all_values()

    # Count the number of filled rows
    filled_rows = sum(1 for row in data if any(cell.strip() for cell in row))

    print(f"Number of filled rows: {filled_rows}")
    if filled_rows > 30:
        worksheet.clear()
        rowdata = ["Date","SPY 50 day average","SPY last","Stoch(k)","Stoch(d)","RSI","VIX","S5FI","Fred","Fear and Greed","Markets Risk","Other Risks"]
        worksheet.append_row(rowdata)

def write_sheet(row_data, sheet):
    # Insert the row at the desired index (e.g., at the end of the sheet)
    sheet.append_row(row_data)

def get_spy():

    url = 'https://www.slickcharts.com/sp500'

    request = requests.get(url,headers={'User-Agent': 'Mozilla/5.0'})

    soup = BeautifulSoup(request.text, "lxml")

    stats = soup.find('table',class_='table table-hover table-borderless table-sm')

    df =pd.read_html(str(stats))[0]

    return(df['Symbol'].tolist())

def get_current_price(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)

    # Get the current share price
    current_price = stock.history(period='1d')['Close'][0]
    return current_price

# this includes the whole set of rules from Tino's spreadsheet
def old_retrieve_and_store(symbol, rowdata, sheet):
    try:
        df = yf.Ticker(symbol)
        data = df.history(period="1d")  # Attempt to get historical data
    
        if data.empty:
            print(f"No price data found for {symbol}. It may be delisted.")
            return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    df = df.history(period='6mo')[['Open', 'High', 'Low', 'Close', 'Volume']]
    # volume today
    vol_today = df['Volume'].iloc[-1]
    # mean volume
    avg_volume = df['Volume'].mean()
    # Add some indicators
    df.ta.stoch(high='high', low='low', k=14, d=3, append=True)
    k=df.iloc[-1:]['STOCHk_14_3_3'].iloc[0]
    d=df[-1:]['STOCHd_14_3_3'].iloc[0]
    rsi = df.ta.rsi().iloc[-1:].iloc[0]
    # check if rsi has reversed.  It needs to be above 30 now and in  previousndays below 30
    rsilist = df.ta.rsi().tolist()
    rsilist.reverse()
    now_time = datetime.now(timezone('Australia/Sydney'))
    fmt = "%Y-%m-%d %H:%M:%S %Z%z"
    now_time = now_time.strftime(fmt)
    if k < 20 and d > k:
        if vol_today > avg_volume:
            if rsilist[0] >= 30 and rsilist[1] <= 30:
                rowdata = []
                print("Symbol", symbol, " TRADE", "REVERSAL") 
                rowdata.append(now_time)
                rowdata.append(f"{symbol}") 
                rowdata.append("OK TO TRADE REVERSAL") 
                rowdata.append(get_current_price(symbol)) 
                sheet.append_row(rowdata)

def retrieve_and_store(symbol, rowdata, sheet):
    try:
        df = yf.Ticker(symbol)
        data = df.history(period="1d")  # Attempt to get historical data
    
        if data.empty:
            print(f"No price data found for {symbol}. It may be delisted.")
            return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    df = df.history(period='6mo')[['Open', 'High', 'Low', 'Close', 'Volume']]
    # Add some indicators
    rsi = df.ta.rsi().iloc[-1:].iloc[0]
    # check if rsi has reversed.  It needs to be above 30 now and in  previousndays below 30
    rsilist = df.ta.rsi().tolist()
    rsilist.reverse()
    now_time = datetime.now(timezone('Australia/Sydney'))
    fmt = "%Y-%m-%d %H:%M:%S %Z%z"
    now_time = now_time.strftime(fmt)
    if rsilist[0] >= 30 and rsilist[1] <= 30:
        rowdata = []
        print("Symbol", symbol, " TRADE", "REVERSAL") 
        rowdata.append(now_time)
        rowdata.append(f"{symbol}") 
        rowdata.append("OK TO TRADE REVERSAL") 
        rowdata.append(get_current_price(symbol)) 
        sheet.append_row(rowdata)
    
def retrieve_and_sell(symbol, rowdata, sheet):
    try:
        df = yf.Ticker(symbol)
        data = df.history(period="1d")  # Attempt to get historical data
    
        if data.empty:
            print(f"No price data found for {symbol}. It may be delisted.")
            return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    df = df.history(period='6mo')[['Open', 'High', 'Low', 'Close', 'Volume']]
    rsi = df.ta.rsi().iloc[-1:].iloc[0]
    # check if rsi has reversed.  It needs to be below 70 now and above 70 yesterday
    rsilist = df.ta.rsi().tolist()
    rsilist.reverse()
    now_time = datetime.now(timezone('Australia/Sydney'))
    fmt = "%Y-%m-%d %H:%M:%S %Z%z"
    now_time = now_time.strftime(fmt)
    if rsilist[1] >= 70 and rsilist[0] <= 70:
        rowdata = []
        print("Symbol", symbol, " SELL", "REVERSAL") 
        rowdata.append(now_time)
        rowdata.append(f"{symbol}") 
        rowdata.append("OK TO SELL REVERSAL") 
        rowdata.append(get_current_price(symbol)) 
        sheet.append_row(rowdata)

##################################################
[sheet, spreadsheet] = connect_sheet()
#income_stmt_balance_sheet(spreadsheet)

rowdata=[]
now_time = datetime.now(timezone('Australia/Sydney'))
fmt = "%Y-%m-%d %H:%M:%S %Z%z"
now_time = now_time.strftime(fmt)
rowdata.append(now_time)

# get historical pricing data
df = yf.Ticker('^spx')
time.sleep(2)  # Sleep for 5 seconds
rowdata.append(float(f"{df.info['fiftyDayAverage']}"))
time.sleep(2)  # Sleep for 5 seconds
rowdata.append(float(f"{df.info['regularMarketPrice']}"))
time.sleep(2)  # Sleep for 5 seconds
df = df.history(period='6mo')[['Open', 'High', 'Low', 'Close']]
time.sleep(2)  # Sleep for 5 seconds
# Add some indicators
df.ta.stoch(high='high', low='low', k=14, d=3, append=True)
time.sleep(2)  # Sleep for 5 seconds
sto_k=df.iloc[-1:]['STOCHk_14_3_3'].iloc[0]
sto_d=df[-1:]['STOCHd_14_3_3'].iloc[0]
rowdata.append(float(f"{sto_k}"))
rowdata.append(float(f"{sto_d}"))
rsi=df.ta.rsi().iloc[-1:].iloc[0]
rowdata.append(float(f"{rsi}"))
time.sleep(2)  # Sleep for 5 seconds

# get the current $VIX
df = yf.Ticker('^VIX')
time.sleep(1)  # Sleep for 5 seconds
vix=df.info['regularMarketPrice']
time.sleep(2)  # Sleep for 5 seconds
rowdata.append(float(f"{vix}"))

list_of_spy_stocks = get_spy()
list_of_spy_stocks.remove('BRK.B')
list_of_spy_stocks.remove('BF.B')
list_of_stocks = get_all_finviz_stocks(spreadsheet)
    
d = datetime.today() - timedelta(days=210)
print("Start date:", d.date())

df = yf.download(tickers=list_of_spy_stocks, start=d.date(), end=date.today())

df = df.stack()

df['50_wma'] = df.groupby(level=1)['Close']\
                 .transform(lambda x: ta.wma(close=x, length=50))

df['200_wma'] = df.groupby(level=1)['Close']\
                  .transform(lambda x: ta.wma(close=x, length=200))

df['above_50_wma'] = df.apply(lambda x: 1 if (x['Close'] > x['50_wma'])
                                          else 0, axis=1)

df['above_200_wma'] = df.apply(lambda x: 1 if (x['Close'] > x['200_wma'])
                                           else 0, axis=1)

xx = (df.groupby(level=0)['above_50_wma'].sum()/len(list_of_spy_stocks))*100
s5fi = xx.iloc[-1]
rowdata.append(float(f"{s5fi}"))
fred=float(retrieve_fred())
rowdata.append(float(f"{fred}"))
fear_and_greed=float(retrieve_fear_and_greed())
rowdata.append(float(f"{fear_and_greed}"))
# retrieve and store sto and rsi for each of the tickers it might be enough for now to store last values
####################
#test_ticker(spreadsheet)
add_header(sheet)
clean_sheet(sheet)
share_sheet = spreadsheet.worksheet("Shares to Trades") 
sell_sheet = spreadsheet.worksheet("Shares to sell") 
####################
if vix < 25 and fred <= 0 and fear_and_greed < 45:
    rowdata.append("MARKETS LOW RISK")
    if rsi < 30 and sto_k < 20 and s5fi < 40:
        rowdata.append("SHARES LOW RISK")
    elif rsi > 30 and sto_k > 20 and s5fi > 40:
        rowdata.append("SHARES NEUTRAL RISK")
    else:
        rowdata.append("SHARES HIGH RISK")
    for item in list_of_stocks:
        retrieve_and_store(item,rowdata, share_sheet)
        time.sleep(1)  # Sleep for 5 seconds
        retrieve_and_sell(item,rowdata, sell_sheet)
        time.sleep(1)  # Sleep for 5 seconds
elif vix > 25 and vix < 30 and fred > 0 and fred < 1 and fear_and_greed > 45 and fear_and_greed < 55:
    rowdata.append("MARKETS NEUTRAL RISK")
    if rsi < 30 and sto_k < 20 and s5fi < 40:
        rowdata.append("SHARES LOW RISK")
    elif rsi > 30 and sto_k > 20 and s5fi > 40:
        rowdata.append("SHARES NEUTRAL RISK")
    else:
        rowdata.append("SHARES HIGH RISK")
    for item in list_of_stocks:
        retrieve_and_store(item,rowdata, share_sheet)
        time.sleep(2)  # Sleep for 5 seconds
        retrieve_and_sell(item,rowdata, sell_sheet)
        time.sleep(2)  # Sleep for 5 seconds
elif vix > 30:
    rowdata.append("MARKETS HIGH RISK")
    rowdata.append("SELL FOR PROFIT")
    for item in list_of_stocks:
        retrieve_and_store(item,rowdata, share_sheet)
        time.sleep(1)  # Sleep for 5 seconds
        retrieve_and_sell(item,rowdata, sell_sheet)
        time.sleep(1)  # Sleep for 5 seconds
else:
    rowdata.append("UNKNOWN RISK")
    rowdata.append("UNKNOWN")
    for item in list_of_stocks:
        retrieve_and_store(item,rowdata, share_sheet)
        time.sleep(2)  # Sleep for 5 seconds
        retrieve_and_sell(item,rowdata, sell_sheet)
        time.sleep(2)  # Sleep for 5 seconds

write_sheet(rowdata,sheet)
