import os
import sys
import time

import_dir = sys.argv[1]
sys.path.append(import_dir)

# https://python-chess.readthedocs.io/en/v0.23.10/
import chess
import chess.uci

def main():
    board = None
    while True:
        line = raw_input()
        # some split token corresponding to that in chess_displayable.rpy
        args = line.split('#')
        if not args:
            continue   
        if args[0] == 'quit':
            break
        elif args[0] == 'fen':
            fen = args[1]
            if board is None:
                board = chess.Board(fen=fen)
        elif args[0] == 'piece_at':
            file_idx, rank_idx = int(args[1]), int(args[2])
            piece = board.piece_at(chess.square(file_idx, rank_idx))
            if piece:
                print(piece.symbol())
            else:
                print('None')
        sys.stdout.flush()

if __name__ == '__main__':
    main()