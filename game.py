#import tensorflow as tf
import numpy as np
import argparse
from agents import *


class GameState():
    def __init__(self, n: int, connect: int = 4):
        """
        Arguments:
            n: size of board (nxn)
        """
        print(f"Creating a connect four matrix of size {n}X{n}\n")
        self.board = np.zeros((n, n))

        self.player1 = 1
        self.player2 = 2
        self.size = n
        self.connect = 4

        print("Initialized board:")
        print(self)
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

    def add_piece(self, player: int, i: int):
        if all(self.board[:, i]):
            raise ValueError("Selected column is full")

        for j, row in enumerate(self.board):
            if row[i]:
                self.board[j-1, i] = player
                return

        self.board[-1, i] = player

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
                    print("Horizontal Win")
                    return True

        # Check Verticle, Bottom->Top
        for i in range(num_rows-1, self.connect, -1):
            for j in range(num_columns):
                if self.board[i, j] == player and self.board[i-1, j] == player \
                        and self.board[i-2, j] == player and self.board[i-3, j] == player:
                    print("Verticle Win")
                    return True

        # Check Downward Slope
        for i in range(num_rows-self.connect, -1, -1):
            for j in range(num_columns - (self.connect - 1)):
                if self.board[i, j] == player and self.board[i+1, j+1] == player \
                        and self.board[i+2, j+2] == player and self.board[i+3, j+3] == player:
                    print("Downward Slope Win")
                    return True

        # Check Upward Slope
        for i in range(num_rows-self.connect, -1, -1):
            for j in range(self.connect -1, num_columns):
                if self.board[i, j] == player and self.board[i+1, j-1] == player \
                        and self.board[i+2, j-2] == player and self.board[i+3, j-3] == player:
                    print("Upward Slope Win")
                    return True

        return False

    def get_valid_indices(self) -> set:
        valid = set()
        top_row = self.board[0]
        for i, val in enumerate(top_row):
            if val == 0:
                valid.add(i)
        
        return valid

    
    def __str__(self):
        return self.__repr__()
            

def main(n: int):
    board = GameState(n)
    player1 = HumanAgent(player=1)
    player2 = RandomAgent(player=2)

    while True:
        print("\nPlayer 1's Turn\n")
        choice = player1.take_turn(board)
        board.add_piece(player=1, i=choice)

        if board.has_won(1):
            print("\n\nPlayer 1 WINS!\n\n")
            print(board)
            break

        print("\nPlayer 2's Turn\n")
        choice = player2.take_turn(board)
        board.add_piece(player=2, i=choice)

        if board.has_won(2):
            print("\n\nPlayer 2 WINS!\n\n")
            print(board)
            break



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pass Size of the Desired Connect Four Matrix")
    parser.add_argument('-size', metavar="n", type=int, const="default", default=7,
                    help='size of nXn connect four matrix', nargs="?")

    args = parser.parse_args()
    n = args.size
    main(n)