import random

import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
import re

url_yoho = "https://kabuyoho.jp/reportTarget?bcode=2385"
res = requests.get(url_yoho)
soup = BeautifulSoup(res.text, 'html.parser')
tag_items = soup.select('p:-soup-contains("シグナル") ~ p')
signal = [t.get_text(strip=True) for t in tag_items][0]
print(signal)

tag_items = soup.select('th:-soup-contains("理論株価(PBR基準)") ~ td')
target = [t.get_text(strip=True) for t in tag_items][0]

t = re.findall(r'^(\d+).+円.+', target)[0]
print(t)