import datetime
import math
import os
import time

import requests
from bs4 import BeautifulSoup

import pandas as pd

# 全データを再解析する場合はTrueにする（項目増やしたときとか）
re_analyze_flag = False

# 株一覧の取得
df = pd.read_excel("data_j.xls")
df_stock = df[(df["市場・商品区分"] == "市場第二部（内国株）") |
         (df["市場・商品区分"] == "市場第一部（内国株）") |
         (df["市場・商品区分"] == "マザーズ（内国株）") |
         (df["市場・商品区分"] == "JASDAQ(スタンダード・内国株）")][["コード", "銘柄名"]]

pickup_columns = ["コード", "社名", "", "", "", "始値", "高値", "安値", "終値", "目標株価", "診断", "アナリスト"]
df_pickup = pd.DataFrame(index=[], columns=pickup_columns)


def get_average(data, num):
    length = len(end_data)
    d = data[length - num:length]
    return sum(d) / len(d)


for index, row in df_stock.iterrows():
    end_data = []

    # 1社ごとのデータの読み込み
    file = "master/" + str(row["コード"]) + ".csv"
    if not os.path.isfile(file):
        print("file not found:" + row["コード"])
        continue
    df_one = pd.read_csv(file, encoding='utf_8_sig')
    if len(df_one.index) < 1:
        print("no data:" + str(row["コード"]))
        continue

    # 日平均などを出す
    for index2, row2 in df_one.iterrows():
        # 古いのは再解析不要
        start = datetime.date(2020, 7, 1)
        if row2["日付"] < start and not re_analyze_flag:
            continue

        # 既に値があるものは解析不要
        if "200日平均" in row2 and not math.isnan(row2["200日平均"]) and not re_analyze_flag:
            continue

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

        df_one.loc[index2, "5日平均"] = average_5
        df_one.loc[index2, "10日平均"] = average_10
        df_one.loc[index2, "25日平均"] = average_25
        df_one.loc[index2, "75日平均"] = average_75
        df_one.loc[index2, "200日平均"] = average_200

    # 一旦保存する
    df_one.to_csv("averaged/" + str(row["コード"]) + ".csv", index=False, encoding='utf_8_sig')

    # 平均データを呼び出せるように保持する
    data_5 = []
    data_10 = []
    data_25 = []
    data_75 = []
    data_price = []

    # 平均データも含めた解析
    df_one = pd.read_csv("averaged/" + str(row["コード"]) + ".csv", encoding='utf_8_sig')
    for index2, row2 in df_one.iterrows():
        # 古いのは再解析不要
        start = datetime.date(2020, 7, 1)
        if row2["日付"] < start and not re_analyze_flag:
            continue
        # 既に値があるものは解析不要
        if "ゴールデンクロス（25日）" in row2 and not math.isnan(row2["ゴールデンクロス（25日）"]) and not re_analyze_flag:
            continue

        data_10.append(row2["10日平均"])
        data_25.append(row2["25日平均"])
        data_75.append(row2["75日平均"])
        data_price.append(row2["終値"])

        # 平均の上昇場
        average_25_Flag = False
        if not math.isnan(row2["25日平均"]) and not math.isnan(data_25[index2 - 1]):
            average_25_Flag = (row2["25日平均"] - data_25[index2 - 1]) > 0
        average_75_Flag = False
        average_75_ratio = None
        if not math.isnan(row2["75日平均"]) and not math.isnan(data_75[index2 - 1]) and not math.isnan(data_75[index2 - 2]):
            average_75_Flag = (row2["75日平均"] - data_75[index2 - 1]) > 0
            average_75_ratio = ((row2["75日平均"] - data_75[index2 - 1]) - (data_75[index2 - 1] - data_75[index2 - 2])) / row2["75日平均"]

        # 傾きが上がった瞬間を確認
        gradientFlag = False
        gradientFlagB = False
        if not math.isnan(row2["25日平均"]) and not math.isnan(data_25[index2 - 1]) and not math.isnan(data_25[index2 - 2]):
            gradientA = (row2["25日平均"] - data_25[index2 - 1]) / row2["25日平均"]
            gradientB = (data_25[index2 - 1] - data_25[index2 - 2]) / data_25[index2 - 1]
            # この傾き係数は変える余地あり
            if gradientA > 0.001 > gradientB and (gradientA - gradientB) > 0.0005:
                gradientFlag = True
            if gradientA < gradientB:
                gradientFlagB = True
        gradientFlagC = False
        if not math.isnan(row2["10日平均"]) and not math.isnan(data_10[index2 - 1]) and not math.isnan(data_10[index2 - 2]):
            gradientA = (row2["10日平均"] - data_10[index2 - 1]) / row2["10日平均"]
            gradientB = (data_10[index2 - 1] - data_10[index2 - 2]) / data_10[index2 - 1]
            # この傾き係数は変える余地あり
            if gradientA > 0.002 and (gradientA - gradientB) > 0.0010 and gradientB < 0.001:
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

        # ゴールデンクロスを確認2
        gxFlag2 = True
        gxFlag2A = True
        dxFlag2 = True

        if not math.isnan(row2["25日平均"]):
            if row2["終値"] > row2["25日平均"]:
                dxFlag2 = False
            else:
                gxFlag2 = False
                gxFlag2A = False

            for i in range(3):
                if not math.isnan(data_price[index2 - (i + 1)]) and not math.isnan(data_25[index2 - (i + 1)]):
                    if data_price[index2 - (i + 1)] > data_25[index2 - (i + 1)]:
                        gxFlag2 = False
                        gxFlag2A = False
                    else:
                        dxFlag2 = False
                    # ゴールデンクロスは上がっているときのみ
                    if row2["25日平均"] < data_25[index2 - (i + 1)]:
                        gxFlag2 = False
                    if row2["25日平均"] > data_25[index2 - (i + 1)]:
                        dxFlag2 = False
                else:
                    dxFlag2 = False
                    gxFlag2 = False
                    gxFlag2A = False

        else:
            dxFlag2 = False
            gxFlag2 = False
            gxFlag2A = False

        divergence_rate_75 = (row2["終値"] - row2["75日平均"]) / row2["終値"]
        divergence_rate_25 = (row2["終値"] - row2["25日平均"]) / row2["終値"]

        df_one.loc[index2, "乖離率（25日平均）"] = divergence_rate_25
        df_one.loc[index2, "乖離率（75日平均）"] = divergence_rate_75

        df_one.loc[index2, "ゴールデンクロス（25日）"] = gxFlag
        df_one.loc[index2, "ゴールデンクロス_A（25日）"] = gxFlagA
        df_one.loc[index2, "デッドクロス（25日）"] = dxFlag
        df_one.loc[index2, "ゴールデンクロス（終値）"] = gxFlag2
        df_one.loc[index2, "ゴールデンクロス_A（終値）"] = gxFlag2A
        df_one.loc[index2, "デッドクロス（終値）"] = dxFlag2
        df_one.loc[index2, "25日平均上昇場"] = average_25_Flag
        df_one.loc[index2, "75日平均上昇場"] = average_75_Flag
        df_one.loc[index2, "75日平均変動率"] = average_75_ratio
        df_one.loc[index2, "25日平均急上昇ポイント"] = gradientFlag
        df_one.loc[index2, "25日平均上昇陰りポイント"] = gradientFlagB
        df_one.loc[index2, "10日平均急上昇ポイント"] = gradientFlagC

    for index2, row2 in df_one.iterrows():
        size = len(data_price)
        # 5営業日後騰落率
        rate5 = None
        if (index2 + 5) < size and not math.isnan(row2["終値"]) and not math.isnan(data_price[index2 + 5]):
             rate5 = (data_price[index2 + 5] - row2["終値"]) / row2["終値"]
        # 10営業日後騰落率
        rate10 = None
        if (index2 + 10) < size and  not math.isnan(row2["終値"]) and not math.isnan(data_price[index2 + 10]):
             rate10 = (data_price[index2 + 10] - row2["終値"]) / row2["終値"]
        # 25営業日後騰落率
        rate25 = None
        if (index2 + 25) < size and not math.isnan(row2["終値"]) and not math.isnan(data_price[index2 + 25]):
            rate25 = (data_price[index2 + 25] - row2["終値"]) / row2["終値"]
        # 75営業日後騰落率
        rate75 = None
        if (index2 + 75) < size and not math.isnan(row2["終値"]) and not math.isnan(data_price[index2 + 75]):
            rate75 = (data_price[index2 + 75] - row2["終値"]) / row2["終値"]
        df_one.loc[index2, "5営業日後騰落率"] = rate5
        df_one.loc[index2, "10営業日後騰落率"] = rate10
        df_one.loc[index2, "25営業日後騰落率"] = rate25
        df_one.loc[index2, "75営業日後騰落率"] = rate75

        # 10日平均での75営業日後騰落率（日々の誤差を見ない））
        rate75_2 = None
        if (index2 + 75) < size and not math.isnan(data_10[index2]) and not math.isnan(data_10[index2 + 75]):
            rate75_2 = (data_10[index2 + 75] - data_10[index2]) / data_10[index2]
        df_one.loc[index2, "75営業日後騰落率（10日平均）"] = rate75_2

    df_one.to_csv("master/" + str(row["コード"]) + ".csv", index=False, encoding='utf_8_sig')

    # 直近データを利用してのスクリーニング
    row2 = df_one.tail(1).iloc[0]
    if row2["75日平均上昇場"] and row2["75日平均変動率"] > 0 and row2["25日平均上昇場"]:
        if row2["ゴールデンクロス（25日）"] or row2["25日平均急上昇ポイント"] or row2["乖離率（75日平均）"] > 0.02:
            time.sleep(1)
            minkabu = "https://minkabu.jp/stock/" + str(row["コード"])
            res = requests.get(minkabu)
            soup = BeautifulSoup(res.text, 'html.parser')
            tag_items = soup.select('h2:-soup-contains("目標株価") ~ div')
            target = [t.get_text(strip=True) for t in tag_items][0][:-1].replace(",", "")
            target = int(target) if target.isdigit() or target != "---" else 0  # ない場合は計算上0とする

            if target / row2["終値"] < 1.2:
                continue

            tag_items = soup.select('p:-soup-contains("株価診断") ~ span')
            diagnosis = [t.get_text(strip=True) for t in tag_items][0]
            if diagnosis == "割高":
                continue
            tag_items = soup.select('p:-soup-contains("アナリスト") ~ span')
            analyst = [t.get_text(strip=True) for t in tag_items][0]

            print("https://finance.yahoo.co.jp/quote/" + str(row["コード"]) + ".T")
            print(minkabu)

            print("現在株価：" + str(row2["終値"]))
            print("目標株価：" + str(target))
            print("診断：" + diagnosis)
            print("アナリスト：" + analyst)
            print("75日平均傾き変動率：" + str(row2["75日平均変動率"] * 100))

            if row2["ゴールデンクロス（25日）"]:
                print("ゴールデンクロス（25日）")
            if row2["25日平均急上昇ポイント"]:
                print("25日平均急上昇ポイント")
            if row2["乖離率（75日平均）"] > 0.02:
                print("高乖離率" + str(row2["乖離率（75日平均）"]))

            s = pd.Series(
                [str(row2["コード"]), "", "", "" ,row2["始値"], row2["高値"], row2["安値"], row2["終値"], str(target), diagnosis, analyst],
                index=pickup_columns)
            df_pickup = df_pickup.append(s, ignore_index=True)

now = datetime.datetime.now()
df_pickup.to_csv("analyzed/daily_" + now.strftime("Y-m-d") + ".csv", index=False, encoding='utf_8_sig')
