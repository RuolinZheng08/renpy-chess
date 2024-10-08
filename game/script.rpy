﻿# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")

# THIS_PATH is defined in chess_displayable.rpy
# define THIS_PATH = '00-chess-engine/'
init python:
    # for importing libraries
    import_dir = os.path.join(renpy.config.gamedir, THIS_PATH, 'python-packages')
    # to prevent STOCKFISH_ENGINE from getting stored and pickled
    global_objects = {}

# The game starts here.

label start:
    scene bg room
    e "Welcome to the Ren'Py Chess Game!"

label chess_game:
    # board notation
    $ fen = STARTING_FEN
    $ global_objects['STOCKFISH_ENGINE'] = chess.engine.SimpleEngine.popen_uci(STOCKFISH, startupinfo=STARTUPINFO)

    menu:
        "Please select the game mode."

        "Player vs. Player":
            $ player_color = None # None for Player vs. Player
            $ depth = None

        "Player vs. Computer":
            # initialize other variables used by the stockfish engine in stockfish.go()
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
                    $ player_color = chess.WHITE # this constant is defined in chess_displayable.rpy 

                "Black":
                    # board view flipped so that the player's color is at the bottom of the screen
                    $ player_color = chess.BLACK

    window hide
    $ quick_menu = False

    # avoid rolling back and losing chess game state
    $ renpy.block_rollback()

    # disable Esc key menu to prevent the player from saving the game
    $ _game_menu_screen = None

    call screen chess(fen, player_color, depth)

    # re-enable the Esc key menu
    $ _game_menu_screen = 'save'

    # avoid rolling back and entering the chess game again
    $ renpy.block_rollback()

    # restore rollback from this point on
    $ renpy.checkpoint()

    # kill stockfish engine
    $ quit_stockfish()

    $ quick_menu = True
    window show

    if _return == DRAW:
        e "The game ended in a draw."
    else: # RESIGN or CHECKMATE
        $ winner = "White" if _return == chess.WHITE else "Black"
        e "The winner is [winner]."
        if player_color is not None: # PvC
            if _return == player_color:
                e "Congratulations, player!"
            else:
                e "Better luck next time, player."

    menu:
        "Would you like to play another game?"

        "Yes":
            jump chess_game

        "No":
            pass

    return
