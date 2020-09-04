# Ren'Py Chess Engine 2.0

## About

This is a chess GUI built with the [Ren'Py](http://renpy.org/) Visual Novel Engine, [python-chess](https://github.com/niklasf/python-chess), and [Stockfish](https://stockfishchess.org/) (for chess AI). You can use it as a standalone playable or integrate it as a minigame into a Ren'Py visual novel project. Read the [guide for integration](https://github.com/RuolinZheng08/renpy-chess#guide-for-integrating-into-a-renpy-project) below.

#### Gameplay Example: Fool's Mate
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/master/foolsmate.gif" alt="Gameplay Example" width=600>

## Differences between Ren'Py Chess 1.0 and Ren'Py Chess 2.0

|   | Pros  | Cons  |
|---|---|---|
| [Ren'Py Chess 1.0](https://github.com/RuolinZheng08/renpy-chess-engine)  | <ul><li>Has no Python package dependency hence supports any OS: Windows, Mac, Linux, Android, iOS, and even Web browser-play</li></ul> | <ul><li>Does not support en passant, castling, or promotion</li> <li>Does not support claiming a draw for the threefold repetition or the fifty-move rule</li> <li>Player can only play as White in Player vs. Computer</li> <li>Uses a chess AI of minimal implementation with no support for customizing the strength of the AI</li></ul>   |
| [Ren'Py Chess 2.0](https://github.com/RuolinZheng08/renpy-chess)  | <ul><li>Has full support for en passant and castling, plus a special UI for promotion</li> <li>Has full support and a special UI for claiming a draw for the threefold repetition or the fifty-move rule</li> <li>Supports flipping board view</li> <li>Uses Stockfish and supports customization of the strength (thinking time, depth) of the chess AI</li></ul>  | <ul><li>Only tested on Mac and Windows. Does not support iOS or Web. If you are on other OS (Linux, Android) and encounter a problem, please submit a GitHub issue</li> </ul>  |

## Gameplay

The game supports **Player vs. Player** and **Player vs. Computer**. In PvC, player can choose to play as either Black or White.

Click on a piece and all of its available moves will be highlighted in blue. Click on any of the legal destination squares to make a move. Press `Flip board view` to flip the view, with White on the bottom by default.

#### Flip Board View
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/master/flip_board.gif" alt="Flip Board" width=600>

#### Promotion UI
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/master/promotion.gif" alt="Promotion" width=600>

#### Stalemate
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/master/stalemate.gif" alt="Stalemate" width=600>

#### Player vs. Computer (Stockfish)
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/master/pvc.gif" alt="Play vs Computer" width=600>

#### Threefold Repetition: UI for Claiming a Draw
(Also shows a similar UI choice screen if the fifty-move rule is in effect)
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/master/threefold.gif" alt="Threefold Repetition" width=600>

## Guide for Integrating into a Ren'Py Project

The core class is a [Ren'Py Creator-Defined Displayable](https://www.renpy.org/doc/html/udd.html) named `ChessDisplayable` inside `game/chess_displayable.rpy`.

### Instructions

Copy the image files `game/images/chesspieces` and `game/images/chessboard.png` and the script file `game/chess_displayable.rpy` into your `game/` directory.

In your `script.rpy`, define the following configuration variables for the chess engine:

- `fen`: the [Forsyth–Edwards Notation](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation) of the board
- `player_color`: `None` for PvP. For PvC, `chess.WHITE` or `chess.BLACK`.
- `movetime`: `None` for PvP. For PvC, between `0` and `MAX_MOVETIME = 3000` milliseconds.
- `depth`: `None` for PvP. For PvC, between `0` and `MAX_DEPTH = 20`.

To call the chess displayable screen:

```renpy
window hide
$ quick_menu = False

call screen chess

$ quick_menu = True
window show
```

A complete example is as follows. Also see the `script.rpy` file in this repo.

```renpy
define e = Character("Eileen")
$ fen = chess.STARTING_FEN

menu:
    "Please select the game mode."

    "Player vs. Player":
        $ player_color = None # None for Player vs. Player
        $ bottom_color = None # white at the bottom of the screen by default
        $ movetime = None
        $ depth = None

    "Player vs. Computer":
        $ movetime = 2000
        $ depth = 10

        menu:
            "Please select Player color"

            "White":
                $ player_color = chess.WHITE
                $ bottom_color = chess.WHITE

            "Black":
                # board view flipped so that the player's color is at the bottom of the screen
                $ player_color = chess.BLACK
                $ bottom_color = chess.BLACK

window hide
$ quick_menu = False

call screen chess

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
```

### Customizations for Different Screen Sizes, Colors, Styles, and Audios

Override the defaults in `chess_displayable.rpy` and replace the default chess piece and chess board images, or, audio files.

```renpy
define LOC_LEN = 90 # length of one side of a loc

define COLOR_HOVER = '#00ff0050' # green
define COLOR_SELECTED = '#0a82ff88' # blue
define COLOR_LEGAL_DST = '#45c8ff50' # blue, destination of a legal move
define COLOR_WHITE = '#fff'

define AUDIO_MOVE = 'audio/move.wav'
define AUDIO_CAPTURE = 'audio/capture.wav'
define AUDIO_PROMOTION = 'audio/promotion.wav'
define AUDIO_CHECK = 'audio/check.wav'
define AUDIO_CHECKMATE = 'audio/checkmate.wav'
define AUDIO_DRAW = 'audio/draw.wav' # used for stalemate, threefold, fifty-move
define AUDIO_FLIP_BOARD = 'audio/flip_board.wav'
```

## Continuous Development
The project is under active maintenance and you can view its development status on this public [Trello board](https://trello.com/b/ip9YLSPa/renpy-chess). Please feel free to submit a GitHub issue for bugs and feature requests. The source code is expected to be used in a Ren'Py kinetic novel game, [The Wind at Dawn](https://madeleine-chai.itch.io/the-wind-at-dawn).
