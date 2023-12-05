# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 13:14:43 2023

@author: rjadams
"""

import os
import pickle
import re
import chess
import chess.pgn
import chess.engine
import chessdotcom
import math
from datetime import datetime, timedelta

# Constants
CONFIG_FILE = 'config.pkl'
PROCESSED_GAMES_FILE_TEMPLATE = 'saved/processed_games_{username}.txt'
GAMES_PICKLE_FILE_TEMPLATE = 'saved/games_dict_{username}.pickle'
ANALYZED_GAMES_FILE_TEMPLATE = 'games/analyzed_games_{username}.pgn'
NON_ANALYZED_GAMES_FILE_TEMPLATE = 'games/non_analyzed_games_{username}.pgn'
TO_STUDY_FILE_TEMPLATE = 'to_study/moves_to_study_{username}.pgn'

# Set up default User-Agent for chess.com API
chessdotcom.Client.request_config["headers"]["User-Agent"] = (
    "My Python Application. "
    "Contact me at example@example.com"
)

# Helper function definitions:

def load_config():
    # Load or create a configuration dict
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, 'rb') as file:
            return pickle.load(file)
    return {}

def save_config(config):
    # Save the current configuration dict to a file
    with open(CONFIG_FILE, 'wb') as file:
        pickle.dump(config, file)

def get_user_input(config):
    # Collect user input and save it to the config dict
    config['username'] = input("Enter your chess.com username: ") if 'username' not in config else config['username']
    config['year'] = input("Enter the year to retrieve games from (e.g., 2023): ") if 'year' not in config else config['year']
    config['month'] = input("Enter the month to retrieve games from (1-12): ") if 'month' not in config else config['month']
    config['engine_path'] = input("Enter the full path to the Stockfish engine: ") if 'engine_path' not in config else config['engine_path']
    config['depth'] = int(input("Enter the depth for the Stockfish analysis (e.g., 16): ")) if 'depth' not in config else config['depth']
    save_config(config)
    return config

def get_percentage_threshold(score_before, percentage_threshold_base=0.42, max_eval_for_strict_percentage=300):
    if abs(score_before) <= max_eval_for_strict_percentage:
        return percentage_threshold_base
    return percentage_threshold_base + math.log(abs(score_before) / max_eval_for_strict_percentage, 10) * 0.05

def fetch_games(config):
    """
    Fetch games from the chess.com API and process each game to extract PGN info and positions
    """
    username = config['username']
    year = config['year']
    month = config['month']
    
    processed_games_file = PROCESSED_GAMES_FILE_TEMPLATE.format(username=username)
    games_pickle_file = GAMES_PICKLE_FILE_TEMPLATE.format(username=username)

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
    response = chessdotcom.get_player_games_by_month_pgn(username, year=int(year), month=int(month))
    pgn_data = response.json['pgn']

    # Extract individual games and their links using regular expressions
    games_info = re.findall(r'(\[Event .+?\]\n\n1. .+?)\n\n(?=\[Event|\Z)', pgn_data['pgn'], flags=re.DOTALL)

    # Create folder if doesn't exist
    non_analyzed_games_dir = os.path.dirname(NON_ANALYZED_GAMES_FILE_TEMPLATE.format(username=username))
    os.makedirs(non_analyzed_games_dir, exist_ok=True)

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
                with open(NON_ANALYZED_GAMES_FILE_TEMPLATE.format(username=username), 'a') as file:
                    file.write(game + '\n\n')

    # Update the pickle file with new games
    with open(games_pickle_file, 'wb') as file:
        pickle.dump(games_dict, file)
        

def process(game, engine, username, depth=16, cp_threshold=25):
    white_player = game.headers["White"]
    black_player = game.headers["Black"]
    
    player_color = None
    if white_player == username:
        player_color = chess.WHITE
    elif black_player == username:
        player_color = chess.BLACK
    if player_color is not None:
        board = game.board()
        for node in game.mainline():
            if board.turn == player_color:
                result = engine.analyse(board, chess.engine.Limit(depth=depth))
                score_before_move = result["score"].white().score()
                if score_before_move == None:
                    break

                move = node.move
                board.push(move)
                
                result = engine.analyse(board, chess.engine.Limit(depth=depth))
                score_after_move = result["score"].white().score()
                if score_after_move == None:
                    break

                difference = abs(score_before_move - score_after_move)
                if player_color == chess.WHITE:
                    if score_before_move > score_after_move:
                        if score_before_move == 0:
                            score_before_move = .01
                        if score_after_move == 0:
                            score_after_move = .01
                            
                        percentage_threshold = get_percentage_threshold(score_before_move)
                        percentage = abs(difference / score_before_move) 
                        
                        if difference > cp_threshold and percentage > percentage_threshold:
                            node.nags.add(chess.pgn.NAG_DUBIOUS_MOVE)
                            
                if player_color == chess.BLACK:
                    if score_before_move < score_after_move:
                        if score_before_move == 0:
                            score_before_move = .01
                        if score_after_move == 0:
                            score_after_move = .01
                            
                        percentage_threshold = get_percentage_threshold(score_before_move)
                        percentage = abs(difference / score_before_move)
                        
                        if difference > cp_threshold and percentage > percentage_threshold:
                            node.nags.add(chess.pgn.NAG_DUBIOUS_MOVE)

            else:
                move = node.move
                board.push(move)

    return game

def analyze_games_with_stockfish(config):
    username = config['username']
    engine_path = config['engine_path']
    depth = config['depth']

    analyzed_games_file = ANALYZED_GAMES_FILE_TEMPLATE.format(username=username)
    non_analyzed_games_file = NON_ANALYZED_GAMES_FILE_TEMPLATE.format(username=username)

    # Open the engine
    with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
        # Load analyzed game_ids if the file exists
        analyzed_games = set()
        if os.path.isfile(analyzed_games_file):
            with open(analyzed_games_file, 'r') as file:
                analyzed_games = set(file.read().splitlines())
                
        analyzed_games_update = set()

        # Open the non-analyzed PGN file for reading
        with open(non_analyzed_games_file) as pgn_file:
            game_counter = 0
            while True:
                game = chess.pgn.read_game(pgn_file)
                if game is None:
                    break  # No more games in the file
                
                link = game.headers["Link"]
                game_id = re.search(r'/(\d+)$', link).group(1)
                if game_id not in analyzed_games and game_id not in analyzed_games_update:
                    game_counter += 1
                    print(f'Analyzing game {game_counter}: {link}')
                    analyzed_game = process(game, engine, username, depth)
                    
                    # Write the analyzed game to the ANALYZED_GAMES_FILE.
                    with open(analyzed_games_file, 'a', encoding='utf-8') as output_file:
                        print(analyzed_game, file=output_file, end='\n\n')
                        
                    analyzed_games_update.add(game_id)
                    
        # Update the list of analyzed games.
        with open(analyzed_games_file, 'a') as file:
            for game_id in analyzed_games_update:
                file.write(game_id + '\n')
                
                
def extract_moves_for_study(config):
    username = config['username']
    analyzed_games_file = ANALYZED_GAMES_FILE_TEMPLATE.format(username=username)
    to_study_file = TO_STUDY_FILE_TEMPLATE.format(username=username)
    
    not_decent_moves_info = []  # Accumulate information from all games here

    # Ensure that the Stockfish engine is closed if it was mistakenly left open
    # It's not needed for this function as we're only extracting annotated moves
    with open(analyzed_games_file) as pgn_file:
        game_counter = 0
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            game_counter += 1
            print(f'Analyzing Game: {game_counter}')
            white_player = game.headers["White"]
            black_player = game.headers["Black"]

            player_color = None
            if white_player == username:
                player_color = chess.WHITE
            elif black_player == username:
                player_color = chess.BLACK

            if player_color is not None:
                board = game.board()

                for node in game.mainline():
                    fen_before_move = board.fen()
                    move = node.move

                    if board.turn == player_color and (
                        chess.pgn.NAG_DUBIOUS_MOVE in node.nags or
                        chess.pgn.NAG_MISTAKE in node.nags or
                        chess.pgn.NAG_BLUNDER in node.nags):

                        not_decent_moves_info.append([fen_before_move, move.uci()])
                    board.push(move)

    # Create directory for study files if it doesn't exist
    study_dir = os.path.dirname(to_study_file)
    os.makedirs(study_dir, exist_ok=True)

    # Create a PGN file for all the accumulated positions from different games
    with open(to_study_file, 'w', encoding='utf-8') as pgn_file:
        for fen, move_uci in not_decent_moves_info:
            game = chess.pgn.Game()
            game.headers["Event"] = "Bad Moves Analysis"
            game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
            game.headers["Round"] = "?"
            game.headers["White"] = username  # Adjust if needed
            game.headers["Black"] = "Analysis"
            game.headers["Result"] = "*"
            game.setup(chess.Board(fen))

            # Add the bad move to the game
            move = chess.Move.from_uci(move_uci)
            node = game.add_variation(move)
            node.comment = "Bad move identified for review."

            # Write to the PGN file
            exporter = chess.pgn.FileExporter(pgn_file)
            game.accept(exporter)

    print("Finished creating moves_to_study.pgn with positions to review.")                


def get_previous_month_year():
    today = datetime.now()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)
    return last_month.year, last_month.month

def main():
    config = load_config()
    
    # If user input needed for other settings, uncomment the next line
    config = get_user_input(config)
    
    # Automatically determine the previous month for analysis
    config['year'], config['month'] = get_previous_month_year()
    
    fetch_games(config)  # Fetch and save games from the previous month
    analyze_games_with_stockfish(config)  # Analyze games with Stockfish
    extract_moves_for_study(config)  # Extract study moves from the previous month

if __name__ == "__main__":
    main()