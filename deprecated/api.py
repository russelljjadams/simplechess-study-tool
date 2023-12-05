# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 18:46:51 2023

@author: rjadams
"""

import json
import chessdotcom as c

c.Client.request_config["headers"]["User-Agent"] = (
   "My Python Application. "
   "Contact me at email@example.com"
)

games = c.get_player_games_by_month_pgn('simplechessbrah', year=2023, month=10)

response = c.get_player_games_by_month_pgn('simplechessbrah', year=2023, month=10)
games_data = response.json

games_list = []
for game in games.json['pgn'].items():
    games_list.append(game)
    
with open("test2.pgn", "w", encoding="utf-8") as output:
    output.write(games_list[0][1])
