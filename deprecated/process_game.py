# -*- coding: utf-8 -*-
"""
Created on Sat Nov 25 11:51:33 2023

@author: rjadams
"""

import math
import chess.pgn
import chess.engine
import re, os

DEPTH = 16

username = "simplechessbrah"  # Replace with your actual username
engine_path = r"C:\Users\rjadams\Documents\stockfish\stockfish-windows-x86-64-avx2.exe"

def get_percentage_threshold(score_before, percentage_threshold_base=0.42, max_eval_for_strict_percentage=300):
    if abs(score_before) <= max_eval_for_strict_percentage:
        return percentage_threshold_base
    # As the player's advantage increases, the percentage threshold becomes less strict.
    return percentage_threshold_base + math.log(abs(score_before) / max_eval_for_strict_percentage, 10) * 0.05

def process(game, engine, username, cp_threshold=25):
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
                result = engine.analyse(board, chess.engine.Limit(depth=DEPTH))
                score_before_move = result["score"].white().score()
                if score_before_move == None:
                    break

                move = node.move
                board.push(move)
                
                result = engine.analyse(board, chess.engine.Limit(depth=DEPTH))
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

if __name__ == "__main__":
    # Open the engine
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    
    analyzed_games_file = f"saved/analyzed_games_{username}.txt"
    # Load analyzed game_ids if the file exists
    analyzed_games = set()
    if os.path.isfile(analyzed_games_file):
        with open(analyzed_games_file, 'r') as file:
            analyzed_games = set(file.read().splitlines())
    
    # Open the PGN file for both input and output
    with open(f"games/non_analyzed_games_{username}.pgn") as pgn_file, open(f"games/analyzed_games_{username}.pgn", "a", encoding="utf-8") as output_file:
        exporter = chess.pgn.FileExporter(output_file)
        
        game_counter = 0
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            
            link = game.headers["Link"]
            pre_game_id = re.search(r'/(\d+)$', link)
            game_id = pre_game_id.group(1)
            if game_id not in analyzed_games:
                with open(analyzed_games_file, 'a') as file:
                    file.write(game_id + '\n')
                if game is None:
                    break  # No more games in the file
                game_counter += 1
                print(f'Game Number: {game_counter}')
        
                # Process and export the analyzed game
                analyzed_game = process(game, engine, username)
                analyzed_game.accept(exporter)
    
    # Quit the engine
    engine.quit()