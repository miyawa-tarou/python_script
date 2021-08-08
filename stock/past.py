# プラスとなる可能性が高まるシグナルを見つける。何もしない場合と比べて40日後の騰落の数値を見る
# TODO: データを増やして検証する
# TODO: 日付をずらす
import math
import os
import datetime

from concurrent import futures
import pandas as pd
import statistics

df = pd.read_excel("data_j.xls")
df_stock = df[(df["市場・商品区分"] == "市場第二部（内国株）") |
         (df["市場・商品区分"] == "市場第一部（内国株）") |
         (df["市場・商品区分"] == "マザーズ（内国株）") |
         (df["市場・商品区分"] == "JASDAQ(スタンダード・内国株）")][["コード", "銘柄名"]]

# df_stock = df[(df["市場・商品区分"] == "市場第一部（内国株）")]

count_data = {"all": [], "all2": [], "25日平均上昇場": [], "75日平均上昇場": []}
count_data2 = {}

c1 = 0
c2 = 0


def analyze(code):

    file = "master/" + code + ".csv"
    if not os.path.isfile(file):
        return

    stock_prices = []
    # 日付,始値,高値,安値,終値,出来高,終値調整値,5日平均,10日平均,25日平均,75日平均,200日平均
    # ゴールデンクロス（25日）,ゴールデンクロス_A（25日）,デッドクロス（25日）,ゴールデンクロス（終値）,ゴールデンクロス_A（終値）,デッドクロス（終値）
    # 25日平均上昇場,75日平均上昇場,25日平均急上昇ポイント,25日平均上昇陰りポイント,10日平均急上昇ポイント
    # 5営業日後騰落率,10営業日後騰落率,20営業日後騰落率,75営業日後騰落率,乖離率（25日平均）,乖離率（75日平均）
    # 25営業日後騰落率,75営業日後騰落率,75日平均変動率,75営業日後騰落率（10日平均）,40営業日前株価,60営業日前株価,出来高変化率,25日平均変動率,25日平均変動率差,75日平均変動率差
    df_one = pd.read_csv(file, encoding='utf_8_sig')
    for index2, row2 in df_one.iterrows():
        stock_prices.append(row2["終値"])

        # 騰落率データがないと結果を照合できない & 出来高が小さいのは避けるためスキップ
        if not "75営業日後騰落率" in row2 or math.isnan(row2["75営業日後騰落率"]) or not "出来高" in row2 or row2["出来高"] < 100000:
            continue

        # 1年分のみの解析
        # start = datetime.date(2020, 7, 1)
        # if pd.to_datetime(row2["日付"]).date() < start:
        #     continue

        count_data["all"].append(row2["75営業日後騰落率"])

        if row2["乖離率（25日平均）"] > - 100:
            count_data["all2"].append(row2["75営業日後騰落率"])

            for column in ["25日平均上昇場", "75日平均上昇場"]:
                if column in row2 and row2[column]:
                    count_data[column].append(row2["75営業日後騰落率"])

            for column in ["乖離率（25日平均）", "乖離率（75日平均）"]:
                if column in row2 and not math.isnan(row2[column]):
                    for i in range(-1000, 1000, 10):
                        x = i * 0.001
                        if not column + ">" + str(i) in count_data:
                            count_data[column + ">" + str(i)] = []
                            count_data[column + "<" + str(i)] = []
                        if row2[column] > x:
                            count_data[column + ">" + str(i)].append(row2["75営業日後騰落率"])
                        if row2[column] < x:
                            count_data[column + "<" + str(i)].append(row2["75営業日後騰落率"])
            continue
            for column in ["25日平均変動率", "25日平均変動率差"]:
                if column in row2 and not math.isnan(row2[column]):
                    for i in range(-1000, 1000, 10):
                        x = i * 0.00001
                        if not column + ">" + str(i) in count_data:
                            count_data[column + ">" + str(i)] = []
                            count_data[column + "<" + str(i)] = []
                        if row2[column] > x:
                            count_data[column + ">" + str(i)].append(row2["75営業日後騰落率"])
                        if row2[column] < x:
                            count_data[column + "<" + str(i)].append(row2["75営業日後騰落率"])

            # 高いほどよい
            row2["40営業日前株価率"] = None
            if "40営業日前株価" in row2 and not math.isnan(row2["40営業日前株価"]):
                row2["40営業日前株価率"] = row2["40営業日前株価"] / row2["終値"]
            row2["60営業日前株価率"] = None
            if "60営業日前株価" in row2 and not math.isnan(row2["60営業日前株価"]):
                row2["60営業日前株価率"] = row2["60営業日前株価"] / row2["終値"]
            for column in ["40営業日前株価率", "60営業日前株価率"]:
                if column in row2 and row2[column] is not None and not math.isnan(row2[column]):
                    d = 1 - row2[column]
                    for i in range(-1000, 1000, 10):
                        x = i * 0.001
                        if not column + ">" + str(i) in count_data:
                            count_data[column + ">" + str(i)] = []
                            count_data[column + "<" + str(i)] = []
                        if d > x:
                            count_data[column + ">" + str(i)].append(row2["75営業日後騰落率"])
                        if d < x:
                            count_data[column + "<" + str(i)].append(row2["75営業日後騰落率"])

        #
        # if index2 - 60 > 0:
        #     ratio = (row2["終値"] - stock_prices[index2 - 60]) / row2["終値"]
        #     if "25日平均上昇場" in row2 and "75日平均上昇場" in row2 and "25日平均上昇陰りポイント" in row2 and not row2["25日平均上昇場"] and not row2["75日平均上昇場"] and not row2["25日平均上昇陰りポイント"] and row2["出来高"] > 100000 and ratio > - 0.18 and -0.02 > row2["乖離率（75日平均）"] > -0.15:
        #         for key in ["ゴールデンクロス_A（25日）", "ゴールデンクロス_A（終値）", "25日平均急上昇ポイント", "10日平均急上昇ポイント"]:
        #             if not key in count_data:
        #                 count_data[key] = []
        #             if key in row2 and row2[key] == True:
        #                 count_data[key].append(row2["75営業日後騰落率"])
        #         count_data["all2"].append(row2["75営業日後騰落率"])
        #
        #         if not math.isnan(row2["乖離率（25日平均）"]):
        #             for i in range(-20, 10):
        #                 x = i * 0.01
        #                 if not "ほげ1" + str(i) in count_data:
        #                     count_data["ほげ1" + str(i)] = []
        #                     count_data["ほげ2" + str(i)] = []
        #                 if row2["乖離率（75日平均）"] > x:
        #                     count_data["ほげ1" + str(i)].append(row2["75営業日後騰落率"])
        #                 if row2["乖離率（75日平均）"] < x:
        #                     count_data["ほげ2" + str(i)].append(row2["75営業日後騰落率"])

            #2021/1/1～のデータだと乖離率が大きいほうが儲けが出やすい状態
            # この期間は全体が上昇傾向なのは影響してそう
            # 他の期間でも共通か・買ってはいけないのはどのタイミングか（マイナスのものなどを確認する）
            # 陰り始めをOFFって見るとか
            # if not "ほげ" in count_data2:
            #     count_data2["ほげ"] = []
            # if "25日平均上昇場" in row2 and "75日平均上昇場" in row2 and "25日平均上昇陰りポイント" in row2 and not row2["25日平均上昇場"]and not row2["75日平均上昇場"] and not row2["25日平均上昇陰りポイント"]:
            #     count_data2["ほげ"].append(row2["75営業日後騰落率"])
            #
            # if not "ほげ2" in count_data2:
            #     count_data2["ほげ2"] = []
            # if "25日平均上昇場" in row2 and "25日平均上昇陰りポイント" in row2 and not row2["25日平均上昇場"] and not row2["25日平均上昇陰りポイント"]:
            #     count_data2["ほげ2"].append(row2["75営業日後騰落率"])

future_list = []
with futures.ThreadPoolExecutor(max_workers=24) as executor:
    for index, row in df_stock.iterrows():
        future_list.append(executor.submit(analyze, code=str(row["コード"])))
    for future in futures.as_completed(future_list):
        try:
            data = future.result()
        except Exception as exc:
            print('generated an exception: %s' % (exc))


for column in ["all", "all2", "25日平均上昇場", "75日平均上昇場"]:
    print(column)
    print("平均" + str(statistics.mean(count_data[column])))
    print("中央地" + str(statistics.median(count_data[column])))
    print("分散" + str(statistics.stdev(count_data[column])))
    c = 0
    for d in count_data[column]:
        c += 1 if d > 0 else 0
    print("勝率：" + str(c / len(count_data[column])))
    print(len(count_data[column]))

# for column in ["乖離率（25日平均）", "乖離率（75日平均）", "40営業日前株価率", "60営業日前株価率", "25日平均変動率", "25日平均変動率差", "75日平均変動率", "75日平均変動率差"]:
for column in ["乖離率（25日平均）", "乖離率（75日平均）"]:

    print("種類,平均,中央地,勝率,件数")
    for i in range(-1000, 1000, 10):
        disp = []
        co = column + ">" + str(i)
        l = len(count_data[co])
        disp.append(co)
        if l > 0:
            disp.append(str(statistics.mean(count_data[co])))
            disp.append(str(statistics.median(count_data[co])))
            c = 0
            for d in count_data[co]:
                c += 1 if d > 0 else 0
            disp.append(str(c / l))
            disp.append(str(l))
        else:
            disp.append("no data")
        print(",".join(disp))

        disp = []
        co = column + "<" + str(i)
        l = len(count_data[co])
        disp.append(co)
        if l > 0:
            disp.append(str(statistics.mean(count_data[co])))
            disp.append(str(statistics.median(count_data[co])))
            c = 0
            for d in count_data[co]:
                c += 1 if d > 0 else 0
            disp.append(str(c / l))
            disp.append(str(l))
        else:
            disp.append("no data")
        print(",".join(disp))
#
# print(c1)
# print(c2)
# for i in range(-20, 10):
#     key = "ほげ1" + str(i)
#     print(key)
#     if len(count_data[key]) < 2:
#         print("no data")
#         continue
#     print("平均" + str(statistics.mean(count_data[key])))
#     print("中央地" + str(statistics.median(count_data[key])))
#     print("分散" + str(statistics.stdev(count_data[key])))
#     c = 0
#     for d in count_data[key]:
#         c += 1 if d > 0 else 0
#     print("勝率：" + str(c / len(count_data[key])))
#     print(len(count_data[key]))
#
#     key = "ほげ2" + str(i)
#     print(key)
#     if len(count_data[key]) < 2:
#         print("no data")
#         continue
#     print("平均" + str(statistics.mean(count_data[key])))
#     print("中央地" + str(statistics.median(count_data[key])))
#     print("分散" + str(statistics.stdev(count_data[key])))
#     c = 0
#     for d in count_data[key]:
#         c += 1 if d > 0 else 0
#     print("勝率：" + str(c / len(count_data[key])))
#     print(len(count_data[key]))
#
#
#
# for key in ["all", "all2", "ゴールデンクロス_A（25日）","ゴールデンクロス_A（終値）", "25日平均急上昇ポイント", "10日平均急上昇ポイント"]:
# # for key in ["all", "ゴールデンクロス（25日）", "ゴールデンクロス_A（25日）", "ゴールデンクロス（終値）", "ゴールデンクロス_A（終値）", "25日平均上昇場", "75日平均上昇場",
# #                 "25日平均急上昇ポイント", "10日平均急上昇ポイント"]:
#
#     print(key)
#     print("平均" + str(statistics.mean(count_data[key])))
#     print("中央地" + str(statistics.median(count_data[key])))
#     print("分散" + str(statistics.stdev(count_data[key])))
#     c = 0
#     for d in count_data[key]:
#         c += 1 if d > 0 else 0
#     print("勝率：" + str(c / len(count_data[key])))
#     print(len(count_data[key]))

# print("ほげ")
# print("平均" + str(statistics.mean(count_data2["ほげ"])))
# print("中央地" + str(statistics.median(count_data2["ほげ"])))
# print("分散" + str(statistics.stdev(count_data2["ほげ"])))
# c = 0
# for d in count_data2["ほげ"]:
#     c += 1 if d > 0 else 0
# print("勝率：" + str(c / len(count_data2["ほげ"])))
# print("件数：" + str(len(count_data2["ほげ"])))
#
# print("ほげ2")
# print("平均" + str(statistics.mean(count_data2["ほげ2"])))
# print("中央地" + str(statistics.median(count_data2["ほげ2"])))
# print("分散" + str(statistics.stdev(count_data2["ほげ2"])))
# c = 0
# for d in count_data2["ほげ2"]:
#     c += 1 if d > 0 else 0
# print("勝率：" + str(c / len(count_data2["ほげ2"])))
# print(len(count_data2["ほげ2"]))
