import numpy as np
import random
import time
import sys
import copy
from game import GameState

#TODO: Determine optimal rewards
TWO_REWARD = 2
THREE_REWARD = 4
FOUR_REWARD = 100
OPP_REWARD = -4
MIDDLE_MULTIPLIER = 3


class HumanAgent():
    def __init__(self, player: int = 1):
        self.player = player

    def take_turn(self, state) -> int:
        print("Select a valid index")
        valid = state.get_valid_indices()
        vis_list = []
        for i in range(state.size):
            if i in valid:
                vis_list.append(str(i))
            else:
                vis_list.append("*")
        vis_str = " " + " | ".join(vis_list) + "\n"
        print(vis_str)
        print(state)
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

    def take_turn(self, state) -> int:
        start_time = time.time()
        valid = state.get_valid_indices()
        time_taken = (time.time() - start_time) / 1e6 #
        print(f"Player {self.player} (Random Agent) took their turn in {time_taken:.2f} μs")
        return random.choice(valid)


def evaluate_section(section, this_player):
    reward = 0

    if this_player == 1:
        opposing_player = 2
    else:
        opposing_player = 1


    if section.count(this_player) == 2 and section.count(0) == 2:
        reward += TWO_REWARD
    elif section.count(this_player) == 3 and section.count(0) == 1:
        reward += THREE_REWARD
    elif section.count(this_player) == 4:
        reward += FOUR_REWARD

    if section.count(opposing_player) == 3 and section.count(0) == 1:
        reward += OPP_REWARD
    
    print("reward", reward)
    return reward
        
    

def evaluate_state(state, player):
    #TODO: Determine optimal rewards

    reward = 0
    num_rows = state.num_rows
    num_columns = state.num_columns
    middle_col = state.num_columns // 2

    # Score Horizontal, Bottom->Top
    for i in range(num_rows-1, -1, -1):
        for j in range(num_columns - (state.connect - 1)):
            section = [state.board[i, j+c] for c in range(state.connect)]
            reward += evaluate_section(section, player)

    # Score Verticle, Bottom->Top
    for i in range(num_rows-1, state.connect-2, -1):
        for j in range(num_columns):
            if j == middle_col:
                multiplier = MIDDLE_MULTIPLIER
            else:
                multiplier = 1
            section = [state.board[i-c, j] for c in range(state.connect)]
            reward += multiplier * evaluate_section(section, player)
            

    # Score Downward Slope
    for i in range(num_rows-state.connect, -1, -1):
        for j in range(num_columns - (state.connect - 1)):
            section = [state.board[i+c, j+c] for c in range(state.connect)]
            reward += evaluate_section(section, player)

    # Score Upward Slope
    for i in range(num_rows-state.connect, -1, -1):
        for j in range(state.connect -1, num_columns):
            section = [state.board[i+c, j-c] for c in range(state.connect)]
            reward += evaluate_section(section, player)
    
    return reward


class MiniMaxAgent():
    def __init__(self, player: int = 2):
        self.max_player = player
        self.min_player = 2 if player == 1 else 1

    def take_turn(self, game_state: GameState) -> int:
        def minimax(state: GameState, maximizer: bool, depth: int, alpha: int = -sys.maxsize - 1, beta: int = sys.maxsize):
            min_i = None
            max_i = None
            if state.terminal() or depth == 0: 
                if state.has_won(self.max_player):      # max player receives large reward
                    return (None, sys.maxsize)
                elif state.has_won(self.min_player):    # min player receives large reward
                    return (None, -sys.maxsize - 1) 
                if state.is_full():
                    return (None, 0)                    # nobody wins

                if depth == 0:
                    print("depth 0")
                    reward = evaluate_state(state, self.max_player)
                    print(reward)
                    return (None, reward)

            if maximizer:                                 # if it is maximizing players turn
                max_val = -sys.maxsize - 1
                for i in state.get_valid_indices():
                    state_copy = state.__deepcopy__()
                    state_copy.add_piece(self.max_player, i)
                    col, score = minimax(state_copy, False, depth-1, alpha, beta)
                    if score > max_val:
                        max_i = i
                        max_val = score
                    alpha = max(alpha, max_val)
                    if alpha >= beta:
                        break

                return max_i, max_val

            else:                                   # if it is minimizing players turn
                min_val = sys.maxsize
                for i in state.get_valid_indices():
                    state_copy = state.__deepcopy__()
                    state_copy.add_piece(self.min_player, i)
                    col, score = minimax(state_copy, True, depth-1, alpha, beta)
                    if score > min_val:
                        min_i = i
                        min_val = score
                    beta = min(beta, min_val)
                    if alpha >= beta:
                        break

                return min_i, min_val
                
        start_time = time.time()
        col, _ = minimax(game_state, True, 5)
        
        time_taken = (time.time() - start_time) / 1e6 #

        print(f"Player {self.max_player} (MiniMax Agent) took their turn in {time_taken:.2f} μs")
        return col
