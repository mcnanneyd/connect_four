import numpy as np
import random
import time

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
    def __init__(self, player: int = 2):
        self.player = player

    def take_turn(self, board) -> int:
        start_time = time.time()
        valid = board.get_valid_indices()
        time_taken = (time.time() - start_time) / 1e6 #
        print(f"Player {self.player} (Random Agent) took their turn in {time_taken:.2f} μs")
        return random.choice(tuple(valid))
