# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")

init python:
    # stockfish engine is OS-dependent
    if renpy.android:
        STOCKFISH = 'bin/stockfish-10-armv7' # 32 bit
    elif renpy.ios:
        STOCKFISH = 'bin/stockfish-11-64' # FIXME: no iOS stockfish available
    elif renpy.linux:
        STOCKFISH = 'bin/stockfish_20011801_x64'
    elif renpy.macintosh:
        STOCKFISH = 'bin/stockfish-11-64'
    elif renpy.windows:
        STOCKFISH = 'bin/stockfish_20011801_x64.exe'

    # get the global absolute path of the stockfish engine binary
    stockfish_path = os.path.abspath(os.path.join(renpy.config.gamedir, STOCKFISH))

    startupinfo = None
    # stop stockfish from opening up shell
    # https://stackoverflow.com/a/63538680
    if renpy.windows:
        # the module subprocess should have already been imported
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW

    # IMPORTANT: this must be in an `init python` block, otherwise it will result in a pickle error
    stockfish = chess.uci.popen_engine(stockfish_path, startupinfo=startupinfo)
    # now we are ready to use the stockfish variable when constructing the minigame screen


# The game starts here.

label start:
    scene bg room
    e "Welcome to the Ren'Py Chess Game!"

    menu:
        "Please select the game mode."

        "Player vs. Player":
            $ stockfish = None # no need for AI
            $ player_color = None # None for Player vs. Player
            $ movetime = None
            $ depth = None

        "Player vs. Computer":
            # initialize other variables used by the stockfish engine in stockfish.go()
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
                    $ player_color = chess.WHITE

                "Black":
                    # board view flipped so that the player's color is at the bottom of the screen
                    $ player_color = chess.BLACK

    window hide
    $ quick_menu = False

    # avoid rolling back and losing chess game state
    $ renpy.block_rollback()

    # disable Esc key menu to prevent the player from saving the game
    $ _game_menu_screen = None

    $ fen = chess.STARTING_FEN
    call screen chess(stockfish, fen, player_color, movetime, depth)

    # re-enable the Esc key menu
    $ _game_menu_screen = 'save'

    # avoid rolling back and entering the chess game again
    $ renpy.block_rollback()

    # restore rollback from this point on
    $ renpy.checkpoint()

    $ quick_menu = True
    window show

    if _return == DRAW:
        e "The game ended in a draw."
    else:
        $ winner = "White" if _return == chess.WHITE else "Black"
        e "The winner is [winner]."
        if _return == player_color:
            e "Congratulations, player!"
        elif _return is not None:
            e "Better luck next time, player."

    return
