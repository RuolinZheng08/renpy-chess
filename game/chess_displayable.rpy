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

    X_OFFSET = 280
    # use loc to mean UI square and distinguish from logical square
    LOC_LEN = 90 # length of one side of a loc

    COLOR_HOVER = '#00ff0050'
    COLOR_SELECTED = '#0a82ff88'
    COLOR_LEGAL = '#45b8ff88' # legal move

    # use tuples for immutability
    PIECE_TYPES = ('pawn', 'bishop', 'knight', 'rook', 'king', 'queen')
    SHORT_HANDS = ('p', 'r', 'b', 'n', 'k', 'q')

    
    class HoverDisplayable(renpy.Displayable):
        """
        Highlights the hovered loc in green
        """

        def __init__(self):
            super(HoverDisplayable, self).__init__()
            self.hover_coord = None
            self.hover_img = Solid(COLOR_HOVER, xsize=LOC_LEN, ysize=LOC_LEN)
            self.hover_render = None

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)
            if not self.hover_render:
                self.hover_render = renpy.render(self.hover_img, width, height, st, at)
            if self.hover_coord:
                render.blit(self.hover_render, self.hover_coord)
            return render

        def event(self, ev, x, y, st):
            if X_MIN < x < X_MAX and ev.type == pygame.MOUSEMOTION:
                self.hover_coord = round_coord(x, y)
                renpy.redraw(self, 0)

    class LocDisplayable(renpy.Displayable):
        def __init__(self, piece_render=None, piece_coord=None):
            self.piece_render = piece_render
            self.piece_coord = piece_coord

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)
            if self.piece_render:
                render.blit(self.piece_render, self.piece_coord)
            return render

    class ChessDisplayable(renpy.Displayable):

        def __init__(self):
            super(ChessDisplayable, self).__init__()

            self.board = chess.Board()

            # displayables and renders
            self.selected_img = Solid(COLOR_SELECTED, xsize=LOC_LEN, ysize=LOC_LEN)
            self.selected_render = None

            self.piece_imgs = {}
            self.piece_renders = {}

            # coordinate tuples for blitting selected loc and generating moves
            self.src_coord = None
            self.dst_coord = None

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)
            if not self.selected_render:
                self.selected_render = renpy.render(self.selected_img, width, height, st, at)
            if self.src_coord:
                render.blit(self.selected_render, self.src_coord)

            # test
            piece = Image('images/chesspieces/king_white.png')
            pr = renpy.render(piece, width, height, st, at)
            render.blit(pr, (X_OFFSET, 0))

            return render

        def event(self, ev, x, y, st):
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # first click, check if loc is selectable
                if self.src_coord is None:
                    self.src_coord = round_coord(x, y)
                    src_square = coord_to_square(*self.src_coord)
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
                    try:
                        self.board.push(move)
                    except ValueError:
                        pass

                    self.src_coord, self.dst_coord = None, None
                    # self.moves_list_piece = []

        def visit(self):
            return []

        # helpers
        def construct_piece_imgs(self):
            piece_imgs = {}
            return piece_imgs

        def construct_move(self, src_coord, dst_coord):
            assert src_coord and dst_coord
            from_square = coord_to_square(src_coord)
            to_square = coord_to_square(dst_coord)
            # TODO: promotion
            return chess.Move(from_square, to_square, promotion=None)

    # helper functions
    def coord_to_square(x, y):
        assert X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX
        file_index = (x - X_OFFSET) / LOC_LEN
        rank_index = 7 - (y / LOC_LEN)
        return chess.square(file_index, rank_index)

    def round_coord(x, y):
      '''
      for drawing, computes cursor coord rounded to the upperleft coord of the current loc
      '''
      assert X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX
      x_round = (x - X_OFFSET) / LOC_LEN * LOC_LEN + X_OFFSET
      y_round = y / LOC_LEN * LOC_LEN
      return (x_round, y_round)