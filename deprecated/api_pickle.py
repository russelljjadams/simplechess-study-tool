# -*- coding: utf-8 -*-
"""
Created on Sat Nov 25 15:03:16 2023

@author: rjadams
"""

import chessdotcom as c
import re
import os
import pickle

c.Client.request_config["headers"]["User-Agent"] = (
    "My Python Application. "
    "Contact me at email@example.com"
)

username = "simplechessbrah"

processed_games_file = f'saved/processed_games_{username}.txt'
games_pickle_file = f'saved/games_dict_{username}.pickle'

# Load processed game links if the file exists
processed_game_urls = set()
if os.path.isfile(processed_games_file):
    with open(processed_games_file, 'r') as file:
        processed_game_urls = set(file.read().splitlines())

# Load existing games from the pickle file if it exists
games_dict = {}
if os.path.isfile(games_pickle_file):
    with open(games_pickle_file, 'rb') as file:
        games_dict = pickle.load(file)

# Fetch the games for the specified month
response = c.get_player_games_by_month_pgn(username, year=2023, month=12)
pgn_data = response.json['pgn']

# Extract individual games and their links using regular expressions
games_info = re.findall(r'(\[Event .+?\]\n\n1. .+?)\n\n(?=\[Event|\Z)', pgn_data['pgn'], flags=re.DOTALL)

# Process and store new games
for game in games_info:
    link_match = re.search(r'\[Link "([^"]+)"\]', game)
    if link_match:
        game_url = link_match.group(1)
        game_id = game_url.split('/')[-1]  # Extract the identifier from the URL

        # Add the game to the dictionary if it's not already processed
        if game_id not in processed_game_urls:
            games_dict[game_id] = game  # Save the PGN data in the dictionary
            # Append the link to the processed_games_file
            with open(processed_games_file, 'a') as file:
                file.write(game_id + '\n')
            # Write to PGN
            with open(f"games/non_analyzed_games_{username}.pgn", 'a') as file:
                file.write(game + '\n')

# Update the pickle file with new games
with open(games_pickle_file, 'wb') as file:
    pickle.dump(games_dict, file)