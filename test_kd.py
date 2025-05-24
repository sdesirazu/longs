
# 1. Package
import datetime
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


# 2. 定義函式 (1)
# 2.1 stockCode: 股票代號
# 2.2 historicalDays: 資料回看天數
# 2.3 twFlag: 是否為台灣股票(Y/N)
def stockDownload(stockCode=2330, historicalDays=30, twFlag="Y"):
    
    # 定義變數 - 股票代號
    if twFlag == "Y":
        sid = str(stockCode) + ".TW"
    else:
        sid = str(stockCode)
    
    # 定義變數 - 資料起日
    start = datetime.datetime.now() - datetime.timedelta(days=historicalDays)
    
    # 定義變數 - 資料迄日
    end = datetime.date.today()
    
    # 下載股票資料
    return yf.download(sid, start, end)

# 2. 定義函式 (2)
# 2.1 stockData: 資料集名稱
# 2.2 plotTitle: 圖表標題
def drawMean(stockData, plotTitle="5/20/60 Mean Avg."):
    
    # 線型圖，收盤價、5日均線、20日均線、60日均線
    stockData['Adj Close'].plot(figsize=(16, 8))
    stockData['Adj Close'].rolling(window=5).mean().plot(figsize=(16, 8), label='5_Day_Mean')
    stockData['Adj Close'].rolling(window=20).mean().plot(figsize=(16, 8), label='20_Day_Mean')
    stockData['Adj Close'].rolling(window=60).mean().plot(figsize=(16, 8), label='60_Day_Mean')

    # 顯示格線
    plt.grid(axis='y', color='0.8')

    # 顯示側標
    plt.legend(loc='upper left', shadow=True, fontsize='medium')
    
    # 顯示標題
    plt.title(plotTitle)
    
    return plt.show()

# 包成函數: K/D值天數, K/D值圖
# KD 隨機指標: https://www.ezchart.com.tw/inds.php?IND=KD
# 2. 定義函式 (3)
# 2.1 stockData: 資料集名稱
# 2.2 kdDays: k/d計算基礎天數(預設9天)
# 2.3 plotTitle: 圖表標題
def kdCalculator(stockData,kdDays=9,plotTitle="K/D"):
    
    kd_stock_prep = stockData.copy()
    
    kd_stock_prep['Max Price For Past N Days'] = kd_stock_prep['Close'].rolling(kdDays).max()
    kd_stock_prep['Min Price For Past N Days'] = kd_stock_prep['Close'].rolling(kdDays).min()
    
    # Step 1: 第n天收盤價 - 最近n天內最低價
    kd_stock_prep['Step1'] = kd_stock_prep['Close'] - kd_stock_prep['Min Price For Past N Days']

    # Step 2: 最近n天內最高價 - 最近n天內最低價
    kd_stock_prep['Step2'] = kd_stock_prep['Max Price For Past N Days'] - kd_stock_prep['Min Price For Past N Days']

    # Step 3: RSV
    kd_stock_prep['RSV'] = (kd_stock_prep['Step1'] / kd_stock_prep['Step2']) * 100
    
    
    # Step 4.1: 建立 Derived Value, 計算前一日設置為 50
    df = kd_stock_prep.reset_index()
    target_index = kdDays - 2
    df.loc[target_index,'K'] = 50
    df.loc[target_index,'D'] = 50
    
    
    # Step 4.2: 計算K/D
    # 當日K值(%K)= 2/3 前一日 K值 + 1/3 RSV
    # 當日D值(%D)= 2/3 前一日 D值＋ 1/3 當日K值
    
    target_start = kdDays - 1

    for i in range(1, len(df)):
        if i >= target_start:
            df.loc[i, 'K'] = df.loc[i-1, 'K'] * (2/3) + df.loc[i, 'RSV'] * (1/3)

    for i in range(1, len(df)):
        if i >= target_start:
            df.loc[i, 'D'] = df.loc[i-1, 'D'] * (2/3) + df.loc[i, 'K'] * (1/3)
    
    # Step 5: 畫圖
    df = df.set_index('Date')

    # 線型圖，K/D值
    plt.figure(figsize=(16, 8))
    plt.plot(df['K'], label = "K", linestyle="-.")
    plt.plot(df['D'], label = "D", linestyle="-")
    # 顯示側標
    plt.legend(loc='upper left', shadow=True, fontsize='small')

    # 顯示參考線
    # K值
    plt.axhline(y = 80, color = 'r', linestyle = '-.')
    plt.axhline(y = 20, color = 'g', linestyle = '-.')
    # D值
    plt.axhline(y = 70, color = 'r', linestyle = '-')
    plt.axhline(y = 30, color = 'g', linestyle = '-')

    # 顯示標題
    plt.title(plotTitle)
    plt.show()
    
    return df, plt.show()


# 3. 建立總呼叫函式
def plotStock(stockCode=2330
              ,historicalDays=180
              ,twFlag="Y"
              ,meanPlotTitle="5/20/60 Mean Avg."
              ,kdDays=9
              ,kdPlotTitle="K/D"):
    
    stock_dr = stockDownload(stockCode=stockCode, historicalDays=historicalDays, twFlag=twFlag)
    drawMean(stockData=stock_dr, plotTitle=meanPlotTitle)
    result,plot = kdCalculator(stockData=stock_dr,kdDays=kdDays,plotTitle=kdPlotTitle)
    
    return result,plot

stockCode = "NVDA"

historicalDays = 180
twFlag = "N"
meanPlotTitle = "5/20/60 Mean Avg." + "-" + str(stockCode)
kdDays = 9
kdPlotTitle = "K/D" + "-" + str(stockCode)

dataFrame, kdPlot = plotStock(stockCode=stockCode
                              ,historicalDays=historicalDays
                              ,twFlag=twFlag
                              ,meanPlotTitle=meanPlotTitle
                              ,kdDays=kdDays
                              ,kdPlotTitle=kdPlotTitle)



