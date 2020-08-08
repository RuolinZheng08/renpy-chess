# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")
screen chess:
    default chess_displayble = ChessDisplayable()
    default hover_displayble = HoverDisplayable()
    # TODO: programmatically define the chess board background as an Image obj
    add "bg chessboard" # the bg doesn't need to be redraw every time
    add chess_displayble
    add hover_displayble # hover loc over chesspieces
    modal True

# The game starts here.

label start:
    
    e "hello"

    $ quick_menu = False
    call screen chess
    $ quick_menu = True

    return
