import numpy as np
import random
import time
import sys
import copy
from game import GameState

class HumanAgent():
    def __init__(self, player: int = 1):
        self.player = player

    def take_turn(self, board) -> int:
        print("Select a valid index")
        valid = board.get_valid_indices()
        vis_list = []
        for i in range(board.size):
            if i in valid:
                vis_list.append(str(i))
            else:
                vis_list.append("*")
        vis_str = " " + " | ".join(vis_list) + "\n"
        print(vis_str)
        print(board)
        while True:
            request = input("Input Move: ")
            try:
                if int(request.strip()) in valid:
                    return int(request.strip())
                else:
                    print("Ivalid selection!")
            except:
                print("Ivalid selection!")


class RandomAgent():
    def __init__(self, player: int = 2, depth: int = 25):
        self.player = player

    def take_turn(self, board) -> int:
        start_time = time.time()
        valid = board.get_valid_indices()
        time_taken = (time.time() - start_time) / 1e6 #
        print(f"Player {self.player} (Random Agent) took their turn in {time_taken:.2f} μs")
        return random.choice(valid)


class MiniMaxAgent():
    def __init__(self, player: int = 2):
        self.max_player = player
        self.min_player = 2 if player == 1 else 1

    def take_turn(self, game_board: GameState) -> int:
        def minimax(board: GameState, max: bool, depth: int, alpha: int = sys.maxsize, beta: int = -sys.maxsize - 1):
            if board.terminal(): 
                if board.has_won(self.max_player):      # max player receives large reward
                    return (None, sys.maxsize)
                elif board.has_won(self.min_player):    # min player receives large reward
                    return (None, -sys.maxsize - 1) 
                return (None, 0)                        # nobody wins

            if max:                                 # if it is maximizing players turn
                max_val = -sys.maxsize - 1
                for i in board.get_valid_indices():
                    board_copy = copy.deepcopy(board)
                    board_copy.add_piece(self.max_player, i)
                    score = minimax(board_copy, False, depth-1, alpha, beta)[1]
                    if score > max_val:
                        max_i = i
                        max_val = score
                    alpha = max(alpha, max_val)
                    if alpha >= beta:
                        break

                return max_i, max_val

            else:                                   # if it is minimizing players turn
                max_val = sys.minint
                for i in board.get_valid_indices():
                    board_copy = copy.deepcopy(board)
                    board_copy.add_piece(self.min_player, i)
                    score = minimax(board_copy, True, depth-1, alpha, beta)[1]
                    if score > min_val:
                        min_i = i
                        min_val = score
                    beta = min(beta, min_val)
                    if alpha >= beta:
                        break

                return min_i, min_val
                
        start_time = time.time()
        col, _ = minimax(game_board, True, game_board.size)
        
        time_taken = (time.time() - start_time) / 1e6 #

        print(f"Player {self.max_player} (MiniMax Agent) took their turn in {time_taken:.2f} μs")
        return col
