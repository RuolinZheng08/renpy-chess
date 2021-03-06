﻿# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")

# The game starts here.

label start:
    scene bg room
    e "Welcome to the Ren'Py Chess Game!"
    $ fen = STARTING_FEN
    menu:
        "Please select the game mode."

        "Player vs. Player":
            $ player_color = None # None for Player vs. Player
            $ movetime = None
            $ depth = None

        "Player vs. Computer":
            $ movetime = 2000

            menu:
                "Please select a difficulty level"

                "Easy":
                    $ depth = 2

                "Medium":
                    $ depth = 6

                "Hard":
                    $ depth = 12

            menu:
                "Please select Player color"

                "White":
                    $ player_color = WHITE # this constant is defined in chess_displayable.rpy 

                "Black":
                    # board view flipped so that the player's color is at the bottom of the screen
                    $ player_color = BLACK

    window hide
    $ quick_menu = False

    # avoid rolling back and losing chess game state
    $ renpy.block_rollback()

    call screen chess(fen, player_color, movetime, depth)

    # avoid rolling back and entering the chess game again
    $ renpy.block_rollback()

    # restore rollback from this point on
    $ renpy.checkpoint()

    $ quick_menu = True
    window show

    if _return == DRAW:
        e "The game ended in a draw."
    else: # RESIGN or CHECKMATE
        $ winner = "White" if _return == WHITE else "Black"
        e "The winner is [winner]."
        if player_color is not None: # PvC
            if _return == player_color:
                e "Congratulations, player!"
            else:
                e "Better luck next time, player."

    return
