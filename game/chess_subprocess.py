import os
import sys
import time

import_dir = sys.argv[1]
sys.path.append(import_dir)

# https://python-chess.readthedocs.io/en/v0.23.10/
import chess
import chess.uci

def main():
    board = None # the chess board object
    stockfish = None

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
        elif args[0] == 'stockfish':
            stockfish = 'TODO'
        elif args[0] == 'piece_at':
            get_piece_at(board, args)
        elif args[0] == 'legal_moves':
            print('#'.join([move.uci() for move in board.legal_moves]))
        elif args[0] == 'make_move':
            set_move(board, args)
        sys.stdout.flush()

def get_piece_at(board, args):
    file_idx, rank_idx = int(args[1]), int(args[2])
    piece = board.piece_at(chess.square(file_idx, rank_idx))
    if piece:
        print(piece.symbol())
    else:
        print('None')

def set_move(board, args):
    move_uci = args[1]
    move = chess.Move.from_uci(move_uci)
    board.push(move)
    print(board.turn)

if __name__ == '__main__':
    main()