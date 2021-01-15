import os
import sys

import_dir = sys.argv[1]
sys.path.append(import_dir)

sys.stderr.write(str(sys.path))
sys.stderr.flush()

# https://python-chess.readthedocs.io/en/v0.23.11/
import chess
import chess.uci

# print('P')

print('Im a  happy subprocess')
sys.stdout.flush()

# while True:
#     line = input()
#     # print('subb: ' + line)
#     print('P')
#     sys.stdout.flush()

# def main():
#     while True:
#         line = input()
#         print(line)
#         args = line.split()
#         if not args:
#             continue   
#         if args[0] == 'quit':
#             break
#         elif args[0] == 'fen':
#             fen = args[1]
#             board = chess.Board(fen=fen)
#         elif args[0] == 'piece_at':
#             file_idx, rank_idx = args[1], args[2]
#             print('P')
#         sys.stdout.flush()

# if __name__ == '__main__':
#     main()