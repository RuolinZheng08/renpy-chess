init python:

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
    
    class HoverDisplayable(renpy.Displayable):
        """
        Highlights the hovered loc in green
        """

        def __init__(self):
            super(HoverDisplayable, self).__init__()
            self.hover_coord = None
            self.hover_img = Solid(COLOR_HOVER, xsize=LOC_LEN, ysize=LOC_LEN)
            self.hover_img_render = None

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)
            if not self.hover_img_render:
                self.hover_img_render = renpy.render(self.hover_img, width, height, st, at)
            if self.hover_coord:
                render.blit(self.hover_img_render, self.hover_coord)
            return render

        def event(self, ev, x, y, st):
            if X_MIN < x < X_MAX and ev.type == pygame.MOUSEMOTION:
                self.hover_coord = round_cursor_coord(x, y)
                renpy.redraw(self, 0)

        def visit(self):
            return []

    class ChessDisplayable(renpy.Displayable):

        def __init__(self):
            super(ChessDisplayable, self).__init__()

            self.board = chess.Board()

            # displayables and renders
            self.selected_img = Solid(COLOR_SELECTED, xsize=LOC_LEN, ysize=LOC_LEN)
            self.selected_img_render = None

            self.piece_imgs = {}
            self.piece_img_renders = {}

            # coordinate tuples for blitting selected loc and generating moves
            self.src_coord = None
            self.dst_coord = None

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)
            if not self.selected_img_render:
                self.selected_img_render = renpy.render(self.selected_img, width, height, st, at)
            if self.src_coord:
                render.blit(self.selected_img_render, self.src_coord)
            return render

        def event(self, ev, x, y, st):
            pass
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # first click
                if self.src_coord is None:
                    self.src_coord = round_cursor_coord(x, y)
                    src_square = cursor_to_square(self.src_coord)
                    # redraw if there is a piece on square
                    if self.board.piece_at(src_square).color == self.board.turn:
                        # draws legal moves
                        renpy.redraw(self, 0)
                    else: # deselects
                        self.src_coord = None

                    # redraw if piece present and is player's turn, reset if None
                    piece = self.chessgame.board.get_at_loc(src_loc)
                    if piece and piece.player == self.chessgame.whose_turn():
                        self.moves_list_piece = self.chessgame.moves_piece(src_loc)
                        renpy.redraw(self, 0)
                    else:
                        self.src_coord = None
                # second click
                else:
                    self.dst_coord = cursor_round(x, y)
                    self.player_move = self.move_constructor()
                    ret = self.chessgame.apply_move(self.player_move)
                    if ret:
                        # Deactivate highlight for AI's turn
                        self.hover_coord = None
                        self.player_text = Text("Whose turn: %s" % self.chessgame.whose_turn(), color='#fff', size=26)
                        renpy.redraw(self, 0)
                    # Reset two clicks and moves list
                    self.src_coord, self.dst_coord = None, None
                    self.moves_list_piece = []

        def visit(self):
            return []

    # helper functions
    def cursor_to_square(x, y):
        assert X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX


    def round_cursor_coord(x, y):
      '''
      for drawing, computes cursor position rounded to the upperleft coord of the current loc
      '''
      assert X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX
      x_round = (x - X_OFFSET) / LOC_LEN * LOC_LEN + X_OFFSET
      y_round = y / LOC_LEN * LOC_LEN
      return (x_round, y_round)