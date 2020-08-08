init python:

    import chess
    import pygame

    X_MIN = 280
    X_MAX = 1000
    Y_MIN = 0
    Y_MAX = 720

    X_OFFSET = 280
    LOC_SIZE = 90

    COLOR_HOVER = '#00ff0050'
    COLOR_SELECTED = '#0a82ff88'
    COLOR_LEGAL = '#45b8ff88' # legal move

    class ChessDisplayable(renpy.Displayable):

        def __init__(self, *args, **kwargs):
            super(ChessDisplayable, self).__init__(*args, **kwargs)

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)
            return render

        def event(self, ev, x, y, st):
            pass

        def visit(self):
            return []

        # helpers
    
    class HoverDisplayable(renpy.Displayable):

        def __init__(self, *args, **kwargs):
            super(HoverDisplayable, self).__init__(*args, **kwargs)
            # coordinate tuple for blitting
            self.hover_coord = None
            self.hover_img = Solid(COLOR_HOVER, xsize=LOC_SIZE, ysize=LOC_SIZE)
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
                self.hover_coord = round_cursor_to_loc(x, y)
                renpy.redraw(self, 0)

        def visit(self):
            return []

    # helper functions
    def round_cursor_to_loc(x, y):
      '''
      returns cursor position rounded to the upperleft coordinate of the current loc
      Args:
          x (int)
          y (int)
      Returns:
          (x_round, y_round) (tuple)
      '''
      assert X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX
      x_round = (x - X_OFFSET) / LOC_SIZE * LOC_SIZE + X_OFFSET
      y_round = y / LOC_SIZE * LOC_SIZE
      return (x_round, y_round)