import math
import urllib.request, urllib.error, urllib.parse
import time
import random
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

base_url = 'https://www.hltv.org/stats/matches?startDate=2020-01-01&endDate=2020-6-30&rankingFilter=Top50'
lan_url = base_url+'&matchType=Lan&offset='
online_url = base_url+'&matchType=Online&offset='
lan_entries = 8438
online_entries = 16897
entries_per_page = 50
page_count_lan = math.ceil(lan_entries / entries_per_page)
page_count_online = math.ceil(online_entries / entries_per_page)
total_page_count = page_count_lan + page_count_online
progress_file = open("D:/Projects/hltvdownload/history/offset.txt", "r+")
current_page = int(progress_file.read())

while current_page < total_page_count:
    if current_page >= page_count_lan:
        local_page = (current_page-page_count_lan)
        match_type = 'online'
        url = online_url
    else:
        local_page = current_page
        match_type = 'lan'
        url = lan_url
    offset = local_page * 50
    try:
        req = urllib.request.Request(url+str(offset), None, hdr)
        response = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        print(e.reason + ' ' + str(e.code))
        progress_file.close()
        exit()
    webContent = response.read()
    f = open(f'D:/Projects/hltvdownload/history/{match_type}/{local_page}.html', 'wb')
    f.write(webContent)
    f.close()
    print(f'{current_page} / {total_page_count} ({round((current_page / total_page_count) * 100, 3)}%)')
    current_page += 1
    progress_file.seek(0)
    progress_file.write(str(current_page))
    progress_file.truncate()
    time.sleep(1.333+random.random())

progress_file.close()
