# BEGIN DEF

define X_MIN = 280
define X_MAX = 1000
define Y_MIN = 0
define Y_MAX = 720

define X_LEFT_OFFSET = 280 # the horizontal offset to the left of the chessboard UI

# use loc to mean UI square and distinguish from logical square
define LOC_LEN = 90 # length of one side of a loc

# both file and rank index from 0 to 7
define INDEX_MIN = 0
define INDEX_MAX = 7

define COLOR_HOVER = '#00ff0050'
define COLOR_SELECTED = '#0a82ff88'
define COLOR_LEGAL_DST = '#45c8ff50' # destination of a legal move
define COLOR_WHITE = '#fff'

define TEXT_SIZE = 26
define TEXT_WHOSETURN_COORD = (1020, 20)
define TEXT_STATUS_COORD = (1020, 60)

# use tuples for immutability
define PIECE_TYPES = ('p', 'r', 'b', 'n', 'k', 'q')

define PROMOTION_RANK_WHITE = 6 # INDEX_MAX - 1
define PROMOTION_RANK_BLACK = 1 # INDEX_MIN + 1

# file paths
define CHESSPIECES_PATH = 'images/chesspieces/'

define AUDIO_MOVE = 'audio/move.wav'
define AUDIO_CAPTURE = 'audio/capture.wav'
define AUDIO_PROMOTION = 'audio/promotion.wav'
define AUDIO_CHECK = 'audio/check.wav'
define AUDIO_CHECKMATE = 'audio/checkmate.wav'
define AUDIO_STALEMATE = 'audio/stalemate.wav'

define STOCKFISH = 'bin/stockfish-11-64'

# stockfish params
define MAX_MOVETIME = 3000 # max think time in millisec
define MAX_DEPTH = 20

# END DEF

# BEGIN DEFAULT

default fen = chess.STARTING_FEN
default chess_displayble = ChessDisplayable(fen=fen)

# END DEFAULT

# BEGIN STYLE # TODO: modify this

style promotion_piece is button
style promotion_piece_text is text:
    size 45
    hover_color "#00FFFF"             # Cyan
    outlines [ (0, "#0000FF", 1, 1) ] # Blue
    color "#FF0000"                   # Red

# END STYLE

# BEGIN SCREEN

screen select_promotion_screen:
    text "Select promotion piece type" xpos 25 ypos 45 color COLOR_WHITE size 16
    vbox xalign 0.09 ypos 80:
        textbutton "♜" action SetVariable('chess_displayble.promotion', chess.ROOK) style "promotion_piece"
        textbutton "♝" action SetVariable('chess_displayble.promotion', chess.BISHOP) style "promotion_piece"
        textbutton "♞" action SetVariable('chess_displayble.promotion', chess.KNIGHT) style "promotion_piece"
        textbutton "♛" action SetVariable('chess_displayble.promotion', chess.QUEEN) style "promotion_piece"

screen chess:
    default hover_displayble = HoverDisplayable()
    default chess_displayble = ChessDisplayable(fen=fen, 
        player_color=player_color, movetime=movetime, depth=depth)
    # TODO: programmatically define the chess board background as an Image obj
    add "bg chessboard" # the bg doesn't need to be redraw every time
    add chess_displayble
    add hover_displayble # hover loc over chesspieces
    if chess_displayble.is_gameover:
        timer 6.0 action Return(chess_displayble.winner)
    use select_promotion_screen

# END SCREEN

init python:

    # use UCI for move notations and FEN for board and move history
    # terms like cursor and coord, Stockfish and AI may be used interchangably

    # https://python-chess.readthedocs.io/en/v0.23.11/
    import chess
    import chess.uci
    import pygame
    import os
    
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
            if X_MIN < x < X_MAX and ev.type == pygame.MOUSEMOTION:
                self.hover_coord = round_coord(x, y)
                renpy.redraw(self, 0)                

    class ChessDisplayable(renpy.Displayable):
        """
        The main displayable for the chess minigame
        If player_color is None, use Player vs. Player mode
        Else, use Player vs. Stockfish mode
        player_color: None, chess.WHITE, chess.BLACK
        """
        def __init__(self, fen=chess.STARTING_FEN, player_color=None, movetime=2000, depth=10):
            super(ChessDisplayable, self).__init__()

            self.board = chess.Board(fen=fen)

            self.player_color = None
            if player_color is not None:
                self.player_color = player_color
                stockfish_path = os.path.abspath(os.path.join(config.basedir, 'game', STOCKFISH))
                self.stockfish = chess.uci.popen_engine(stockfish_path)
                self.stockfish.position(self.board)
                self.stockfish_movetime = movetime if movetime <= MAX_MOVETIME else MAX_MOVETIME
                self.stockfish_depth = depth if depth <= MAX_DEPTH else MAX_DEPTH
            else:
                self.stockfish = None

            # displayables
            self.selected_img = Solid(COLOR_SELECTED, xsize=LOC_LEN, ysize=LOC_LEN)
            self.legal_dst_img = Solid(COLOR_LEGAL_DST, xsize=LOC_LEN, ysize=LOC_LEN)
            self.piece_imgs = self.load_piece_imgs()
            self.status_txt = None

            # coordinate tuples for blitting selected loc and generating moves
            self.src_coord = None
            # a list of legal destinations for the currently selected piece
            self.legal_dsts = []

            # promotion piece type will be set by the buttons on select_promotion_screen
            self.promotion = None

            # set to True at checkmate or stalemate
            self.is_gameover = False
            # return to _return in script, could be chess.WHITE, chess.BLACK, or, None
            self.winner = None # None for stalemate

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)
            # render pieces on board
            for square in chess.SQUARES:
                piece = self.board.piece_at(square)
                if piece:
                    piece_img = self.piece_imgs[piece.symbol()]
                    piece_coord = indices_to_coord(chess.square_file(square),
                                                    chess.square_rank(square))
                    render.place(piece_img, 
                        x=piece_coord[0], y=piece_coord[1])

            # render selected loc
            if self.src_coord:
                render.place(self.selected_img, 
                    x=self.src_coord[0], y=self.src_coord[1], 
                    width=LOC_LEN, height=LOC_LEN)

            # render a list legal moves for the selected piece on loc
            for square in self.legal_dsts:
                square_coord = indices_to_coord(chess.square_file(square),
                                                chess.square_rank(square))
                render.place(self.legal_dst_img, x=square_coord[0], y=square_coord[1])

            # update text
            whoseturn_txt = Text('Whose turn: %s' %
                ('White' if self.board.turn else 'Black'), 
                color=COLOR_WHITE, size=TEXT_SIZE)
            render.place(whoseturn_txt, 
                x=TEXT_WHOSETURN_COORD[0], y=TEXT_WHOSETURN_COORD[1])

            if self.status_txt:
                render.place(self.status_txt, 
                    x=TEXT_STATUS_COORD[0], y=TEXT_STATUS_COORD[1])

            return render

        def event(self, ev, x, y, st):
            # skip GUI interaction for AI's turn in Player vs. AI mode
            if self.stockfish and self.board.turn != self.player_color:
                self.stockfish.position(self.board)
                move = self.stockfish.go(movetime=self.stockfish_movetime, 
                    depth=self.stockfish_depth)
                move = move.bestmove
                self.play_move_audio(move)

                self.board.push(move)
                renpy.redraw(self, 0) # redraw pieces

                self.check_game_status()
                return

            if X_MIN < x < X_MAX and ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # first click, check if loc is selectable
                if self.src_coord is None:
                    src_coord = round_coord(x, y)
                    src_square = coord_to_square(src_coord)
                    # redraw if there is a piece of the current player's color on square
                    piece = self.board.piece_at(src_square)
                    if piece and piece.color == self.board.turn:
                        self.src_coord = src_coord
                        # save legal destinations to be highlighted when redrawing render
                        self.legal_dsts = [move.to_square for move
                        in self.board.legal_moves if move.from_square == src_square]
                        renpy.redraw(self, 0)

                # second click, check if should deselect
                else:
                    dst_coord = round_coord(x, y)
                    dst_square = coord_to_square(dst_coord)
                    src_square = coord_to_square(self.src_coord)

                    # if player selects the same piece, deselect
                    if dst_square == src_square:
                        self.src_coord = None
                        self.legal_dsts = []
                        renpy.redraw(self, 0)
                        return

                    # if player selects a piece of their color, change selection to that piece
                    piece = self.board.piece_at(dst_square)
                    if piece and piece.color == self.board.turn: # repeat code from first click
                        self.src_coord = dst_coord
                        src_square = dst_square
                        # save legal destinations to be highlighted when redrawing render
                        self.legal_dsts = [move.to_square for move
                        in self.board.legal_moves if move.from_square == src_square]
                        renpy.redraw(self, 0)
                        return

                    # move construction
                    move = chess.Move(src_square, dst_square, promotion=self.promotion)
                    if self.has_promoting_piece(src_square) and not move.promotion:
                        # TODO: show/hide UI for selecting promotion
                        renpy.notify('Please select a piece type to promote to')

                    if move in self.board.legal_moves:
                        self.play_move_audio(move)

                        self.board.push(move)
                        self.src_coord = None
                        self.legal_dsts = []
                        renpy.redraw(self, 0)

                        self.check_game_status()


        # helpers
        def load_piece_imgs(self):
            # white pieces represented as P, N, K, etc. and black p, n, k, etc.
            piece_imgs = {}

            for piece in PIECE_TYPES:
                white_piece, black_piece = piece.upper(), piece
                white_path = CHESSPIECES_PATH + 'w' + white_piece + '.png'
                black_path = CHESSPIECES_PATH + 'b' + black_piece + '.png'
                piece_imgs[white_piece] = Image(white_path)
                piece_imgs[black_piece] = Image(black_path)

            return piece_imgs

        def has_promoting_piece(self, square):
            # check if the square contains a promoting piece
            # i.e. a pawn on the second to last row, of the current player color
            piece = self.board.piece_at(square)
            ret = (piece and piece.color == self.board.turn and
                piece.piece_type == chess.PAWN)
            if not ret:
                return False
            rank = chess.square_rank(square)
            if piece.color == chess.WHITE:
                return rank == PROMOTION_RANK_WHITE
            else:
                return rank == PROMOTION_RANK_BLACK

        def play_move_audio(self, move):
            if move.promotion:
                renpy.sound.play(AUDIO_PROMOTION)
            else:
                if self.board.is_capture(move):
                    renpy.sound.play(AUDIO_CAPTURE)
                else:
                    renpy.sound.play(AUDIO_MOVE)

        def check_game_status(self):
            """
            Check if is checkmate, in check, or stalemate
            and update status text display accordingly
            """
            # need is_checkmate first b/c is_check implies is_checkmate
            if self.board.is_checkmate():
                self.status_txt = Text('Checkmate', 
                    color=COLOR_WHITE, size=TEXT_SIZE)
                renpy.sound.play(AUDIO_CHECKMATE)
                renpy.redraw(self, 0)

                # after a move, if it's white's turn, that means black has
                # just moved and put white into checkmate, thus winner is black
                # hence need to negate self.board.turn to get winner
                renpy.notify('Checkmate! The winner is %s' % ('black' if self.board.turn else 'white'))
                self.winner = not self.board.turn
                self.is_gameover = True
                raise renpy.IgnoreEvent()

            elif self.board.is_check():
                self.status_txt = Text('In Check', 
                    color=COLOR_WHITE, size=TEXT_SIZE)
                renpy.sound.play(AUDIO_CHECK)
                renpy.redraw(self, 0)

            elif self.board.is_stalemate():
                self.status_txt = Text('Stalemate', 
                    color=COLOR_WHITE, size=TEXT_SIZE)
                renpy.sound.play(AUDIO_STALEMATE)
                renpy.redraw(self, 0)

                renpy.notify('Stalemate')
                self.winner = None
                self.is_gameover = True
                raise renpy.IgnoreEvent()

            else:
                self.status_txt = None

    # helper functions
    def coord_to_square(coord):
        x, y = coord
        assert X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX
        file_idx = (x - X_LEFT_OFFSET) / LOC_LEN
        rank_idx = INDEX_MAX - (y / LOC_LEN)
        square = chess.square(file_idx, rank_idx)
        return square

    def round_coord(x, y):
        '''
        for drawing, computes cursor coord rounded to the upperleft coord of the current loc
        '''
        assert X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX
        x_round = (x - X_LEFT_OFFSET) / LOC_LEN * LOC_LEN + X_LEFT_OFFSET
        y_round = y / LOC_LEN * LOC_LEN
        return (x_round, y_round)

    def indices_to_coord(file_idx, rank_idx):
        assert INDEX_MIN <= file_idx <= INDEX_MAX and INDEX_MIN <= file_idx <= INDEX_MAX
        x = LOC_LEN * file_idx + X_LEFT_OFFSET
        y = LOC_LEN * (INDEX_MAX - rank_idx)
        return (x, y)