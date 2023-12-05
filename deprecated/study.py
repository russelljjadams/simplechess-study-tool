# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 10:29:14 2023

@author: rjadams
"""

import chess.pgn
import chess.engine

from datetime import datetime

username = "simplechessbrah"  # Replace with your actual username
not_decent_moves_info = []  # Accumulate information from all games here

engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\rjadams\Documents\stockfish\stockfish-windows-x86-64-avx2.exe")


with open("test.pgn") as pgn_file:
    game_counter = 1
    while True:
        print(f'Game: {game_counter}')
        game_counter += 1
        game = chess.pgn.read_game(pgn_file)
        if game is None:
            break

        # Process each game and extract information
        white_player = game.headers["White"]
        black_player = game.headers["Black"]

        # Find out if the user is playing white or black
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

# Create a PGN file for all the accumulated positions from different games
with open('test_positions.pgn', 'w', encoding='utf-8') as pgn_file:
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

print("Finished creating bad_moves.pgn with bad move positions.")