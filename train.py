import numpy as np
import random
import time
import sys
import copy
import json
from game import GameState
from agents import MiniMaxAgent
from multiprocessing import Process, cpu_count
from datetime import datetime
import os


def play_game(agent1, agent2, n):
    board = GameState(n)
    while True:
        if board.is_full():
            break
        choice = agent1.take_turn(board)
        board.add_piece(player=1, i=choice)
        with open('error.log', 'a') as f:
            f.write(f"failed to add piece {datetime.now()}\n")
        if board.has_won(1):
            return True

        if board.is_full():
            break
        choice = agent2.take_turn(board)
        board.add_piece(player=2, i=choice)
        with open('error.log', 'a') as f:
            f.write(f"failed to add piece {datetime.now()}\n")

        if board.has_won(2):
            return False

        



def explore(n: int):
    constantAgent = MiniMaxAgent(player=1)
    # Previously used rewards for reference
    two = 2.0
    three = 4.0
    four = 100.0
    opp = -4.0
    middle = 3.0
    val_template = {"wins": 0, "losses": 0, "win_rate": 0}
    num_games = 25
    base_vals = {                
                    "two"   : 2.0 , 
                    "three" : 4.0 ,
                    "four"  : 100 , 
                    "opp"   : -4.0,
                    "middle": 3.0 }

    procedure = {
                "two"   : {"base_val": 2.0 , "range": (0.1, 10, 0.1)} , 
                "three" : {"base_val": 4.0 , "range": (0.1, 20, 0.2)} ,
                "four"  : {"base_val": 100 , "range": (10, 1000, 10)} , 
                "opp"   : {"base_val": -4.0, "range": (-50, -1, 0.5)} ,
                "middle": {"base_val": 3.0 , "range": (1,  500, 5)}
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

                    if results[val]["wins"] > 0 or results[val]["losses"] > 0:
                       results[val]["win_rate"] = results[val]["wins"] / (results[val]["wins"] + results[val]["losses"])
                    else:
                        continue

                    print(f"{variable}{index}.json     run {i * 100 + run }/{len(values) * 100}:", results[val])

                    with open(f"results/{variable}{index}.json", "w") as outfile:
                        json.dump(results, outfile)

                    


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
    explore(7)
