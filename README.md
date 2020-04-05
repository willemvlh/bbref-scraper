# bbref-scraper
Easy NBA data scraping for Python using data provided by Basketball Reference.

#Usage

##Retrieving a player
```
>>> from bballer import player
>>> pl = player.get_by_name("Carmelo Anthony") 
Player(Carmelo Anthony, 1984-05-29) # Returns first match

>>> pl_list = player.search("Bogdanovic")
[('Bojan Bogdanović (2015-2020)', 'https://www.basketball-reference.com/players/b/bogdabo02.html'), ('Bogdan Bogdanović (2018-2020)', 'https://www.basketball-reference.com/players/b/bogdabo01.html')]
>>> player.get_by_url(pl_list[0][1])
Player(Bojan Bogdanović, 1989-04-18)
```

##Querying a player
```
Player(Carmelo Anthony, 1984-05-29)
>>> pl.date_of_birth
datetime.date(1984, 5, 29)
>>> rookie_season = pl.seasons[0]
>>> rookie_season.minutes_played
2995
>>> most_points_game = max(rookie_season.game_logs, key=lambda g: g.points)
GameLog(points=41, rebounds=5, assists=0)
```

##Querying a team
```
>>> from bballer import team
>>> warriors = team.get_by_name("Golden State Warriors")
>>> warriors.championships
6
>>> season = warriors.season(2015)
>>> for pl in season.roster:
>>>    print(pl["name"])
Matt Barnes
Ian Clark
Stephen Curry
Kevin Durant
Draymond Green
Andre Iguodala
Damian Jones
Shaun Livingston
Kevon Looney
James Michael McAdoo
Patrick McCaw
JaVale McGee
Zaza Pachulia
Klay Thompson
Anderson Varejão
Briante Weber
David West



```

