import requests
from bs4 import BeautifulSoup
import re

res = requests.get('https://www.m3net.jp/attendance/circle2021sR.php')

# レスポンスの HTML から BeautifulSoup オブジェクトを作る
soup = BeautifulSoup(res.text, 'html.parser')

# title タグの文字列を取得する
tables = soup.select(".tblCircleList")

event_id = 8

values1 = []
for data in tables:
    tr = data.find_all("tr")
    for row in tr:
        space = row.find(class_="left").get_text(strip=True)
        link = row.find("li").find("a")

        if (link):
            name = re.sub(r'\'', '\\\'', link.get_text(strip=True))
            url = link['href']
        else:
            link = row.find("li")
            name = re.sub(r'\'', '\\\'', link.get_text(strip=True))
            url = ""


        # 現行仕様はWEBのスペースの情報も併記されている
        single_space = re.search(r'^[A-Za-zあ-んア-ン]-[0-9]+', space).group()
        # print(single_space)
        # print(name)
        # print(url)

        sp = single_space.split("-")
        space_head = "'" + sp[0] + "'" if single_space else "null"
        space_body = "'" + sp[1] + "'" if single_space else "null"
        text = "(null, " + str(event_id) + ", " + space_head + ", " + space_body + ", '" + name + "', '" + url + "')"
        values1.append(text)

print("INSERT INTO `dojin_event_space`(id, event_id, space_head, space_number, circle_name,url) VALUES")
print(','.join(values1) + ";")




res = requests.get('https://www.m3net.jp/attendance/circle2021sW.php')

# レスポンスの HTML から BeautifulSoup オブジェクトを作る
soup = BeautifulSoup(res.text, 'html.parser')

# title タグの文字列を取得する
tables = soup.select(".tblCircleList")

event_id = 9

values1 = []
for data in tables:
    tr = data.find_all("tr")
    for row in tr:
        space = row.find(class_="left").get_text(strip=True)
        link = row.find("li").find("a")

        if (link):
            name = re.sub(r'\'', '\\\'', link.get_text(strip=True))
            url = link['href']
        else:
            link = row.find("li")
            name = re.sub(r'\'', '\\\'', link.get_text(strip=True))
            url = ""

        # 現行仕様はWEBのスペースの情報も併記されている
        single_space = re.search(r'[一-鿐]-[0-9]+$', space).group()
        # print(single_space)
        # print(name)
        # print(url)

        sp = single_space.split("-")
        space_head = "'" + sp[0] + "'" if single_space else "null"
        space_body = "'" + sp[1] + "'" if single_space else "null"
        text = "(null, " + str(event_id) + ", " + space_head + ", " + space_body + ", '" + name + "', '" + url + "')"
        values1.append(text)
print("INSERT INTO `dojin_event_space`(id, event_id, space_head, space_number, circle_name,url) VALUES")
print(','.join(values1) + ";")



