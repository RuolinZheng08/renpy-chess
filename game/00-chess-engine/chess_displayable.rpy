# BEGIN DEF

# directory paths
# the path of the current directory within game/
define THIS_PATH = '00-chess-engine/'
define IMAGE_PATH = 'images/'
define AUDIO_PATH = 'audio/'
define BIN_PATH = 'bin/' # stockfish binaries
define CHESSPIECES_PATH = THIS_PATH + IMAGE_PATH + 'chesspieces/'

# file paths
define IMG_CHESSBOARD = THIS_PATH + IMAGE_PATH + 'chessboard.png'
define AUDIO_MOVE = THIS_PATH + AUDIO_PATH + 'move.wav'
define AUDIO_CAPTURE = THIS_PATH + AUDIO_PATH + 'capture.wav'
define AUDIO_PROMOTION = THIS_PATH + AUDIO_PATH + 'promotion.wav'
define AUDIO_CHECK = THIS_PATH + AUDIO_PATH + 'check.wav'
define AUDIO_CHECKMATE = THIS_PATH + AUDIO_PATH + 'checkmate.wav'
define AUDIO_DRAW = THIS_PATH + AUDIO_PATH + 'draw.wav' # used for resign, stalemate, threefold, fifty-move
define AUDIO_FLIP_BOARD = THIS_PATH + AUDIO_PATH + 'flip_board.wav'

# this chess game is full-screen when the game resolution is 1280x720
define CHESS_SCREEN_WIDTH = 1280
define CHESS_SCREEN_HEIGHT = 720

# use loc to mean UI square and distinguish from logical square
define LOC_LEN = 90 # length of one side of a loc

# both file and rank index from 0 to 7
define INDEX_MIN = 0
define INDEX_MAX = 7
# 'a' is the leftmost file with index 0
define FILE_LETTERS = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')

define PROMOTION_RANK_WHITE = 6 # INDEX_MAX - 1
define PROMOTION_RANK_BLACK = 1 # INDEX_MIN + 1

define COLOR_HOVER = '#90ee90aa' # HTML LightGreen
define COLOR_SELECTED = '#40e0d0aa' # Turquoise
define COLOR_LEGAL_DST = '#afeeeeaa' # PaleTurquoise
define COLOR_PREV_MOVE = '#6a5acdaa' # SlateBlue
define COLOR_WHITE = '#fff'

define TEXT_SIZE = 26
define TEXT_BUTTON_SIZE = 45 # promotion piece and flip-board arrow button
define TEXT_WHOSETURN_COORD = (-260, 40)
define TEXT_STATUS_COORD = (-260, 80)

# use tuples for immutability
define PIECE_TYPES = ('p', 'r', 'b', 'n', 'k', 'q')

# number of history moves to display
define NUM_HISTORY = 5

# stockfish params
define MIN_MOVETIME = 100 # min thinking time in milliseconds
define MAX_MOVETIME = 3000 # max thinking time in milliseconds
define MIN_DEPTH = 1
define MAX_DEPTH = 20

# constants from the python-chess library
define STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

# BEGIN ENUM
# color
define WHITE = True
define BLACK = False

# status code enum
define INCHECK = 1
define THREEFOLD = 2
define FIFTYMOVES = 3
# end game conditions and _return code
define DRAW = 4
define CHECKMATE = 5 # chess.WHITE is True i.e. 1 and chess.BLACK is False i.e. 0
define STALEMATE = 6

# END ENUM
# END DEF

# BEGIN STYLE

style game_status_text is text:
    font 'DejaVuSans.ttf'
    color COLOR_WHITE
    size TEXT_SIZE

style promotion_piece is button
style promotion_piece_text is text:
    font 'DejaVuSans.ttf'
    size TEXT_BUTTON_SIZE
    color '#aaaaaa' # gray
    hover_color '#555555' # darker gray
    selected_color COLOR_WHITE

# text button styles for the chess screen
# used for the resign button and the undo-last-move button
style control_button is button
style control_button_text is text:
    font 'DejaVuSans.ttf'
    size TEXT_BUTTON_SIZE
    color '#aaaaaa' # gray
    hover_color COLOR_WHITE

# END STYLE

# BEGIN SCREEN

screen chess(fen, player_color, movetime, depth):
    
    modal True

    default hover_displayable = HoverDisplayable()
    default chess_displayable = ChessDisplayable(fen=fen, 
        player_color=player_color, movetime=movetime, depth=depth)

    add Solid('#000') # black

    # left top panel for diplaying whoseturn text
    fixed xpos 20 ypos 80 spacing 40:
        vbox:
            showif chess_displayable.whose_turn == WHITE:
                text 'Whose turn: White' style 'game_status_text'
            else:
                text 'Whose turn: Black' style 'game_status_text'
            
            showif chess_displayable.game_status == CHECKMATE:
                text 'Checkmate' style 'game_status_text'
            elif chess_displayable.game_status == STALEMATE:
                text 'Stalemate' style 'game_status_text'
            elif chess_displayable.game_status == INCHECK:
                text 'In Check' style 'game_status_text'
            # no need to display DRAW or RESIGN as they immediately return

            null height 50

            text 'Most recent moves' style 'game_status_text' xalign 0.5
            for move in chess_displayable.history:
                text (move) style 'game_status_text' xalign 0.5

    # left bottom
    fixed xpos 20 ypos 500:
        vbox:
            hbox spacing 5:
                text 'Resign' color COLOR_WHITE yalign 0.5
                textbutton '⚐':
                    action [Confirm('Would you like to resign?', 
                        yes=[Play('sound', AUDIO_DRAW),
                        Function(chess_displayable.kill_chess_subprocess), 
                        # if the current player resigns, the winner will be the opposite side
                        Return(not chess_displayable.whose_turn)])]
                    style 'control_button' yalign 0.5

            hbox spacing 5:
                text 'Undo move' color COLOR_WHITE yalign 0.5
                textbutton '⟲':
                    action [Function(chess_displayable.undo_move)]
                    style 'control_button' yalign 0.5

            hbox spacing 5:
                text 'Flip board view' color COLOR_WHITE yalign 0.5
                textbutton '↑↓':
                    action [Play('sound', AUDIO_FLIP_BOARD),
                    ToggleField(chess_displayable, 'bottom_color'),
                    SetField(chess_displayable, 'has_flipped_board', True)]
                    style 'control_button' yalign 0.5

    # middle panel for chess displayable
    fixed xpos 280:
        add Image(IMG_CHESSBOARD)
        add chess_displayable
        add hover_displayable # hover loc over chesspieces
        if chess_displayable.game_status == CHECKMATE:
            # use a timer so the player can see the screen once again
            timer 4.0 action [Function(chess_displayable.kill_chess_subprocess), Return(chess_displayable.winner)]
        elif chess_displayable.game_status == STALEMATE:
            timer 4.0 action [Function(chess_displayable.kill_chess_subprocess), Return(DRAW)]

    # right panel for promotion selection
    showif chess_displayable.show_promotion_ui:
        text 'Select promotion piece type' xpos 1010 ypos 180 color COLOR_WHITE size 18
        vbox xalign 0.9 yalign 0.5 spacing 20:
            null height 40
            textbutton '♜':
                action SetField(chess_displayable, 'promotion', 'r') style 'promotion_piece'
            textbutton '♝':
                action SetField(chess_displayable, 'promotion', 'b') style 'promotion_piece'
            textbutton '♞':
                action SetField(chess_displayable, 'promotion', 'n') style 'promotion_piece'
            textbutton '♛':
                action SetField(chess_displayable, 'promotion', 'q') style 'promotion_piece'

# END SCREEN

init python:

    # use UCI for move notations and FEN for board and move history
    # terms like cursor and coord, Stockfish and AI may be used interchangably

    import os
    import sys
    import pygame
    from collections import deque # track move history

    # stockfish engine is OS-dependent
    if renpy.android:
        STOCKFISH = 'stockfish-10-armv7' # 32 bit
    elif renpy.ios:
        STOCKFISH = 'stockfish-11-64' # FIXME: no iOS stockfish available
    elif renpy.linux:
        STOCKFISH = 'stockfish_20011801_x64'
    elif renpy.macintosh:
        STOCKFISH = 'stockfish-11-64'
    elif renpy.windows:
        STOCKFISH = 'stockfish_20011801_x64.exe'

    # mark the Mac and Linux stockfish binaries as executable
    stockfish_dir = os.path.join('game', THIS_PATH, BIN_PATH)
    build.executable(os.path.join(stockfish_dir, 'stockfish-11-64')) # mac
    build.executable(os.path.join(stockfish_dir, 'stockfish_20011801_x64')) # linux

    class HoverDisplayable(renpy.Displayable):
        """
        Highlights the hovered loc in green
        """
        def __init__(self):
            super(HoverDisplayable, self).__init__()
            self.hover_coord = None
            self.hover_img = Solid(COLOR_HOVER, xsize=LOC_LEN, ysize=LOC_LEN)

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)
            if self.hover_coord:
                render.place(self.hover_img, 
                    x=self.hover_coord[0], y=self.hover_coord[1], 
                    width=LOC_LEN, height=LOC_LEN)
            return render

        def event(self, ev, x, y, st):
            # use screen height b/c chess displayable is a square
            if 0 < x < CHESS_SCREEN_HEIGHT and ev.type == pygame.MOUSEMOTION:
                self.hover_coord = round_coord(x, y)
                renpy.redraw(self, 0)                

    class ChessDisplayable(renpy.Displayable):
        """
        The main displayable for the chess minigame
        If player_color is None, use Player vs. Player mode
        Else, use Player vs. Stockfish mode
        player_color: None, chess.WHITE, chess.BLACK
        """
        def __init__(self, fen=STARTING_FEN, player_color=None, movetime=2000, depth=10):

            import subprocess # for communicating with the chess engine

            super(ChessDisplayable, self).__init__()

            chess_script = os.path.join(renpy.config.gamedir, THIS_PATH, 'chess_subprocess.py')
            # for importing libraries
            import_dir = os.path.join(renpy.config.gamedir, THIS_PATH, 'python-packages')

            startupinfo = None
            if renpy.windows:      
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
            self.chess_subprocess = subprocess.Popen(
                [sys.executable, chess_script, import_dir],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                startupinfo=startupinfo)
            
            self.chess_subprocess.stdin.write('#'.join(['fen', fen, '\n']))
            # no return code to parse

            self.whose_turn = WHITE
            self.has_flipped_board = False # for flipping board view

            self.history = deque([], NUM_HISTORY)

            self.player_color = player_color

            if self.player_color is None: # player vs player
                self.bottom_color = WHITE # white on the bottom of screen by default
                self.uses_stockfish = False # no AI

            else: # player vs computer
                self.bottom_color = self.player_color # player color on the bottom
                self.uses_stockfish = True

                # validate stockfish params movetime and depth
                movetime = movetime if MIN_MOVETIME <= movetime <= MAX_MOVETIME else MAX_MOVETIME
                depth = depth if MIN_DEPTH <= depth <= MAX_DEPTH else MAX_DEPTH

                # load appropraite stockfish binary in subprocess
                stockfish_path = os.path.abspath(os.path.join(renpy.config.gamedir, THIS_PATH, BIN_PATH, STOCKFISH))
                self.chess_subprocess.stdin.write('#'.join([
                    'stockfish', stockfish_path, str(renpy.windows), str(movetime), str(depth), '\n']))
                # no return code to parse
                
            # displayables
            self.selected_img = Solid(COLOR_SELECTED, xsize=LOC_LEN, ysize=LOC_LEN)
            self.legal_dst_img = Solid(COLOR_LEGAL_DST, xsize=LOC_LEN, ysize=LOC_LEN)
            self.highlight_img = Solid(COLOR_PREV_MOVE, xsize=LOC_LEN, ysize=LOC_LEN)
            self.piece_imgs = self.load_piece_imgs()

            # coordinate tuples for blitting selected loc and generating moves
            self.src_coord = None
            # a list of legal destinations for the currently selected piece
            self.legal_dsts = []
            # highlight the two squares involved in the previous move
            self.highlighted_squares = []

            # if True, show promotion UI screen
            self.show_promotion_ui = False
            self.promotion = None

            self.game_status = None
            # return to _return in script, could be chess.WHITE, chess.BLACK, or, None
            self.winner = None # None for stalemate

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)

            # render selected loc
            if self.src_coord:
                render.place(self.selected_img, 
                    x=self.src_coord[0], y=self.src_coord[1], 
                    width=LOC_LEN, height=LOC_LEN)

            # render a list legal moves for the selected piece on loc
            for file_idx, rank_idx in self.legal_dsts:
                square_coord = indices_to_coord(file_idx, rank_idx, bottom_color=self.bottom_color)
                render.place(self.legal_dst_img, x=square_coord[0], y=square_coord[1])
            # render the highlighted move, represented as [(src_file, src_rank), (dst_file, dst_rank)]
            for file_idx, rank_idx in self.highlighted_squares:
                square_coord = indices_to_coord(file_idx, rank_idx, bottom_color=self.bottom_color)
                render.place(self.highlight_img, x=square_coord[0], y=square_coord[1])

            # render pieces on board
            for file_idx in range(INDEX_MIN, INDEX_MAX + 1):
                for rank_idx in range(INDEX_MIN, INDEX_MAX + 1):
                    # the symbol P, N, B, R, Q or K for white pieces or the lower-case variants for the black pieces
                    piece = self.get_piece_at(file_idx, rank_idx)
                    if piece in self.piece_imgs: # piece could be None
                        piece_coord = indices_to_coord(file_idx, rank_idx, bottom_color=self.bottom_color)
                        render.place(self.piece_imgs[piece], 
                            x=piece_coord[0], y=piece_coord[1])

            renpy.restart_interaction() # force refresh the screen

            return render

        def event(self, ev, x, y, st):
            # ignore clicks if the game has ended
            if self.game_status in [CHECKMATE, STALEMATE, DRAW]:
                return

            # skip GUI interaction for AI's turn in Player vs. AI mode
            if self.uses_stockfish and self.whose_turn != self.player_color:
                self.chess_subprocess.stdin.write('stockfish_move\n')
                move = self.chess_subprocess.stdout.readline().strip()
                self.make_move(move)
                return

            # XXX: in developer mode only, open up the UI for promotion or for claiming draw
            # in threefold repetition or fifty moves rule
            # https://en.wikipedia.org/wiki/Threefold_repetition
            # https://en.wikipedia.org/wiki/Fifty-move_rule
            # p: promotion, d: draw
            if config.developer:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_p]: # promotion
                    self.show_promotion_ui = not self.show_promotion_ui # toggle show or hide
                    renpy.restart_interaction()
                elif keys[pygame.K_c]: # claim draw
                    self.show_claim_draw_ui() # no need to specify if it's threefold or fifty-move

            # set by the flip board button
            if self.has_flipped_board:
                self.has_flipped_board = False
                # reset any selected piece
                self.src_coord = None
                self.legal_dsts = []
                renpy.redraw(self, 0)
                renpy.restart_interaction()

            # regular gameplay interaction
            if 0 < x < CHESS_SCREEN_HEIGHT and ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:

                # first click, check if loc is selectable
                if self.src_coord is None:
                    src_coord = round_coord(x, y)
                    src_file, src_rank = coord_to_square(src_coord, bottom_color=self.bottom_color)
                    # redraw if there is a piece of the current player's color on square
                    piece = self.get_piece_at(src_file, src_rank)
                    # white pieces are upper case, WHITE = True
                    # hence piece.color is equivalent to piece.isupper()
                    if piece and piece.isupper() == self.whose_turn:
                        self.src_coord = src_coord
                        # get legal destinations for redrawing
                        self.get_legal_dsts(src_file, src_rank)

                        if self.has_promoting_piece(src_file, src_rank):
                            self.show_promotion_ui = True
                            self.promotion = None

                        renpy.redraw(self, 0)

                # second click, check if should deselect
                else:
                    dst_coord = round_coord(x, y)
                    dst_file, dst_rank = coord_to_square(dst_coord, bottom_color=self.bottom_color)
                    src_file, src_rank = coord_to_square(self.src_coord, bottom_color=self.bottom_color)

                    # if player selects the same piece, deselect
                    if dst_file == src_file and dst_rank == src_rank:
                        self.src_coord = None
                        self.show_promotion_ui = False
                        self.legal_dsts = []
                        renpy.redraw(self, 0)
                        return

                    # if player selects a piece of their color, change selection to that piece
                    piece = self.get_piece_at(dst_file, dst_rank)
                    if piece and piece.isupper() == self.whose_turn:
                        # repeat code from first click
                        # change selection to the second-click piece
                        self.src_coord = dst_coord
                        src_file, src_rank = dst_file, dst_rank
                        self.get_legal_dsts(src_file, src_rank)  # get legal destinations for redrawing
                        # check if the piece is a promoting pawn
                        if self.has_promoting_piece(src_file, src_rank):
                            self.show_promotion_ui = True
                        else:
                            self.show_promotion_ui = False
                        self.promotion = None
                        renpy.redraw(self, 0)
                        return

                    # construct move uci and pass to subprocess to validate
                    move = construct_move_uci(src_file, src_rank, dst_file, dst_rank, promotion=self.promotion)

                    # needs promotion but the player hasn't select a piece to promote to
                    # if has promotion, len(move) should be 5, for ex, 'a7a8q'
                    if self.show_promotion_ui and len(move) == 4:
                        renpy.notify('Please select a piece type to promote to')

                    if move in self.get_legal_moves():
                        self.make_move(move)
                    # otherwise the piece selection remains unchanged
                    # waiting for the player to select a valid move
                       
        # helpers
        def load_piece_imgs(self):
            # white pieces represented as P, N, K, etc. and black p, n, k, etc.
            piece_imgs = {}

            for piece in PIECE_TYPES:
                white_path = os.path.join(CHESSPIECES_PATH, 'w' + piece + '.png')
                black_path = os.path.join(CHESSPIECES_PATH, 'b' + piece + '.png')
                white_piece, black_piece = piece.upper(), piece
                piece_imgs[white_piece] = Image(white_path)
                piece_imgs[black_piece] = Image(black_path)

            return piece_imgs

        def has_promoting_piece(self, file_idx, rank_idx):
            # check if the square identified by file and rank contains a promoting piece
            # i.e. a pawn on the second to last row, of the current player color
            piece = self.get_piece_at(file_idx, rank_idx)
            if not piece or not piece in ['p', 'P'] or not piece.isupper() == self.whose_turn:
                return False
            if piece.isupper(): # white
                return rank_idx == PROMOTION_RANK_WHITE
            else:
                return rank_idx == PROMOTION_RANK_BLACK

        def play_move_audio(self, move):
            if len(move) == 5: # has promotion
                renpy.sound.play(AUDIO_PROMOTION)
            else:
                # check subprocess to see if the move is a capture
                self.chess_subprocess.stdin.write('#'.join(['is_capture', move, '\n']))
                is_capture = eval(self.chess_subprocess.stdout.readline().strip())
                if is_capture:
                    renpy.sound.play(AUDIO_CAPTURE)
                else:
                    renpy.sound.play(AUDIO_MOVE)

        def check_game_status(self):
            """
            Check if is checkmate, in check, or stalemate
            and update status text display accordingly
            """
            self.chess_subprocess.stdin.write('game_status\n')
            self.game_status = int(self.chess_subprocess.stdout.readline().strip())
            # need is_checkmate and is_stalemate before is_check
            if self.game_status == CHECKMATE:
                renpy.sound.play(AUDIO_CHECKMATE)
                # after a move, if it's white's turn, that means black has
                # just moved and put white into checkmate, thus winner is black
                # hence need to negate self.whose_turn to get winner
                renpy.notify('Checkmate! The winner is %s' % ('black' if self.whose_turn else 'white'))
                self.winner = not self.whose_turn
                return

            if self.game_status == STALEMATE:
                renpy.sound.play(AUDIO_DRAW)
                renpy.notify('Stalemate')
                return

            # prompt player to claim draw if threefold or fifty-move occurs
            if self.game_status == THREEFOLD:
                self.show_claim_draw_ui(reason='Threefold repetition rule: ')
            if self.game_status == FIFTYMOVES:
                self.show_claim_draw_ui(reason='Fifty moves rule: ')

            # game resumes
            if self.game_status == INCHECK:
                renpy.sound.play(AUDIO_CHECK)

            else: # subprocess might have printed -1
                self.game_status = None

        def show_claim_draw_ui(self, reason=''):
            """
            reason: a string indicating the reason to claim the draw, directly prepended to message
            """
            renpy.show_screen('confirm', 
                message=reason + 'Would you like to claim draw?', 
                yes_action=[Hide('confirm'), Play('sound', AUDIO_DRAW),
                Function(self.kill_chess_subprocess), Return(DRAW)], 
                no_action=Hide('confirm'))
            renpy.restart_interaction()

        def add_highlight_move(self, move):
            src_file, src_rank, dst_file, dst_rank = move_uci_to_file_rank(move)
            self.highlighted_squares = [(src_file, src_rank), (dst_file, dst_rank)]

        # START function definitions that make call to helper functions that communicate with the subprocess
        def get_legal_dsts(self, src_file, src_rank):
            """
            filter the destination squares from the legal moves
            """
            self.legal_dsts = []
            legal_moves = self.get_legal_moves()
            for move in legal_moves:
                move_src_file, move_src_rank, move_dst_file, move_dst_rank = move_uci_to_file_rank(move)
                # the move originates from the current square
                if move_src_file == src_file and move_src_rank == src_rank:
                    self.legal_dsts.append((move_dst_file, move_dst_rank))

        def make_move(self, move):
            """
            1. play the corresponding move audio
            2. communicate the move to the subprocess
            3. highlight the src and dst squares of the move
            4. append the move to history
            5. 
            """
            self.play_move_audio(move)
            self.push_move(move)
            self.add_highlight_move(move)
            # for redrawing
            self.history.append(move)
            self.src_coord = None
            self.legal_dsts = []
            renpy.redraw(self, 0)

            self.check_game_status()
            self.show_promotion_ui = False
            self.promotion = None

        def undo_move(self):
            """
            inverse of make_move, proceed only if there is something in history
            1. play the audio for making a move
            2. communicate the undoing to the subprocess
            3. remove the move from the history      
            """
            if not self.history or (self.uses_stockfish and len(self.history) < 2):
                return
            renpy.sound.play(AUDIO_MOVE)
            if self.uses_stockfish: # PvC, undo two moves
                self.pop_move()
                self.pop_move()
                self.history.pop()
                self.history.pop()
            else: # PvP, undo one move
                self.pop_move()
                self.history.pop()
            # for redrawing
            self.src_coord = None
            self.legal_dsts = []
            self.highlighted_squares = []
            renpy.redraw(self, 0)

            self.check_game_status()
            self.show_promotion_ui = False
            self.promotion = None

        # END

        # helper functions for communicating with the subprocess
        def get_piece_at(self, file_idx, rank_idx):
            """
            return the symbol P, N, B, R, Q or K for white pieces or the lower-case variants for the black pieces
            """
            self.chess_subprocess.stdin.write('#'.join(['piece_at', str(file_idx), str(rank_idx), '\n']))
            piece = self.chess_subprocess.stdout.readline().strip()
            return piece if piece != 'None' else None

        def get_legal_moves(self):
            """
            return a list of legal moves
            """
            self.chess_subprocess.stdin.write('legal_moves\n')
            legal_moves = self.chess_subprocess.stdout.readline().strip().split('#')
            return legal_moves

        def push_move(self, move):
            # update board in the subprocess
            self.chess_subprocess.stdin.write('#'.join(['push_move', move, '\n']))
            # update whose_turn upon a valid move
            self.whose_turn = eval(self.chess_subprocess.stdout.readline().strip())

        def pop_move(self):
            """
            inverse of push_move, undo the last move
            """
            self.chess_subprocess.stdin.write('pop_move\n')
            # update whose_turn upon undoing
            self.whose_turn = eval(self.chess_subprocess.stdout.readline().strip())

        def kill_chess_subprocess(self):
            self.chess_subprocess.stdin.write('quit\n')

    # helper functions
    def coord_to_square(coord, bottom_color=WHITE):
        """
        bottom_color: if chess.BLACK, flip the coordinate calculation
        """
        x, y = coord
        if bottom_color == WHITE:
            file_idx = x / LOC_LEN
            rank_idx = INDEX_MAX - (y / LOC_LEN)
        else: # black on bottom_color
            file_idx = INDEX_MAX - x / LOC_LEN
            rank_idx = y / LOC_LEN
        return file_idx, rank_idx

    def indices_to_coord(file_idx, rank_idx, bottom_color=WHITE):
        assert INDEX_MIN <= file_idx <= INDEX_MAX and INDEX_MIN <= file_idx <= INDEX_MAX
        if bottom_color == WHITE:
            x = LOC_LEN * file_idx
            y = LOC_LEN * (INDEX_MAX - rank_idx)
        else: # black on bottom_color
            x = LOC_LEN * (INDEX_MAX - file_idx)
            y = LOC_LEN * rank_idx
        return (x, y)

    def round_coord(x, y):
        """
        for drawing, computes cursor coord rounded to the upperleft coord of the current loc
        """
        x_round = x / LOC_LEN * LOC_LEN
        y_round = y / LOC_LEN * LOC_LEN
        return (x_round, y_round)

    def square_to_file_rank(square):
        """
        has promotion if len(square) == 3
        """
        assert len(square) == 2 or len(square) == 3
        square = square[:2] # ignore promotion
        file_idx = ord(square[0]) - ord('a')
        rank_idx = int(square[1]) - 1
        return file_idx, rank_idx

    def move_uci_to_file_rank(move):
        """
        move uci looks like 'a7a8' or 'a7a8q'
        """
        src = move[:2]
        dst = move[2:]
        move_src_file, move_src_rank = square_to_file_rank(src)
        move_dst_file, move_dst_rank = square_to_file_rank(dst)
        return move_src_file, move_src_rank, move_dst_file, move_dst_rank

    def construct_move_uci(src_file_idx, src_rank_idx, dst_file_idx, dst_rank_idx, promotion=None):
        move = FILE_LETTERS[src_file_idx] + str(src_rank_idx + 1)
        move += FILE_LETTERS[dst_file_idx] + str(dst_rank_idx + 1)
        if promotion:
            move += promotion
        return move