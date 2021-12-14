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

with open('D:/Projects/hltvdownload/lanurls.txt') as f:
    lan_urls = f.readlines()

with open('D:/Projects/hltvdownload/onlineurls.txt') as f:
    online_urls = f.readlines()

page_count_lan = len(lan_urls)
page_count_online = len(online_urls)
total_page_count = page_count_lan + page_count_online
progress_file = open("D:/Projects/hltvdownload/matches/offset.txt", "r+")
current_page = int(progress_file.read())

while current_page < total_page_count:
    if current_page >= page_count_lan:
        local_page = (current_page-page_count_lan)
        match_type = 'online'
        url = online_urls[local_page]
    else:
        local_page = current_page
        match_type = 'lan'
        url = lan_urls[local_page]
    try:
        req = urllib.request.Request(url, None, hdr)
        response = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        print(e.reason + ' ' + str(e.code))
        progress_file.close()
        exit()
    webContent = response.read()
    f = open(f'D:/Projects/hltvdownload/matches/{match_type}/{local_page}.html', 'wb')
    f.write(webContent)
    f.close()
    print(f'{current_page} / {total_page_count} ({round((current_page / total_page_count) * 100, 3)}%)')
    current_page += 1
    progress_file.seek(0)
    progress_file.write(str(current_page))
    progress_file.truncate()
    time.sleep(1.333+random.random())

progress_file.close()
