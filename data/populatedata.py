import sqlite3
from datetime import datetime
import os
from bs4 import BeautifulSoup

conn = sqlite3.connect(
    f"file:///D:/Projects/hltvdownload/data/matchdb.sqlite?mode=rw",
    uri=True,
)
cur = conn.cursor()


class MatchRow:
    pass


def run(mstr):
    for match_page in os.listdir(f'D:\matchdata\{mstr}'):
        # region open page
        with open(rf'D:\matchdata\{mstr}\{match_page}', mode="r", encoding="utf-8") as f:
            page = f.read()
        parsed_page = BeautifulSoup(page, "html.parser")
        # endregion
        print(match_page)
        row = MatchRow()

        # region Parsing "Best of N" and map series for current map_number in series
        row.is_lan = 0 if mstr == 'online' else 1
        best_of = parsed_page.find("div", {"class": ["stats-match-maps"], })
        map_series = []
        if not best_of:
            row.best_of = 1
            row.map_number = 1
        else:
            map_columns = best_of.findAll("a", href=True)
            if not map_columns:
                row.best_of = 1
                row.map_number = 1
            else:
                for m in map_columns:
                    map_series.append(
                        m.find("div", {"class": ["stats-match-map-result-mapname dynamic-map-name-full"], }).contents[0])
                row.best_of = 3 if map_series.pop(0) == "Best of 3" else 5

        # endregion
        match_info = parsed_page.find("div", {"class": ["match-info-box-con"], })

        row.map_name = match_info.find("div", {"class": ["match-info-box"], }).findAll(text=True, recursive=False)[1].strip()
        if len(map_series) > 0:
            row.map_number = float(map_series.index(row.map_name)) / 5

        # region Date/day delta
        date = match_info.find("span", {"data-time-format": ["yyyy-MM-dd HH:mm"], })
        parsed_date = ''.join(list(date.contents[0])[:10])
        f_date = datetime(2020, 1, 1, 0, 0, 0)
        l_date = datetime.strptime(parsed_date, '%Y-%m-%d')
        delta = l_date - f_date
        row.day_delta = delta.days
        row.day_delta = (row.day_delta - 3) / (286 - 3)
        if row.day_delta < 0:
            continue
        # endregion

        #region Match info box
        team_left = str(match_info.find("div", {"class": ["team-left"], }).find("a", href=True).findAll(text=True, recursive=False)[0])
        team_right = str(match_info.find("div", {"class": ["team-right"], }).find("a", href=True).findAll(text=True, recursive=False)[0])

        match_breakdowns = match_info.findAll("div", {"class": ["match-info-row"], })
        score_data = match_breakdowns[0].find("div", {"class": ["right"], }).findAll("span")
        team_ratings = match_breakdowns[1].find("div", {"class": ["right"], }).findAll(text=True, recursive=False)[0].split(' : ')
        team_firstbloods = match_breakdowns[2].find("div", {"class": ["right"], }).findAll(text=True, recursive=False)[0].split(' : ')
        team_clutches = match_breakdowns[3].find("div", {"class": ["right"], }).findAll(text=True, recursive=False)[0].split(' : ')
        round_breakdowns = parsed_page.findAll("div", {"class": ["round-history-team-row"], })
        team_left_round = round_breakdowns[0].findAll("div", {"class": ["round-history-half"], })
        team_left_1h_raw = team_left_round[0].findAll("img")
        team_left_2h_raw = team_left_round[1].findAll("img")
        team_right_round = round_breakdowns[1].findAll("div", {"class": ["round-history-half"], })
        team_right_1h_raw = team_right_round[0].findAll("img")
        team_right_2h_raw = team_right_round[1].findAll("img")
        team_left_1h_img = []
        team_left_2h_img = []
        team_right_1h_img = []
        team_right_2h_img = []

        for img in team_left_1h_raw:
            team_left_1h_img.append(img["src"].split('/')[-1].split('.')[0])
        for img in team_left_2h_raw:
            team_left_2h_img.append(img["src"].split('/')[-1].split('.')[0])
        for img in team_right_1h_raw:
            team_right_1h_img.append(img["src"].split('/')[-1].split('.')[0])
        for img in team_right_2h_raw:
            team_right_2h_img.append(img["src"].split('/')[-1].split('.')[0])

        player_stats_table = parsed_page.findAll("table", {"class": ["stats-table"], })

        left_player_table = player_stats_table[0].find("tbody").findAll("tr")
        right_player_table = player_stats_table[1].find("tbody").findAll("tr")
        left_player_stats = {}
        right_player_stats = {}

        def buildPlayerStats(pt, t):
            for i in range(5):
                name = pt[i].find("td", {"class": ["st-player"], }).find("a", href=True).find(text=True, recursive=False)
                kills = float(pt[i].find("td", {"class": ["st-kills"], }).find(text=True, recursive=False))
                kills = kills / 64
                assists = float(pt[i].find("td", {"class": ["st-assists"], }).find(text=True, recursive=False))
                assists = assists / 20
                deaths = float(pt[i].find("td", {"class": ["st-deaths"], }).find(text=True, recursive=False))
                deaths = (deaths - 2) / (46 - 2)
                kast = float(pt[i].find("td", {"class": ["st-kdratio"], }).find(text=True, recursive=False).strip('%'))
                kast = (kast - 16.7) / (100 - 16.7)
                adr = pt[i].find("td", {"class": ["st-adr"], }).find(text=True, recursive=False)
                if adr == '-':
                    adr = 0.0
                adr = float(adr)
                adr = adr / 172.7
                rating = float(pt[i].find("td", {"class": ["st-rating"], }).find(text=True, recursive=False))
                rating = (rating - 0.09) / (2.92 - 0.09)
                t[name] = [
                    kills,
                    assists,
                    deaths,
                    kast,
                    adr,
                    rating
                ]

        buildPlayerStats(left_player_table, left_player_stats)
        buildPlayerStats(right_player_table, right_player_stats)

        class Pattern:
            none = "end"
            ct_win = "ct_win"
            t_win = "t_win"
            ct_lose = "ct_lose"
            t_lose = "t_lose"
            bomb_win = "bomb_win"
            bomb_lose = "bomb_lose"
            defuse_win = "defuse_win"
            defuse_lose = "defuse_lose"
            time_win = "time_win"
            time_lose = "time_lose"

        # 'ct_win', 't_win', 'bomb_defused', 'bomb_exploded', 'stopwatch', 'emptyHistory'
        def buildHalf(t1_img, t2_img, t1):
            for i in range(15):
                name = t1_img[i]
                if name == 'ct_win':
                    t1.append(Pattern.ct_win)
                elif name == 't_win':
                    t1.append(Pattern.t_win)
                elif name == 'bomb_defused':
                    t1.append(Pattern.defuse_win)
                elif name == 'bomb_exploded':
                    t1.append(Pattern.bomb_win)
                elif name == 'stopwatch':
                    t1.append(Pattern.time_win)
                elif name == 'emptyHistory':
                    enemy = t2_img[i]
                    if enemy == 'ct_win':
                        t1.append(Pattern.t_lose)
                    elif enemy == 't_win':
                        t1.append(Pattern.ct_lose)
                    elif enemy == 'bomb_defused':
                        t1.append(Pattern.defuse_lose)
                    elif enemy == 'bomb_exploded':
                        t1.append(Pattern.bomb_lose)
                    elif enemy == 'stopwatch':
                        t1.append(Pattern.time_lose)
                    elif enemy == 'emptyHistory':
                        t1.append(Pattern.none)

        team_left_1h = []
        team_left_2h = []
        team_right_1h = []
        team_right_2h = []

        buildHalf(team_left_1h_img, team_right_1h_img, team_left_1h)
        buildHalf(team_left_2h_img, team_right_2h_img, team_left_2h)
        buildHalf(team_right_1h_img, team_left_1h_img, team_right_1h)
        buildHalf(team_right_2h_img, team_left_2h_img, team_right_2h)

        def addPattern(row, pattern, side, h):
            for i in range(15):
                setattr(row, f"{side}_{h}h_r{i+1}", pattern[i])

        def addPlayers(row, names, stats, side):
            i = 1
            for p in names:
                setattr(row, f"{side}_p{i}_kills", stats[p][0])
                setattr(row, f"{side}_p{i}_assists", stats[p][1])
                setattr(row, f"{side}_p{i}_deaths", stats[p][2])
                setattr(row, f"{side}_p{i}_kast", stats[p][3])
                setattr(row, f"{side}_p{i}_adr", stats[p][4])
                setattr(row, f"{side}_p{i}_rating", stats[p][5])
                i += 1

        if score_data[2]["class"][0] == "ct-color":
            row.team_ct = str(team_left)
            ct_score_1h = float(score_data[2].contents[0]) / 15
            ct_score_2h = float(score_data[4].contents[0]) / 15
            #row.ct_rating = (float(team_ratings[0]) - 0.39) / (1.74 - 0.39)
            #row.ct_firstblood = (float(team_firstbloods[0]) - 1) / (31 - 1)
            #row.ct_clutches = float(team_clutches[0]) / 15
            #addPattern(row, team_left_1h, "ct", 1)
            #addPattern(row, team_left_2h, "ct", 2)
            #addPlayers(row, sorted(left_player_stats), left_player_stats, "ct")

            row.team_t = str(team_right)
            t_score_1h = float(score_data[3].contents[0]) / 15
            t_score_2h = float(score_data[5].contents[0]) / 15
            #row.t_rating = (float(team_ratings[1]) - 0.39) / (1.74 - 0.39)
            #row.t_firstblood = (float(team_firstbloods[1]) - 1) / (31 - 1)
            #row.t_clutches = float(team_clutches[1]) / 15
            #addPattern(row, team_right_1h, "t", 1)
            #addPattern(row, team_right_2h, "t", 2)
            #addPlayers(row, sorted(right_player_stats), right_player_stats, "t")
        else:
            row.team_ct = str(team_right)
            ct_score_1h = float(score_data[3].contents[0]) / 15
            ct_score_2h = float(score_data[5].contents[0]) / 15
            #row.ct_rating = (float(team_ratings[1]) - 0.39) / (1.74 - 0.39)
            #row.ct_firstblood = (float(team_firstbloods[1]) - 1) / (31 - 1)
            #row.ct_clutches = float(team_clutches[1]) / 15
            #addPattern(row, team_right_1h, "ct", 1)
            #addPattern(row, team_right_2h, "ct", 2)
            #addPlayers(row, sorted(right_player_stats), right_player_stats, "ct")

            row.team_t = str(team_left)
            t_score_1h = float(score_data[2].contents[0]) / 15
            t_score_2h = float(score_data[4].contents[0]) / 15
            #row.t_rating = (float(team_ratings[0]) - 0.39) / (1.74 - 0.39)
            #row.t_firstblood = (float(team_firstbloods[0]) - 1) / (31 - 1)
            #row.t_clutches = float(team_clutches[0]) / 15
            #addPattern(row, team_left_1h, "t", 1)
            #addPattern(row, team_left_2h, "t", 2)
            #addPlayers(row, sorted(left_player_stats), left_player_stats, "t")

        #for k in row.__dict__.keys():
        #    v = type(row.__dict__[k])
        #    if v is str:
        #        ctype = "TEXT"
        #    elif v is float:
        #        ctype = "REAL"
        #    elif v is int:
        #        ctype = "INTEGER"
        #    print(f'"{k}"	{ctype} NOT NULL,')

        if ct_score_1h + ct_score_2h == 16:
            row.result = 1
        elif t_score_1h + t_score_2h == 16:
            row.result = 0
        else:
            row.result = 0.5
        query = "INSERT INTO matches " + str(tuple(row.__dict__.keys())) + " VALUES" + str(tuple(row.__dict__.values()))
        cur.execute(query)
        conn.commit()


run('lan')
run('online')

cur.close()
conn.close()
