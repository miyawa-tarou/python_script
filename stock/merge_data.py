import os

import pandas as pd

df = pd.read_excel("data_j.xls")
df_stock = df[(df["市場・商品区分"] == "市場第二部（内国株）") |
         (df["市場・商品区分"] == "市場第一部（内国株）") |
         (df["市場・商品区分"] == "マザーズ（内国株）") |
         (df["市場・商品区分"] == "JASDAQ(スタンダード・内国株）")][["コード", "銘柄名"]]


for index, row in df_stock.iterrows():
    df_all = pd.DataFrame(index=[], columns=["日付", "始値", "高値", "安値", "終値", "出来高", "終値調整値"])

    df_master = pd.read_csv("master/" + str(row["コード"]) + ".csv")

    for year in reversed(range(1990, 2021)):
        file = "files/" + str(row["コード"]) + "_" + str(year) + ".csv"
        print(file)
        if not os.path.isfile(file):
            print(row["コード"])
            break

        df_one = pd.read_csv(file, header=1, encoding='shift_jis')
        for index2, row2 in df_one.iterrows():
            if row2["終値調整値"] != row2["終値"]:
                coef = row2["終値調整値"] / row2["終値"]

                # 係数が1付近の場合は株式分割とかではなさそうなので、何もしない
                if 0.9 < coef < 1.1:
                    continue

                df_one.loc[index2, "始値"] = row2["始値"] * coef
                df_one.loc[index2, "高値"] = row2["高値"] * coef
                df_one.loc[index2, "安値"] = row2["安値"] * coef
                df_one.loc[index2, "終値"] = row2["終値"] * coef

        df_master = pd.concat([df_master, df_one])

    df_master = df_master.drop_duplicates(subset="日付", keep='last')
    df_master = df_master.sort_values(by="日付")

    df_all.to_csv("merged/" + str(row["コード"]) + ".csv", index=False, encoding='utf_8_sig')
