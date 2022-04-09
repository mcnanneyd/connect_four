#import tensorflow as tf
import numpy as np
import argparse


class GameState():
    def __init__(self, n: int):
        """
        Arguments:
            n: size of board (nxn)
        """
        print(f"Creating a connect four matrix of size {n}X{n}\n")
        self.board = np.zeros((n, n))

        self.player1 = 1
        self.player2 = 2
        self.size = n

        print("Initialized board:")
        print(self)
    
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
    
    def __str__(self):
        return self.__repr__()
            

def main(n: int):
    board = GameState(n)
    board.add_piece(1, 1)
    board.add_piece(1, 3)
    board.add_piece(2, 3)
    board.add_piece(2, 3)
    board.add_piece(2, 3)
    board.add_piece(2, 3)
    board.add_piece(2, 3)
    board.add_piece(2, 3)
    board.add_piece(2, 3)

    print(board)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pass Size of the Desired Connect Four Matrix")
    parser.add_argument('-size', metavar="n", type=int, const="default", default=8,
                    help='size of nXn connect four matrix', nargs="?")

    args = parser.parse_args()
    n = args.size
    main(n)