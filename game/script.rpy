# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")

# The game starts here.

label start:
    python:
        import chess
        player_color = None # None for Player vs. Player
        movetime = None
        depth = None

    scene bg room
    e "Welcome to the Ren'Py Chess Game!"

    menu:
        "Please select the game mode."

        "Player vs. Player":
            pass

        "Player vs. Computer":
            $ movetime = 2000
            $ depth = 10

            menu:
                "Please select Player color"

                "White":
                    $ player_color = chess.WHITE

                "Black":
                    $ player_color = chess.BLACK

    window hide
    $ quick_menu = False

    call screen chess

    $ quick_menu = True
    window show

    if _return == 'white':
        e 'white won'
    elif _return == 'black':
        e 'black won'
    elif _return == 'draw':
        e 'game ended in a draw'

    return
