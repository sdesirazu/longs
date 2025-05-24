import yfinance as yf
import pandas as pd
microsoft = yf.Ticker('MSFT')
dict =  microsoft.info
df = pd.DataFrame.from_dict(dict,orient='index')
df = df.reset_index()
# Iterate through each row using itertuples
rowdata = []
for row in df.itertuples(index=True):
    rowdata.append(f"{row[1]},{row[2]}")

