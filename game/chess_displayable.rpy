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
    COLOR_LEGAL = '#45b8ff88' # legal move

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
            self.piece_imgs = self.load_piece_imgs()

            # coordinate tuples for blitting selected loc and generating moves
            self.src_coord = None
            self.dst_coord = None

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
                        # draws legal moves
                        renpy.redraw(self, 0)
                    else: # deselect
                        self.src_coord = None

                # second click, check if should deselect
                else:
                    self.dst_coord = round_coord(x, y)
                    move = self.construct_move(self.src_coord, self.dst_coord)
                    self.board.push(move)

                    self.src_coord, self.dst_coord = None, None
                    # self.moves_list_piece = []

        def visit(self):
            return []

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
            return chess.Move(from_square, to_square, promotion=None)

    # helper functions
    def coord_to_square(coord):
        x, y = coord
        assert X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX
        file_idx = (x - X_LEFT_OFFSET) / LOC_LEN
        rank_idx = INDEX_MAX - (y / LOC_LEN)
        return chess.square(file_idx, rank_idx)

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
        y = LOC_LEN * rank_idx
        return (x, y)