import os

import pandas as pd
import math

df = pd.read_excel("data_j.xls")
df_stock = df[(df["市場・商品区分"] == "市場第二部（内国株）") |
         (df["市場・商品区分"] == "市場第一部（内国株）") |
         (df["市場・商品区分"] == "マザーズ（内国株）") |
         (df["市場・商品区分"] == "JASDAQ(スタンダード・内国株）")][["コード", "銘柄名"]]

for index, row in df_stock.iterrows():
    data_5 = []
    data_10 = []
    data_25 = []
    data_75 = []
    data_price = []

    gxFlag = True

    df_one = pd.read_csv("averaged/" + str(row["コード"]) + ".csv", encoding='utf_8_sig')
    for index2, row2 in df_one.iterrows():
        data_10.append(row2["10日平均"])
        data_25.append(row2["25日平均"])
        data_75.append(row2["75日平均"])
        data_price.append(row2["終値"])

        # 平均の上昇場
        average_25_Flag = False
        if not math.isnan(row2["25日平均"]) and not math.isnan(data_25[index2 - 1]):
            average_25_Flag =  (row2["25日平均"] - data_25[index2 - 1]) > 0
        average_75_Flag = False
        if not math.isnan(row2["75日平均"]) and not math.isnan(data_75[index2 - 1]):
            average_75_Flag =  (row2["75日平均"] - data_75[index2 - 1]) > 0

        # 傾きが上がった瞬間を確認
        gradientFlag = False
        gradientFlagB = False
        if not math.isnan(row2["25日平均"]) and not math.isnan(data_25[index2 - 1]) and not math.isnan(data_25[index2 - 2]):
            gradientA = (row2["25日平均"] - data_25[index2 - 1]) / row2["25日平均"]
            gradientB = (data_25[index2 - 1] - data_25[index2 - 2]) / data_25[index2 - 1]
            # この傾き係数は変える余地あり
            if gradientA > 0.001 and (gradientA - gradientB) > 0.0005:
                gradientFlag = True
            if gradientA < gradientB:
                gradientFlagB = True
        gradientFlagC = False
        if not math.isnan(row2["10日平均"]) and not math.isnan(data_10[index2 - 1]) and not math.isnan(data_10[index2 - 2]):
            gradientA = (row2["10日平均"] - data_10[index2 - 1]) / row2["10日平均"]
            gradientB = (data_10[index2 - 1] - data_10[index2 - 2]) / data_10[index2 - 1]
            # この傾き係数は変える余地あり
            if gradientA > 0.002 and (gradientA - gradientB) > 0.0010:
                gradientFlagC = True

        # ゴールデンクロスを確認
        gxFlag = True
        gxFlagA = True
        dxFlag = True

        if not math.isnan(row2["25日平均"]) and not math.isnan(row2["75日平均"]):
            if row2["25日平均"] > row2["75日平均"]:
                dxFlag = False
            else:
                gxFlag = False
                gxFlagA = False

            for i in range(3):
                if not math.isnan(data_25[index2 - (i + 1)]) and not math.isnan(data_75[index2 - (i + 1)]):
                    if data_25[index2 - (i + 1)] > data_75[index2 - (i + 1)]:
                        gxFlag = False
                        gxFlagA = False
                    else:
                        dxFlag = False
                    # ゴールデンクロスは上がっているときのみ
                    if row2["75日平均"] < data_75[index2 - (i + 1)]:
                        gxFlag = False
                    if row2["25日平均"] > data_25[index2 - (i + 1)]:
                        dxFlag = False
                else:
                    dxFlag = False
                    gxFlag = False
                    gxFlagA = False

        else:
            dxFlag = False
            gxFlag = False
            gxFlagA = False

        df_one.loc[index2, "ゴールデンクロス"] = gxFlag
        df_one.loc[index2, "ゴールデンクロス_A"] = gxFlagA
        df_one.loc[index2, "デッドクロス"] = dxFlag
        df_one.loc[index2, "25日平均上昇場"] = average_25_Flag
        df_one.loc[index2, "75日平均上昇場"] = average_75_Flag
        df_one.loc[index2, "25日平均急上昇ポイント"] = gradientFlag
        df_one.loc[index2, "25日平均上昇陰りポイント"] = gradientFlagB
        df_one.loc[index2, "10日平均急上昇ポイント"] = gradientFlagC


    for index2, row2 in df_one.iterrows():

        size = len(data_price)
        # 3営業日後騰落率
        rate3 = None
        if (index2 + 3) < size and not math.isnan(row2["終値"]) and not math.isnan(data_price[index2 + 3]):
             rate3 = (data_price[index2 + 3] - row2["終値"]) / row2["終値"]
        # 5営業日後騰落率
        rate5 = None
        if (index2 + 5) < size and not math.isnan(row2["終値"]) and not math.isnan(data_price[index2 + 5]):
             rate5 = (data_price[index2 + 5] - row2["終値"]) / row2["終値"]
        # 10営業日後騰落率
        rate10 = None
        if (index2 + 10) < size and  not math.isnan(row2["終値"]) and not math.isnan(data_price[index2 + 10]):
             rate10 = (data_price[index2 + 10] - row2["終値"]) / row2["終値"]
        # 20営業日後騰落率
        rate20 = None
        if (index2 + 20) < size and not math.isnan(row2["終値"]) and not math.isnan(data_price[index2 + 20]):
            rate20 = (data_price[index2 + 20] - row2["終値"]) / row2["終値"]
        df_one.loc[index2, "3営業日後騰落率"] = rate3
        df_one.loc[index2, "5営業日後騰落率"] = rate5
        df_one.loc[index2, "10営業日後騰落率"] = rate10
        df_one.loc[index2, "20営業日後騰落率"] = rate20

    df_one.to_csv("crossed/" + str(row["コード"]) + ".csv", index=False, encoding='utf_8_sig')
    break



