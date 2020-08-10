screen chess:
    default chess_displayble = ChessDisplayable()
    default hover_displayble = HoverDisplayable()
    # TODO: programmatically define the chess board background as an Image obj
    add "bg chessboard" # the bg doesn't need to be redraw every time
    add chess_displayble
    add hover_displayble # hover loc over chesspieces
    modal True
    if chess_displayble.winner:
        timer 6.0 action Return(chess_displayble.winner)

init python:

    # use UCI for move notations
    # cursor and coord may be used interchangably

    # https://python-chess.readthedocs.io/en/v0.23.10/
    import chess
    import pygame

    X_MIN = 280
    X_MAX = 1000
    Y_MIN = 0
    Y_MAX = 720

    X_LEFT_OFFSET = 280 # the horizontal offset to the left of the chessboard UI
    # use loc to mean UI square and distinguish from logical square
    LOC_LEN = 90 # length of one side of a loc

    # both file and rank index from 0 to 7
    INDEX_MIN, INDEX_MAX = 0, 7

    COLOR_HOVER = '#00ff0050'
    COLOR_SELECTED = '#0a82ff88'
    COLOR_LEGAL_DST = '#45b8ff88' # destination of a legal move
    COLOR_WHITE = '#fff'

    TEXT_SIZE = 26
    TEXT_WHOSETURN_COORD = (1020, 10)
    TEXT_STATUS_COORD = (1020, 50)

    # use tuples for immutability
    PIECE_TYPES = ('p', 'r', 'b', 'n', 'k', 'q')

    CHESSPIECES_PATH = 'images/chesspieces/'
    
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

        def __init__(self):
            super(ChessDisplayable, self).__init__()

            self.board = chess.Board()

            # displayables
            self.selected_img = Solid(COLOR_SELECTED, xsize=LOC_LEN, ysize=LOC_LEN)
            self.legal_dst_img = Solid(COLOR_LEGAL_DST, xsize=LOC_LEN, ysize=LOC_LEN)
            self.piece_imgs = self.load_piece_imgs()
            self.status_txt = None

            # coordinate tuples for blitting selected loc and generating moves
            self.src_coord = None
            # a list of legal destinations for the currently selected piece
            self.legal_dsts = []
            # return once a winner has been determined
            self.winner = None

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)
            # render pieces on board
            for square in chess.SQUARES:
                piece = self.board.piece_at(square)
                if piece:
                    piece_img = self.piece_imgs[piece.symbol()]
                    piece_coord = indices_to_coord(chess.square_file(square),
                                                    chess.square_rank(square))
                    render.place(piece_img, x=piece_coord[0], y=piece_coord[1])

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
            if X_MIN < x < X_MAX and ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # first click, check if loc is selectable
                if self.src_coord is None:
                    self.src_coord = round_coord(x, y)
                    src_square = coord_to_square(self.src_coord)
                    # redraw if there is a piece of the current player's color on square
                    piece = self.board.piece_at(src_square)
                    if piece and piece.color == self.board.turn:
                        # save legal destinations to be highlighted when redrawing render
                        self.legal_dsts = [move.to_square for move
                        in self.board.legal_moves if move.from_square == src_square]
                        renpy.redraw(self, 0)
                    else: # deselect
                        self.src_coord = None

                # second click, check if should deselect
                else:
                    dst_coord = round_coord(x, y)
                    move = self.construct_move(self.src_coord, dst_coord)
                    if move in self.board.legal_moves:
                        renpy.sound.play('audio/move.wav', channel=0)
                        self.board.push(move)
                        # check if is checkmate, in check, or stalemate
                        # need is_checkmate first b/c is_check implies is_checkmate
                        if self.board.is_checkmate():
                            self.status_txt = Text('Checkmate', 
                                color=COLOR_WHITE, size=TEXT_SIZE)
                            renpy.sound.play('audio/checkmate.wav', channel=1)
                            # after a move, if it's white's turn, that means black has
                            # just moved and put white into checkmate, thus winner is black
                            winner = 'black' if self.board.turn else 'white'
                            renpy.notify('Checkmate! The winner is %s' % winner)
                            self.winner = winner
                        elif self.board.is_check():
                            self.status_txt = Text('In Check', 
                                color=COLOR_WHITE, size=TEXT_SIZE)
                        elif self.board.is_stalemate():
                            self.status_txt = Text('Stalemate', 
                                color=COLOR_WHITE, size=TEXT_SIZE)
                            renpy.notify('Stalemate')
                            self.winner = 'draw'
                        else:
                            self.status_txt = None

                        renpy.redraw(self, 0)
                        
                    self.src_coord = None
                    self.legal_dsts = []

        # helpers
        def load_piece_imgs(self):
            # white pieces represented as P, N, K, etc. and black p, n, k, etc.
            piece_imgs = {}

            for piece in PIECE_TYPES:
                white_piece, black_piece = piece.upper(), piece
                white_path = CHESSPIECES_PATH + white_piece + '_white.png'
                black_path = CHESSPIECES_PATH + black_piece + '_black.png'
                piece_imgs[white_piece] = Image(white_path)
                piece_imgs[black_piece] = Image(black_path)

            return piece_imgs

        def construct_move(self, src_coord, dst_coord):
            assert src_coord and dst_coord
            from_square = coord_to_square(src_coord)
            to_square = coord_to_square(dst_coord)
            # TODO: promotion
            move = chess.Move(from_square, to_square, promotion=None)
            return move

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