import sys
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError
import pandas as pd
import requests
import time

df = pd.read_excel("data_j.xls")
df_stock = df[(df["市場・商品区分"] == "市場第二部（内国株）") |
         (df["市場・商品区分"] == "市場第一部（内国株）") |
         (df["市場・商品区分"] == "マザーズ（内国株）") |
         (df["市場・商品区分"] == "JASDAQ(スタンダード・内国株）")][["コード", "銘柄名"]]

ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
headers = {'User-Agent': ua}

for index, row in df_stock.iterrows():
    for year in reversed(range(1990, 2021)):
        # url = "https://kabuoji3.com/stock/" + str(row["コード"]) + "/" + str(year) + "/"

        response = requests.post(
            "https://kabuoji3.com/stock/file.php",
            {'code':row["コード"], 'year': year},
            headers=headers)
        if response.status_code != 200:
            break

        filename = "files/" + str(row["コード"]) + "_" + str(year) + ".csv"
        with open(filename, 'wb') as saveFile:
            saveFile.write(response.content)

        time.sleep(10)

    print(row["コード"])


# my_share = share.Share('7203.T')
# symbol_data = None
#
# try:
#     symbol_data = my_share.get_historical(share.PERIOD_TYPE_YEAR,
#                                           2,
#                                           share.FREQUENCY_TYPE_DAY,
#                                           1)
# except YahooFinanceError as e:
#     print(e.message)
#     sys.exit(1)
#
# df = pd.DataFrame(symbol_data)
# df["datetime"] = pd.to_datetime(df.timestamp, unit="ms")
# print(df.head())

