import yfinance as yf
import pandas as pd

# Replace 'AAPL' with the ticker symbol of the stock you want to check
ticker_symbol = 'AAPL'
stock = yf.Ticker(ticker_symbol)

# Get historical dividends
dividends = stock.dividends
dividends_df = pd.DataFrame(dividends).tz_localize(None)

# Get the income statement data
income_stmt = stock.financials

# Get the net income from the income statement
net_income = income_stmt.loc['Net Income']

# Resample the dividends to annual data
annual_dividends = dividends_df.resample('Y').sum()

# Convert net income to a DataFrame and ensure it's timezone-naive
net_income_df = pd.DataFrame(net_income).tz_localize(None)
breakpoint()

# Resample the net income to annual data
annual_net_income = net_income_df.resample('Y').sum()

# Create a DataFrame to calculate the payout ratio
payout_ratio = pd.DataFrame({
    'Dividends': annual_dividends,
    'Net Income': annual_net_income['Net Income']
})

# Calculate the payout ratio
payout_ratio['Payout Ratio'] = payout_ratio['Dividends'] / payout_ratio['Net Income']

# Display the historical payout ratio
print(payout_ratio)
