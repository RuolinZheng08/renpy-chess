# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")

# The game starts here.

label start:
    scene bg room
    e "Welcome to the Ren'Py Chess Game!"

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
                    $ player_color = chess.WHITE

                "Black":
                    # board view flipped so that the player's color is at the bottom of the screen
                    $ player_color = chess.BLACK

    window hide
    $ quick_menu = False

    $ fen = chess.STARTING_FEN
    call screen chess(fen, player_color, movetime, depth)

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
