import datetime
import math

import yfinance as yf
import pandas as pd
import time

df = pd.read_excel("data_j.xls")
df_stock = df[(df["市場・商品区分"] == "市場第二部（内国株）") |
         (df["市場・商品区分"] == "市場第一部（内国株）") |
         (df["市場・商品区分"] == "マザーズ（内国株）") |
         (df["市場・商品区分"] == "JASDAQ(スタンダード・内国株）")][["コード", "銘柄名"]]

code_list = []

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
start = today + datetime.timedelta(days=-4)

today_str = start.strftime("%Y-%m-%d")
tomorrow_str = tomorrow.strftime("%Y-%m-%d")

print(today_str)
print(tomorrow_str)

for index, row in df_stock.iterrows():

    code = str(row["コード"]) + ".T"
    if len(code_list) < 2:
        code_list.append(code)
        continue

    tickers = " ".join(code_list)

    print(tickers)
    data = yf.download(tickers, start=today_str, end=tomorrow_str, group_by='tickers')

    for c in code_list:
        file_code = c[:-2]
        df_one = pd.read_csv("master/" + file_code + ".csv")

        for index2, row2 in data[c].iterrows():
            if math.isnan(row2["Close"]):
                continue

            date = index2.strftime("%Y-%m-%d")
            s = pd.Series(
                [date, row2["Open"], row2["High"], row2["Low"], row2["Close"], row2["Volume"], row2["Adj Close"]],
                index=["日付", "始値", "高値", "安値", "終値", "出来高", "終値調整値"])

            df_one = df_one.append(s, ignore_index=True)
            # 同一日を入れていたら片方削除する
            df_one = df_one.drop_duplicates(subset="日付", keep='last')

        df_one.to_csv("master/" + file_code + ".csv", index=False, encoding='utf_8_sig')
    code_list = []
    time.sleep(10)
