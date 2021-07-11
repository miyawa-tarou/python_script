import yfinance as yf

import pandas as pd
import requests
import time
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError

msft = yf.Ticker("MSFT")

# get stock info
print(msft.info)

# get historical market data
hist = msft.history(period="5d")
print(hist)

df = pd.read_excel("data_j.xls")
df_stock = df[(df["市場・商品区分"] == "市場第二部（内国株）") |
         (df["市場・商品区分"] == "市場第一部（内国株）") |
         (df["市場・商品区分"] == "マザーズ（内国株）") |
         (df["市場・商品区分"] == "JASDAQ(スタンダード・内国株）")][["コード", "銘柄名"]]

# for index, row in df_stock.iterrows():

# data = yf.download("7203.T", start="2021-07-01", end="2021-07-02", interval="1d")
# print(data)

my_share = share.Share('7203.T')
symbol_data = None

try:
    symbol_data = my_share.get_historical(share.PERIOD_TYPE_YEAR,
                                          2,
                                          share.FREQUENCY_TYPE_DAY,
                                          1)
except YahooFinanceError as e:
    print(e.message)
    sys.exit(1)

df = pd.DataFrame(symbol_data)
df["datetime"] = pd.to_datetime(df.timestamp, unit="ms")
print(df.head())

