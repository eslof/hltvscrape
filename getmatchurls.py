import os

from bs4 import BeautifulSoup

append_filter = '?startDate=2020-01-01&amp;endDate=2020-6-30&amp;matchType=Lan&amp;rankingFilter=Top50'
filter_len = len(append_filter)
base_url = 'https://www.hltv.org'

url_file = open('D:\Projects\hltvdownload\lanurls.txt', 'a')

for history_page in os.listdir('D:\Projects\hltvdownload\history\lan'):
    with open(rf'D:\Projects\hltvdownload\history\lan\{history_page}', mode="r", encoding="utf-8") as f:
        page = f.read()
    parsed_page = BeautifulSoup(page, "html.parser")
    table = parsed_page.find("table", {"class": ["stats-table matches-table no-sort"], })
    urls = table.find_all('a', href=True)
    for url in urls:
        if '/stats/matches/mapstatsid/' in url['href']:
            url_file.write(base_url+url['href'].split('?')[0]+'\n')
url_file.close()

url_file = open('D:\Projects\hltvdownload\onlineurls.txt', 'a')

for history_page in os.listdir('D:\Projects\hltvdownload\history\online'):
    with open(rf'D:\Projects\hltvdownload\history\online\{history_page}', mode="r", encoding="utf-8") as f:
        page = f.read()
    parsed_page = BeautifulSoup(page, "html.parser")
    table = parsed_page.find("table", {"class": ["stats-table matches-table no-sort"], })
    urls = table.find_all('a', href=True)
    for url in urls:
        if '/stats/matches/mapstatsid/' in url['href']:
            url_file.write(base_url+url['href'].split('?')[0]+'\n')

