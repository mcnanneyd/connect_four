#import tensorflow as tf
from re import U
import numpy as np
import argparse
from agents import *
import copy
import json
from multiprocessing import Process, cpu_count
from datetime import datetime

class GameState():
    def __init__(self, n: int, connect: int = 4, board: np.ndarray = None):
        """
        Arguments:
            n: size of board (nxn)
        """
        if board is None:
            self.board = np.zeros((n, n))
        else:
            self.board = board
        self.player1 = 1
        self.player2 = 2
        self.size = n
        self.connect = connect

        self.num_columns = n
        self.num_rows = n
    
    def __repr__(self):
        repr_str = ""
        for row in self.board:

            row_repr = []
            for cell in row:
                if cell == self.player1:
                    row_repr.append("O")
                elif cell == self.player2:
                    row_repr.append("X")
                else:
                    row_repr.append("-")

            row_str = " " + " | ".join(row_repr) + "\n" + "_" * (self.size * 4 - 1) + "\n"
            repr_str += row_str
        
        return repr_str

    def __copy__(self):
        return GameState(self.size, self.connect, board=np.copy(self.board))

    def __deepcopy__(self):
        return GameState(self.size, self.connect, board=np.copy(self.board))

    def add_piece(self, player: int, i: int):
        if self.board[:, i].all():
            raise ValueError("Selected column is full")

        for j in range(self.size):
            if self.board[j, i]:
                self.board[j-1, i] = player
                return

        self.board[-1, i] = player

    def is_full(self):
        full = True
        for cell in self.board[0]:
            if not cell:
                full = False
        return full 

    def terminal(self):
        return self.is_full() or self.has_won(1) or self.has_won(2)       

    def has_won(self, player):
        # j ->
        # i |
        #   v

        num_columns = len(self.board[0])
        num_rows = len(self.board)


        # Check Horizontal, Bottom->Top
        for i in range(num_rows-1, -1, -1):
            for j in range(num_columns - (self.connect - 1)):
                if self.board[i, j] == player and self.board[i, j+1] == player \
                        and self.board[i, j+2] == player and self.board[i, j+3] == player:
                    #print("Horizontal Win")
                    return True

        # Check Verticle, Bottom->Top
        for i in range(num_rows-1, self.connect-2, -1):
            for j in range(num_columns):
                if self.board[i, j] == player and self.board[i-1, j] == player \
                        and self.board[i-2, j] == player and self.board[i-3, j] == player:
                    #print("Verticle Win")
                    return True

        # Check Downward Slope
        for i in range(num_rows-self.connect, -1, -1):
            for j in range(num_columns - (self.connect - 1)):
                if self.board[i, j] == player and self.board[i+1, j+1] == player \
                        and self.board[i+2, j+2] == player and self.board[i+3, j+3] == player:
                    #print("Downward Slope Win")
                    return True

        # Check Upward Slope
        for i in range(num_rows-self.connect, -1, -1):
            for j in range(self.connect -1, num_columns):
                if self.board[i, j] == player and self.board[i+1, j-1] == player \
                        and self.board[i+2, j-2] == player and self.board[i+3, j-3] == player:
                    #print("Upward Slope Win")
                    return True

        return False

    def get_valid_indices(self) -> list:
        valid = []
        top_row = self.board[0]
        for i, val in enumerate(top_row):
            if val == 0:
                valid.append(i)
        
        return valid

    
    def __str__(self):
        return self.__repr__()
            

def human(n: int):
    board = GameState(n)
    player1 = HumanAgent(player=1)
    player2 = HumanAgent(player=2)

    while True:
        print("\nPlayer 1's Turn\n")
        choice = player1.take_turn(board)
        print(board)
        board.add_piece(player=1, i=choice)

        if board.has_won(1):
            print("\n\nPlayer 1 WINS!\n\n")
            print(board)
            break

        print("\nPlayer 2's Turn\n")
        choice = player2.take_turn(board)
        print(board)
        board.add_piece(player=2, i=choice)

        if board.has_won(2):
            print("\n\nPlayer 2 WINS!\n\n")
            print(board)
            break

def play_game(agent1, agent2, n):
    board = GameState(n)
    while True:
        if board.is_full():
            break
        choice = agent1.take_turn(board)
        board.add_piece(player=1, i=choice)
        with open('error.log', 'a') as f:
            f.write(f"failed to add piece {datetime.now()}")
        if board.has_won(1):
            return True

        if board.is_full():
            break
        choice = agent2.take_turn(board)
        board.add_piece(player=2, i=choice)
        with open('error.log', 'a') as f:
            f.write(f"failed to add piece {datetime.now()}")

        if board.has_won(2):
            return False

        



def explore(n: int):
    constantAgent = MiniMaxAgent(player=1)
    two = 2.0
    three = 4.0
    four = 100.0
    opp = -4.0
    middle = 3.0
    val_template = {"wins": 0, "losses": 0, "win_rate": 0}
    num_games = 100
    base_vals = {                
                    "two"   : 2.0 , 
                    "three" : 4.0 ,
                    "four"  : 100 , 
                    "opp"   : -4.0,
                    "middle": 3.0 }

    procedure = {
                "two"   : {"base_val": 2.0 , "range": (0.1, 10, 0.1)} , 
                "three" : {"base_val": 4.0 , "range": (0.1, 20, 0.1)} ,
                "four"  : {"base_val": 100 , "range": (10, 500, 1)} , 
                "opp"   : {"base_val": -4.0, "range": (-50, -1, 1)} ,
                "middle": {"base_val": 3.0 , "range": (1,  300, 1)}
    }
    results = {
                "two"   : {} , 
                "three" : {} ,
                "four"  : {} , 
                "opp"   : {} ,
                "middle": {}}


    def var_worker(variable, info):
        def range_worker(variable, values, index):
            params = base_vals.copy()
            results = {}
            for i, val in enumerate(values):
                results[val] = {"wins": 0, "losses": 0, "win_rate": 0}
                params[variable] = val
                for run in range(num_games):
                    constantAgent = MiniMaxAgent(player=1)
                    dynamicAgent = MiniMaxAgent(player = 2, params=params, silent=True, randomize=False)
                    result = play_game(constantAgent, dynamicAgent, n)
                    if result == True:
                        results[val]["wins"] += 1
                    elif result == False:
                        results[val]["losses"] += 1
                    else:
                        constantAgent = MiniMaxAgent(player=1)
                        dynamicAgent = MiniMaxAgent(player = 2, params=params, silent=True, randomize=False)
                        result = play_game(constantAgent, dynamicAgent, n)
                        if result is None:
                            continue

                    results[val]["win_rate"] = results[val]["wins"] / (results[val]["wins"] + results[val]["losses"])


                    print(f"{variable}{index}.json     run {i * 100 + run }/{len(values) * 100}:", results[val])

                    with open(f"results/{variable}{index}.json", "r") as outfile:
                        data = json.load(outfile)
                        print(data)
                    compiled = {**results , **data}
                    with open(f"results/{variable}{index}.json", "w") as outfile:
                        json.dump(compiled)

                    


        lower_bound = info["range"][0]
        upper_bound = info["range"][1]
        step_size = info["range"][2]
        results[variable] = val_template.copy()
        all_vals = np.arange(float(lower_bound), float(upper_bound), float(step_size))
        sections = np.array_split(all_vals, 4)

        range_procs = []
        for i, section in enumerate(sections):
            proc = Process(target=range_worker, args=(variable, section, i,))
            range_procs.append(proc)
            proc.start()

        for proc in range_procs:
            proc.join()
        

    procs = []
    for variable, info in procedure.items():
        proc = Process(target=var_worker, args=(variable, info,))
        procs.append(proc)
        proc.start()
    
    print(f"exploration being conducted on {cpu_count()} cpu cores")

    for proc in procs:
        proc.join()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pass Size of the Desired Connect Four Matrix")
    parser.add_argument('-size', metavar="n", type=int, const="default", default=7,
                    help='size of nXn connect four matrix', nargs="?")

    args = parser.parse_args()
    n = args.size
    #while True:
    #human(n)
    explore(n)