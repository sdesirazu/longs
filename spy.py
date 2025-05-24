from bs4 import BeautifulSoup
import requests
import yfinance as yf
import pandas_ta as ta
import pandas as pd
def get_spy():

    url = 'https://www.slickcharts.com/sp500'

    request = requests.get(url,headers={'User-Agent': 'Mozilla/5.0'})

    soup = BeautifulSoup(request.text, "lxml")

    stats = soup.find('table',class_='table table-hover table-borderless table-sm')

    df =pd.read_html(str(stats))[0]

    print(df['Symbol'].tolist())
    return df

print(get_spy())
