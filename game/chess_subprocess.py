import os
import sys
import time
import subprocess

import_dir = sys.argv[1]
sys.path.append(import_dir)

# https://python-chess.readthedocs.io/en/v0.23.10/
import chess
import chess.uci

# enum game_status as defined in chess_displayable.rpy
CHECKMATE = 1
STALEMATE = 2
INCHECK = 3
THREEFOLD = 4
FIFTYMOVES = 5
DRAW = 6

def main():
    board = None # the chess board object
    stockfish = None # chess AI engine
    stockfish_movetime = None
    stockfish_depth = None

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
            stockfish_movetime = int(args[3])
            stockfish_depth = int(args[4])
            if stockfish is None:
                stockfish = init_stockfish(board, args)

        elif args[0] == 'stockfish_move':
            get_stockfish_move(board, stockfish, stockfish_movetime, stockfish_depth)
        elif args[0] == 'game_status':
            get_game_status(board)
        elif args[0] == 'piece_at':
            get_piece_at(board, args)
        elif args[0] == 'is_capture':
            get_is_capture(board, args)
        elif args[0] == 'make_move':
            set_move(board, args)
        elif args[0] == 'legal_moves':
            print('#'.join([move.uci() for move in board.legal_moves]))
        sys.stdout.flush()

def init_stockfish(board, args):
    stockfish_path = args[1]
    is_os_windows = eval(args[2])

    # stop stockfish from opening up shell
    # https://stackoverflow.com/a/63538680
    startupinfo = None
    if is_os_windows:      
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW

    stockfish = chess.uci.popen_engine(stockfish_path, startupinfo=startupinfo)
    stockfish.uci()
    stockfish.position(board)
    return stockfish

def get_piece_at(board, args):
    file_idx, rank_idx = int(args[1]), int(args[2])
    piece = board.piece_at(chess.square(file_idx, rank_idx))
    if piece:
        print(piece.symbol())
    else:
        print('None')

def get_is_capture(board, args):
    move_uci = args[1]
    move = chess.Move.from_uci(move_uci)
    print(board.is_capture(move))

def get_game_status(board):
    if board.is_checkmate():
        print(CHECKMATE)
        return
    if board.is_stalemate():
        print(STALEMATE)
        return
    if board.can_claim_threefold_repetition():
        print(THREEFOLD)
        return
    if board.can_claim_fifty_moves():
        print(FIFTYMOVES)
        return
    if board.is_check():
        print(INCHECK)
        return
    print('-1') # no change to game_status

def get_stockfish_move(board, stockfish, stockfish_movetime, stockfish_depth):
    stockfish.position(board)
    move = stockfish.go(movetime=stockfish_movetime, depth=stockfish_depth)
    move = move.bestmove
    print(move.uci())

def set_move(board, args):
    move_uci = args[1]
    move = chess.Move.from_uci(move_uci)
    board.push(move)
    print(board.turn)

if __name__ == '__main__':
    main()