import os
import sys
import time
import subprocess

import_dir = sys.argv[1]
sys.path.append(import_dir)

# https://python-chess.readthedocs.io/en/v0.23.10/
import chess
import chess.uci

def main():
    
    chess_engine = ChessEngine()

    while True:
        line = raw_input()
        # some split token corresponding to that in chess_displayable.rpy
        args = line.split('#')
        if not args:
            continue   
        if args[0] == 'quit':
            break

        elif args[0] == 'fen':
            chess_engine.init_board(args)
        elif args[0] == 'stockfish':
            chess_engine.init_stockfish(args)

        elif args[0] == 'stockfish_move':
            chess_engine.get_stockfish_move()
        elif args[0] == 'game_status':
            chess_engine.get_game_status()
        elif args[0] == 'piece_at':
            chess_engine.get_piece_at(args)
        elif args[0] == 'is_capture':
            chess_engine.get_is_capture(args)
        elif args[0] == 'legal_moves':
            chess_engine.get_legal_moves()
        elif args[0] == 'push_move':
            chess_engine.push_move(args)
        elif args[0] == 'pop_move':
            chess_engine.pop_move()

        sys.stdout.flush()


class ChessEngine():

    def __init__(self):
        # enum game_status as defined in chess_displayable.rpy
        self.INCHECK = 1
        self.THREEFOLD = 2
        self.FIFTYMOVES = 3
        self.DRAW = 4
        self.CHECKMATE = 5
        self.STALEMATE = 6

        self.board = None # the chess board object
        self.stockfish = None # chess AI engine
        self.stockfish_movetime = None
        self.stockfish_depth = None

    def init_board(self, args):
        fen = args[1]
        self.board = chess.Board(fen=fen)

    def init_stockfish(self, args):
        stockfish_path = args[1]
        is_os_windows = eval(args[2])
        self.stockfish_movetime = int(args[3])
        self.stockfish_depth = int(args[4])

        # stop stockfish from opening up shell on windows
        # https://stackoverflow.com/a/63538680
        startupinfo = None
        if is_os_windows:      
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW

        self.stockfish = chess.uci.popen_engine(stockfish_path, startupinfo=startupinfo)
        self.stockfish.uci()
        self.stockfish.position(self.board)

    def get_piece_at(self, args):
        file_idx, rank_idx = int(args[1]), int(args[2])
        piece = self.board.piece_at(chess.square(file_idx, rank_idx))
        if piece:
            print(piece.symbol())
        else:
            print('None')

    def get_is_capture(self, args):
        move_uci = args[1]
        move = chess.Move.from_uci(move_uci)
        print(self.board.is_capture(move))

    def get_game_status(self):
        if self.board.is_checkmate():
            print(self.CHECKMATE)
            return
        if self.board.is_stalemate():
            print(self.STALEMATE)
            return
        if self.board.can_claim_threefold_repetition():
            print(self.THREEFOLD)
            return
        if self.board.can_claim_fifty_moves():
            print(self.FIFTYMOVES)
            return
        if self.board.is_check():
            print(self.INCHECK)
            return
        print('-1') # no change to game_status

    def get_stockfish_move(self):
        self.stockfish.position(self.board)
        move = self.stockfish.go(movetime=self.stockfish_movetime, depth=self.stockfish_depth)
        move = move.bestmove
        print(move.uci())

    def get_legal_moves(self):
        print('#'.join([move.uci() for move in self.board.legal_moves]))

    def push_move(self, args):
        move_uci = args[1]
        move = chess.Move.from_uci(move_uci)
        self.board.push(move)
        print(self.board.turn)

    def pop_move(self):
        # this should not raise an IndexError as the logic has been handled by the caller
        self.board.pop()
        print(self.board.turn)

if __name__ == '__main__':
    main()