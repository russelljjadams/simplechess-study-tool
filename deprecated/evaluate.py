# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 10:33:58 2023

@author: rjadams
"""

import chess.pgn
import chess.engine

DEPTH = 12
username = "simplechessbrah"  # Replace with your actual username

engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\rjadams\Documents\stockfish\stockfish-windows-x86-64-avx2.exe")

with open("test.pgn") as pgn_file:
    while True:
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
                if board.turn == player_color:
                    verbose = True
                else:
                    verbose = False
                result = engine.analyse(board, chess.engine.Limit(depth=DEPTH))
                #print(result)
                score_before_move = result["score"]
                score_before_move = score_before_move.white().score()
                
                # get the move
                move = node.move
                
                # make the move
                board.push(move)
                
                # get new evaluation
                result = engine.analyse(board, chess.engine.Limit(depth=DEPTH))
                
                score_after_move = result["score"]
                score_after_move = score_after_move.white().score()
                print(result)
                difference = abs(score_before_move - score_after_move)
                if player_color == chess.WHITE:
                    if score_before_move > score_after_move:
                        if score_before_move == 0:
                            score_before_move = .01
                        if score_after_move == 0:
                            score_after_move = .01
                            
                        percentage = abs(difference / score_before_move)
                        
                        if difference > 25 and percentage > .4:
                            node.nags.add(chess.pgn.NAG_DUBIOUS_MOVE)
                            
                if player_color == chess.BLACK:
                    if score_before_move < score_after_move:
                        if score_before_move == 0:
                            score_before_move = .01
                        if score_after_move == 0:
                            score_after_move = .01
                            
                        percentage = abs(difference / score_before_move)
                        
                        if difference > 25 and percentage > .4:
                            node.nags.add(chess.pgn.NAG_DUBIOUS_MOVE)
engine.quit()                 
with open("analyzed_test.pgn", "w", encoding="utf-8") as output_file:
    exporter = chess.pgn.FileExporter(output_file)
    game.accept(exporter)

