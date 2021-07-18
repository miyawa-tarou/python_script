# プラスとなる可能性が高まるシグナルを見つける。何もしない場合と比べて40日後の騰落の数値を見る
# TODO: データを増やして検証する
# TODO: 日付をずらす
import math
import os

import pandas as pd
import statistics

df = pd.read_excel("data_j.xls")
df_stock = df[(df["市場・商品区分"] == "市場第二部（内国株）") |
         (df["市場・商品区分"] == "市場第一部（内国株）") |
         (df["市場・商品区分"] == "マザーズ（内国株）") |
         (df["市場・商品区分"] == "JASDAQ(スタンダード・内国株）")][["コード", "銘柄名"]]

count_data = {"all": []}
count_data2 = {}

for index, row in df_stock.iterrows():
    code = str(row["コード"])

    if row["コード"] > 2338:
        break

    file = "master/" + code + ".csv"
    if not os.path.isfile(file):
        continue

    df_one = pd.read_csv(file, encoding='utf_8_sig')
    for index2, row2 in df_one.iterrows():

        # 騰落率データがないと結果を照合できない
        if not "40営業日後騰落率" in row2 or math.isnan(row2["40営業日後騰落率"]):
            continue

        for key in ["ゴールデンクロス（25日）", "ゴールデンクロス_A（25日）", "ゴールデンクロス（終値）", "ゴールデンクロス_A（終値）", "25日平均上昇場", "75日平均上昇場", "25日平均急上昇ポイント", "10日平均急上昇ポイント"]:
            if not key in count_data:
                count_data[key] = []
            if key in row2 and row2[key] == True:
                count_data[key].append(row2["40営業日後騰落率"])
        count_data["all"].append(row2["40営業日後騰落率"])

        for key in ["乖離率（25日平均）", "乖離率（75日平均）"]:
            if not key in count_data:
                count_data[key] = []
            if key in row2 and row2[key] < 0.2:
                count_data[key].append(row2["40営業日後騰落率"])

        if "75日平均上昇場" in row2 and row2["75日平均上昇場"]:
            for key in ["ゴールデンクロス（25日）", "ゴールデンクロス_A（25日）", "ゴールデンクロス（終値）", "ゴールデンクロス_A（終値）", "25日平均上昇場", "75日平均上昇場", "25日平均急上昇ポイント", "10日平均急上昇ポイント"]:
                if not key in count_data2:
                    count_data2[key] = []
                if key in row2 and row2[key] == True:
                    count_data2[key].append(row2["40営業日後騰落率"])
            for key in ["乖離率（25日平均）", "乖離率（75日平均）"]:
                if not key in count_data2:
                    count_data2[key] = []
                if key in row2 and row2[key] < 0.01:
                    count_data2[key].append(row2["40営業日後騰落率"])

            #2021/1/1～のデータだと乖離率が大きいほうが儲けが出やすい状態
            # この期間は全体が上昇傾向なのは影響してそう
            # 他の期間でも共通か・買ってはいけないのはどのタイミングか（マイナスのものなどを確認する）
            # 陰り始めをOFFって見るとか
            if not "ほげ" in count_data2:
                count_data2["ほげ"] = []
            if "ゴールデンクロス（25日）" in row2 and "乖離率（75日平均）" in row2 and row2["ゴールデンクロス（25日）"] and row2["乖離率（75日平均）"] > 0.1:
                count_data2["ほげ"].append(row2["40営業日後騰落率"])

            if not "ほげ2" in count_data2:
                count_data2["ほげ2"] = []
            if "ゴールデンクロス（25日）" in row2 and "乖離率（75日平均）" in row2 and row2["ゴールデンクロス（25日）"] and row2["乖離率（75日平均）"] > 0.15:
                count_data2["ほげ2"].append(row2["40営業日後騰落率"])

for key in ["all", "ゴールデンクロス（25日）", "ゴールデンクロス_A（25日）", "ゴールデンクロス（終値）", "ゴールデンクロス_A（終値）", "25日平均上昇場", "75日平均上昇場", "25日平均急上昇ポイント", "10日平均急上昇ポイント", "乖離率（25日平均）", "乖離率（75日平均）"]:
# for key in ["all", "ゴールデンクロス（25日）", "ゴールデンクロス_A（25日）", "ゴールデンクロス（終値）", "ゴールデンクロス_A（終値）", "25日平均上昇場", "75日平均上昇場",
#                 "25日平均急上昇ポイント", "10日平均急上昇ポイント"]:

    print(key)
    print("平均" + str(statistics.mean(count_data[key])))
    print("中央地" + str(statistics.median(count_data[key])))
    print("分散" + str(statistics.stdev(count_data[key])))
    c = 0
    for d in count_data[key]:
        c += 1 if d > 0 else 0
    print("勝率：" + str(c / len(count_data[key])))
    print(len(count_data[key]))

    if not key == "all":
        print("平均" + str(statistics.mean(count_data2[key])))
        print("中央地" + str(statistics.median(count_data2[key])))
        print("分散" + str(statistics.stdev(count_data2[key])))
        c = 0
        for d in count_data2[key]:
            c += 1 if d > 0 else 0
        print("勝率：" + str(c / len(count_data2[key])))
        print(len(count_data2[key]))

print("ほげ")
print("平均" + str(statistics.mean(count_data2["ほげ"])))
print("中央地" + str(statistics.median(count_data2["ほげ"])))
print("分散" + str(statistics.stdev(count_data2["ほげ"])))
c = 0
for d in count_data2["ほげ"]:
    c += 1 if d > 0 else 0
print("勝率：" + str(c / len(count_data2["ほげ"])))
print("件数：" + str(len(count_data2["ほげ"])))

print("ほげ2")
print("平均" + str(statistics.mean(count_data2["ほげ2"])))
print("中央地" + str(statistics.median(count_data2["ほげ2"])))
print("分散" + str(statistics.stdev(count_data2["ほげ2"])))
c = 0
for d in count_data2["ほげ2"]:
    c += 1 if d > 0 else 0
print("勝率：" + str(c / len(count_data2["ほげ2"])))
print(len(count_data2["ほげ2"]))
