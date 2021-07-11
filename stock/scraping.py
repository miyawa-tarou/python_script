import random

import pandas as pd
import requests
import time
from bs4 import BeautifulSoup

df = pd.read_excel("data_j.xls")
df_stock = df[(df["市場・商品区分"] == "市場第二部（内国株）") |
         (df["市場・商品区分"] == "市場第一部（内国株）") |
         (df["市場・商品区分"] == "マザーズ（内国株）") |
         (df["市場・商品区分"] == "JASDAQ(スタンダード・内国株）")][["コード", "銘柄名"]]

ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
headers = {'User-Agent': ua}

urls = [
    "https://quote.nomura.co.jp/nomura/cgi-bin/parser.pl?TEMPLATE=nomura_tp_kabu_01&QCODE={code}&MKTN=T",
    # "https://trade.smbcnikko.co.jp/InvestmentInformation/7152B0129761/syohin/prelogin/meigkensk?meigNm={code}&meigCd={code}}&kabuka=2&sijyo=1",
    "https://minkabu.jp/stock/{code}",
    "https://minkabu.jp/stock/{code}",
    "https://kabutan.jp/stock/?code={code}",
    "https://finance.yahoo.co.jp/quote/{code}.T"
]

for index, row in df_stock.iterrows():

    url = random.choice(urls)
    url = url.format(code=row["コード"])

    print(url)



