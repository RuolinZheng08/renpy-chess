# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")

# The game starts here.

label start:
    
    e "hello"

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
