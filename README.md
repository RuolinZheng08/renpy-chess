# Ren'Py Chess Engine 2.0

## About

This is a chess GUI built with the [Ren'Py](http://renpy.org/) Visual Novel Engine, [python-chess](https://github.com/niklasf/python-chess), and [Stockfish](https://stockfishchess.org/) (for chess AI). You can use it as a standalone playable or integrate it as a minigame into a Ren'Py visual novel project. Read the [guide for integration](https://github.com/RuolinZheng08/renpy-chess#guide-for-integrating-into-a-renpy-project) below.

### Compatibility
This git branch `renpy-7.3.5` of the project provides support for **Ren'Py SDK <=7.3.5**. It doesn't support Ren'Py 7.4.0 due to the complications Ren'Py 7.4.0 introduced for the purpose of bridging Python 2 and 3. This branch will no longer receive new feature updates. New feature updates will be on the `master` branch which supports **Ren'Py SDK >= 7.4.0**.

### Gameplay Example: Fool's Mate
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/renpy-7.3.5/foolsmate.gif" alt="Gameplay Example" width=600>

## Differences between Ren'Py Chess 1.0 and Ren'Py Chess 2.0

|   | Pros  | Cons  |
|---|---|---|
| [Ren'Py Chess 1.0](https://github.com/RuolinZheng08/renpy-chess-engine)  | <ul><li>Has no Python package dependency hence supports any OS: Windows, Mac, Linux, Android, iOS, and even Web browser-play</li></ul> | <ul><li>Does not support en passant, castling, or promotion</li> <li>Does not support claiming a draw for the threefold repetition or the fifty-move rule</li> <li>Player can only play as White in Player vs. Computer</li> <li>Uses a chess AI of minimal implementation with no support for customizing the strength of the AI</li></ul>   |
| [Ren'Py Chess 2.0](https://github.com/RuolinZheng08/renpy-chess)  | <ul><li>Has full support for en passant and castling, plus a special UI for promotion</li> <li>Has full support and a special UI for claiming a draw for the threefold repetition or the fifty-move rule</li> <li>Supports flipping board view</li> <li>Uses Stockfish and supports customization of the strength (thinking time, depth) of the chess AI</li></ul>  | <ul><li>Only tested on Mac and Windows. Does not support iOS or Web. If you are on other OS (Linux, Android) and encounter a problem, please submit a GitHub issue</li> </ul>  |

## Gameplay

The game supports **Player vs. Player** and **Player vs. Computer**. In PvC, player can choose to play as either Black or White.

Click on a piece and all of its available moves will be highlighted in blue. Click on any of the legal destination squares to make a move. Press `Flip board view` to flip the view, with White on the bottom by default.

#### Flip Board View
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/renpy-7.3.5/flip_board.gif" alt="Flip Board" width=600>

#### Promotion UI
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/renpy-7.3.5/promotion.gif" alt="Promotion" width=600>

#### Stalemate
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/renpy-7.3.5/stalemate.gif" alt="Stalemate" width=600>

#### Player vs. Computer (Stockfish)
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/renpy-7.3.5/pvc.gif" alt="Play vs Computer" width=600>

#### Threefold Repetition: UI for Claiming a Draw
(Also shows a similar UI choice screen if the fifty-move rule is in effect)
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/renpy-7.3.5/threefold.gif" alt="Threefold Repetition" width=600>

## Guide for Integrating into a Ren'Py Project

The core class is a [Ren'Py Creator-Defined Displayable](https://www.renpy.org/doc/html/udd.html) named `ChessDisplayable` inside `game/chess_displayable.rpy`. The core screen takes several parameters, `game/chess_displayable.rpy`.

### Instructions

Copy the following files into your `game/` directory:
- The [Python modules](https://github.com/RuolinZheng08/renpy-chess/tree/master/game/python-packages) inside `game/python-packages`
- The [Stockfish binaries](https://github.com/RuolinZheng08/renpy-chess/tree/master/game/bin) in `game/bin`
- The image files `game/images/chesspieces` and `game/images/chessboard.png`
- The audio files for piece moves in `game/audio`
- The script file `game/chess_displayable.rpy`

In your `script.rpy`, pass the following configuration variables for the chess engine to the chess screen defined as `screen chess(fen, player_color, movetime, depth)`:

- `fen`: the [Forsyth–Edwards Notation](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation) of the board
- `player_color`: `None` for PvP. For PvC, `chess.WHITE` or `chess.BLACK`.
- `movetime`: `None` for PvP. For PvC, between `0` and `MAX_MOVETIME = 3000` milliseconds.
- `depth`: `None` for PvP. For PvC, between `0` and `MAX_DEPTH = 20`.

To call the chess displayable screen:

```renpy
window hide
$ quick_menu = False

$ fen = chess.STARTING_FEN
call screen chess(fen, player_color, movetime, depth)

$ quick_menu = True
window show
```

A complete example is as follows. Also see the `script.rpy` file in this repo.

```renpy
define e = Character("Eileen")

menu:
    "Please select the game mode."

    "Player vs. Player":
        $ player_color = None # None for Player vs. Player
        $ movetime = None
        $ depth = None

    "Player vs. Computer":
        $ movetime = 2000
        $ depth = 10

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
```

### Customizations for Different Difficulty Levels

The strength of the compuer player can be customized by setting the `depth` parameter between the range of 1 and 20, with a larger number indicating more strength. See [Stockfish depth to ELO conversion](https://chess.stackexchange.com/a/8125).

### Customizations for Different Screen Sizes, Colors, Styles, and Audios

Override the defaults in `chess_displayable.rpy` and replace the default chess piece and chess board images, or, audio files in `game/images` and `game/audio`.

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

## Contribution
Please feel free to submit GitHub issues and PRs. You are also more than welcome to join the Trello board if you are interested!

## Asset Credits

- Chess image: Photo by <a href="https://unsplash.com/@neon845b?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Jani Kaasinen</a> on <a href="https://unsplash.com/s/photos/chess?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a>. Resized and cropped to fit the screen.
- Chess background: [Chess - Wikipedia](https://images.app.goo.gl/MNkrhBteWb7VpPGN7)
- [Chess pieces](https://github.com/ljordan51/ChessGame/tree/master/pieces)
