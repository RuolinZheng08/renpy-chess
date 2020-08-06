init python:

    import chess

    class ChessDisplayable(renpy.Displayable):

        def __init__(self, *args, **kwargs):
            super(ChessDisplayable, self).__init__(*args, **kwargs)

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)
            return render

        def event(self, ev, x, y, st):

            import pygame


        def visit(self):
            return []

        # helpers
        