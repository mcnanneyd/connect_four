import numpy as np
import random
import time
import sys
import copy

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



class MiniMaxAgent():
    def __init__(self, player: int = 2, params = None, silent = True, randomize = True):
        self.max_player = player
        self.min_player = 2 if player == 1 else 1
        self.silent = silent
        if not params:
            params = {                
                    "two"   :2.0 , 
                    "three" :4.0 ,
                    "four"  :100 , 
                    "opp"   :-4.0,
                    "middle":3.0
            }
        if randomize:
            for key in params.keys():
                params[key] *= random.uniform(0.1, 10)



        self.TWO_REWARD = params["two"]
        self.THREE_REWARD = params["three"]
        self.FOUR_REWARD = params["four"]
        self.OPP_REWARD = params["opp"]
        self.MIDDLE_MULTIPLIER = params["middle"]

    def take_turn(self, game_state) -> int:
        def minimax(state, maximizer: bool, depth: int, alpha: int = -sys.maxsize - 1, beta: int = sys.maxsize):
            if state.terminal() or depth == 0: 
                if state.has_won(self.max_player):      # max player receives large reward
                    return (None, sys.maxsize)
                elif state.has_won(self.min_player):    # min player receives large reward
                    return (None, -sys.maxsize - 1) 
                elif state.is_full():
                    return (None, 0)                    # nobody wins

                if depth == 0:
                    reward = self.evaluate_state(state, self.max_player)
                    return (None, reward)
            min_i = random.choice(state.get_valid_indices())
            max_i = random.choice(state.get_valid_indices())

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
                    if score < min_val:
                        min_i = i
                        min_val = score
                    beta = min(beta, min_val)
                    if alpha >= beta:
                        break

                return min_i, min_val
                
        start_time = time.time()
        col, _ = minimax(game_state, True, 5)
        
        time_taken = (time.time() - start_time) #

        if not self.silent:
            print(f"Player {self.max_player} (MiniMax Agent) took their turn in {time_taken:.2f} s - choice {col}")
        return col


    def evaluate_state(self, state, player):
        #TODO: Determine optimal rewards

        reward = 0
        num_rows = state.num_rows
        num_columns = state.num_columns
        middle_col = state.num_columns // 2 + 1

        # Score Horizontal, Bottom->Top
        for i in range(num_rows-1, -1, -1):
            for j in range(num_columns - (state.connect - 1)):
                section = [state.board[i, j+c] for c in range(state.connect)]
                reward += self.evaluate_section(section, player)

        # Score Verticle, Bottom->Top
        for i in range(num_rows-1, state.connect-2, -1):
            for j in range(num_columns):
                if j == middle_col:
                    multiplier = self.MIDDLE_MULTIPLIER
                else:
                    multiplier = 1
                section = [state.board[i-c, j] for c in range(state.connect)]
                reward += multiplier * self.evaluate_section(section, player)
                

        # Score Downward Slope
        for i in range(num_rows-state.connect, -1, -1):
            for j in range(num_columns - (state.connect - 1)):
                section = [state.board[i+c, j+c] for c in range(state.connect)]
                reward += self.evaluate_section(section, player)

        # Score Upward Slope
        for i in range(num_rows-state.connect, -1, -1):
            for j in range(state.connect -1, num_columns):
                section = [state.board[i+c, j-c] for c in range(state.connect)]
                reward += self.evaluate_section(section, player)
        
        return reward

    def evaluate_section(self, section, this_player):
        reward = 0

        if this_player == 1:
            opposing_player = 2
        else:
            opposing_player = 1


        if section.count(this_player) == 2 and section.count(0) == 2:
            reward += self.TWO_REWARD
        elif section.count(this_player) == 3 and section.count(0) == 1:
            reward += self.THREE_REWARD
        elif section.count(this_player) == 4:
            reward += self.FOUR_REWARD

        if section.count(opposing_player) == 3 and section.count(0) == 1:
            reward += self.OPP_REWARD
        
        return reward
            