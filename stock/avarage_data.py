import os

import pandas as pd

df = pd.read_excel("data_j.xls")
df_stock = df[(df["市場・商品区分"] == "市場第二部（内国株）") |
         (df["市場・商品区分"] == "市場第一部（内国株）") |
         (df["市場・商品区分"] == "マザーズ（内国株）") |
         (df["市場・商品区分"] == "JASDAQ(スタンダード・内国株）")][["コード", "銘柄名"]]

def get_average(data, num):
    length = len(end_data)
    d = data[length - num:length]
    return sum(d) / len(d)

for index, row in df_stock.iterrows():
    df_all = pd.DataFrame(index=[], columns=["日付", "始値", "高値", "安値", "終値", "出来高", "終値調整値", "5日平均", "10日平均", "25日平均", "75日平均", "200日平均"])

    end_data = []

    df_one = pd.read_csv("merged/" + str(row["コード"]) + ".csv", encoding='utf_8_sig')
    for index2, row2 in df_one.iterrows():

        end_data.append(row2["終値"])
        average_5 = None
        if len(end_data) >= 5:
            average_5 = get_average(end_data, 5)
        average_10 = None
        if len(end_data) >= 10:
            average_10 = get_average(end_data, 10)
        average_25 = None
        if len(end_data) >= 25:
            average_25 = get_average(end_data, 25)
        average_75 = None
        if len(end_data) >= 75:
            average_75 = get_average(end_data, 75)
        average_200 = None
        if len(end_data) >= 200:
            average_200 = get_average(end_data, 200)

        s = pd.Series([row2["日付"], row2["始値"], row2["高値"], row2["安値"], row2["終値"], row2["出来高"], row2["終値調整値"], average_5, average_10, average_25, average_75, average_200],
                  index=["日付", "始値", "高値", "安値", "終値", "出来高", "終値調整値", "5日平均", "10日平均", "25日平均", "75日平均", "200日平均"])
        # df_d = pd.concat([df_d, s])
        df_all = df_all.append(s, ignore_index=True)

    print(df_all)
    df_all.to_csv("averaged/" + str(row["コード"]) + ".csv", index=False, encoding='utf_8_sig')
