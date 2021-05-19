# Ren'Py Chess Engine 2.0

**Play it now on [itch.io](https://r3dhummingbird.itch.io/renpy-chess-game) or watch a [YouTube demo](https://www.youtube.com/watch?v=6RzCvwaFRL0)**

## About

This is a chess GUI built with the [Ren'Py](http://renpy.org/) Visual Novel Engine, [python-chess](https://github.com/niklasf/python-chess), and [Stockfish](https://stockfishchess.org/) (for chess AI). You can use it as a standalone playable or integrate it as a minigame into a Ren'Py visual novel project. Read the [guide for integration](https://github.com/RuolinZheng08/renpy-chess#guide-for-integrating-into-a-renpy-project) below.

### Compatibility
This chess engine supports **Ren'Py SDK >= 7.4.0**. It is not backward compatible with **Ren'Py SDK <= 7.3.5** due to reasons described in [this GitHub issue](https://github.com/RuolinZheng08/renpy-chess/issues/14). See the `renpy-7.3.5` branch for [an old version that is compatible with Ren'Py SDK 7.3.5](https://github.com/RuolinZheng08/renpy-chess/tree/renpy-7.3.5).

### Gameplay Example: Fool's Mate
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/master/gif-demo/foolsmate.gif" alt="Gameplay Example" width=600>

## Differences between Ren'Py Chess 1.0 and Ren'Py Chess 2.0

|   | Pros  | Cons  |
|---|---|---|
| [Ren'Py Chess 1.0](https://github.com/RuolinZheng08/renpy-chess-engine)  | <ul><li>Has no Python package dependency hence supports any OS: Windows, Mac, Linux, Android, iOS, and even Web browser-play</li></ul> | <ul><li>Does not support en passant, castling, or promotion</li> <li>Does not support claiming a draw for the threefold repetition or the fifty-move rule</li> <li>Player can only play as White in Player vs. Computer</li> <li>Uses a chess AI of minimal implementation with no support for customizing the strength of the AI</li></ul>   |
| [Ren'Py Chess 2.0 (This project)](https://github.com/RuolinZheng08/renpy-chess)  | <ul><li>Has full support for en passant and castling, plus a special UI for promotion</li> <li>Has full support and a special UI for claiming a draw for the threefold repetition or the fifty-move rule</li> <li>Supports flipping board view</li> <li>Uses Stockfish and supports customization of the strength (thinking time, depth) of the chess AI</li></ul>  | <ul><li>Only tested on Mac and Windows. Does not support iOS or Web. If you are on other OS (Linux, Android) and encounter a problem, please submit a GitHub issue</li> </ul>  |

## Gameplay

The game supports **Player vs. Player** and **Player vs. Computer**. In PvC, player can choose to play as either Black or White.

Click on a piece and all of its available moves will be highlighted. Click on any of the legal destination squares to make a move. Press `Flip board view` to flip the view, with White on the bottom by default.

### Feature List
- PvP and PvC
- Flip board view
- Resign
- Undo moves

#### Player vs. Computer (Stockfish)
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/master/gif-demo/pvc.gif" alt="Play vs Computer" width=600>

#### Flip Board View, Undo Moves, Resign
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/master/gif-demo/controls.gif" alt="Flip Board" width=600>

#### Promotion UI
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/master/gif-demo/promotion.gif" alt="Promotion" width=600>

#### Threefold Repetition: UI for Claiming a Draw
(Also shows a similar UI choice screen if the fifty-move rule is in effect)
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/master/gif-demo/threefold.gif" alt="Threefold Repetition" width=600>

## Guide for Integrating into a Ren'Py Project

All of the files essential to the chess engine are in `game/00-chess-engine`. Therefore, you only need to copy the entire `00-chess-engine` into your Ren'Py `game` directory.

The chess game is full-screen when the screen resolution is 1280x720, but is customizable to fit any screen sizes, as described in subsequent sections.

### Structure of `00-chess-engine`

```
00-chess-engine/
    - audio                         # chess game sound effects
    - bin                           # chess AI Stockfish binaries
    - images                        # chess board and piece images
    - python-packages               # Python libraries
    - chess_displayable.rpy         # core GUI class
    - chess_subprocess.py           # core logic class
```

The core GUI class is a [Ren'Py Creator-Defined Displayable](https://www.renpy.org/doc/html/udd.html) named `ChessDisplayable` inside `00-chess-engine/chess_displayable.rpy`. You can customize anything stylistic in `chess_displayable.rpy`, as described below in more details.

`00-chess-engine/chess_subprocess.py` is the underlying chess engine. Creating an instance of `ChessDisplayable` will launch `chess_subprocess.py` as a subprocess. You can make logical changes in `chess_subprocess.py` for your specific use cases if you are comfortable with subprocess programming.

In your Ren'Py script, for example, `script.rpy`, pass the following configuration variables for the chess engine to the chess screen defined as `screen chess(fen, player_color, movetime, depth)`:

- `fen`: the [Forsyth–Edwards Notation](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation) of the board
- `player_color`: `None` for PvP. For PvC, `chess.WHITE` or `chess.BLACK`.
- `movetime`: `None` for PvP. For PvC, between `0` and `MAX_MOVETIME = 3000` milliseconds.
- `depth`: `None` for PvP. For PvC, between `0` and `MAX_DEPTH = 20`.

To call the chess displayable screen: (Also see the `game/script.rpy` file in this repo.)

```renpy
define e = Character("Eileen")

window hide
$ quick_menu = False
# avoid rolling back and losing chess game state
$ renpy.block_rollback()

# launches an easy-level PvC where player plays as white
$ fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
call screen chess(fen=fen, player_color=WHITE, movetime=2000, depth=2)

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
```

### Customizations for Different Difficulty Levels

The strength of the compuer player can be customized by setting the `depth` parameter between the range of 1 and 20, with a larger number indicating more strength. See [Stockfish depth to ELO conversion](https://chess.stackexchange.com/a/8125).

### Customizations for Different Screen Sizes, Colors, Styles, and Audios

Override the defaults in `chess_displayable.rpy` and replace the default chess piece and chess board images, or, audio files in `00-chess-engine/images` and `00-chess-engine/audio`.

```renpy
# directory paths
# the path of the current directory within game/
define THIS_PATH = '00-chess-engine/'
define IMAGE_PATH = 'images/'
define AUDIO_PATH = 'audio/'
define BIN_PATH = 'bin/' # stockfish binaries
define CHESSPIECES_PATH = THIS_PATH + IMAGE_PATH + 'chesspieces/'

# file paths
define IMG_CHESSBOARD = THIS_PATH + IMAGE_PATH + 'chessboard.png'
define AUDIO_MOVE = THIS_PATH + AUDIO_PATH + 'move.wav'
define AUDIO_CAPTURE = THIS_PATH + AUDIO_PATH + 'capture.wav'
define AUDIO_PROMOTION = THIS_PATH + AUDIO_PATH + 'promotion.wav'
define AUDIO_CHECK = THIS_PATH + AUDIO_PATH + 'check.wav'
define AUDIO_CHECKMATE = THIS_PATH + AUDIO_PATH + 'checkmate.wav'
define AUDIO_DRAW = THIS_PATH + AUDIO_PATH + 'draw.wav' # used for resign, stalemate, threefold, fifty-move
define AUDIO_FLIP_BOARD = THIS_PATH + AUDIO_PATH + 'flip_board.wav'

# this chess game is full-screen when the game resolution is 1280x720
define CHESS_SCREEN_WIDTH = 1280
define CHESS_SCREEN_HEIGHT = 720

# use loc to mean UI square and distinguish from logical square
define LOC_LEN = 90 # length of one side of a loc

define COLOR_HOVER = '#90ee90aa' # HTML LightGreen
define COLOR_SELECTED = '#40e0d0aa' # Turquoise
define COLOR_LEGAL_DST = '#afeeeeaa' # PaleTurquoise
define COLOR_PREV_MOVE = '#6a5acdaa' # SlateBlue
define COLOR_WHITE = '#fff'
```

## Continuous Development
The project is under active maintenance and you can view its development status on this public [Trello board](https://trello.com/b/ip9YLSPa/renpy-chess). Please feel free to submit a GitHub issue for bugs and feature requests. I have helped to integrate this chess engine into an in-development kinetic novel, [The Wind at Dawn](https://madeleine-chai.itch.io/the-wind-at-dawn).

## Contribution
Please feel free to submit GitHub issues and PRs. You are also more than welcome to join the Trello board if you are interested.

## Asset Credits

- Chess image: Photo by <a href="https://unsplash.com/@neon845b?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Jani Kaasinen</a> on <a href="https://unsplash.com/s/photos/chess?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a>. Resized and cropped to fit the screen.
- Chess background: [Chess - Wikipedia](https://images.app.goo.gl/MNkrhBteWb7VpPGN7)
- [Chess pieces](https://github.com/ljordan51/ChessGame/tree/master/pieces)
