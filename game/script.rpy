# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")

# The game starts here.

label start:
    scene bg room
    e "Welcome to the Ren'Py Chess Game!"

    # board notation
    $ fen = STARTING_FEN

    menu:
        "Please select the game mode."

        "Player vs. Player":
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
                    $ player_color = WHITE # this constant is defined in chess_displayable.rpy 

                "Black":
                    # board view flipped so that the player's color is at the bottom of the screen
                    $ player_color = BLACK

    window hide
    $ quick_menu = False

    # initialize subprocess to communicate with the chess engine
    # THIS_PATH is defined in chess_displayable.rpy
    # define THIS_PATH = '00-chess-engine/'
    python:
        chess_script = os.path.join(renpy.config.gamedir, THIS_PATH, 'chess_subprocess.py')
        # for importing libraries
        import_dir = os.path.join(renpy.config.gamedir, THIS_PATH, 'python-packages')

        import subprocess # for communicating with the chess engine
        # other imports are in chess_displayable.rpy

        startupinfo = None
        if renpy.windows:      
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW

        # remember to kill this process after use to prevent memory leak
        chess_subprocess = subprocess.Popen(
            [sys.executable, chess_script, import_dir],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            startupinfo=startupinfo)

    # avoid rolling back and losing chess game state
    $ renpy.block_rollback()

    call screen chess(chess_subprocess, fen, player_color, movetime, depth)

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

    # kill the chess subprocess to prevent memory leak
    $ chess_subprocess.kill()

    return
