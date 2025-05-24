import yfinance as yf
import pandas as pd

ticker = yf.Ticker("AAPL")
dividends = ticker.dividends
financials = ticker.financials

# Calculate dividend payout ratio
if dividends is not None and financials is not None:
    eps = financials.loc['Basic EPS']
    dividend_per_share = dividends.mean()
    eps_mean = eps.mean()
    dividend_payout_ratio = dividend_per_share / eps_mean
    print("Dividend Payout Ratio:", dividend_payout_ratio)
else:
    print("Dividend or financial data not available")

