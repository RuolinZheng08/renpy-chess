# Ren'Py Chess Engine 2.0

**Play it now on [itch.io](https://r3dhummingbird.itch.io/renpy-chess-game) or watch a [YouTube demo](https://www.youtube.com/watch?v=6RzCvwaFRL0)**

## About

This is a chess GUI built with the [Ren'Py](http://renpy.org/) Visual Novel Engine, [python-chess](https://github.com/niklasf/python-chess), and [Stockfish](https://stockfishchess.org/) (for chess AI). You can use it as a standalone playable or integrate it as a minigame into a Ren'Py visual novel project. Read the [guide for integration](https://github.com/RuolinZheng08/renpy-chess#guide-for-integrating-into-a-renpy-project) below.

### Compatibility
This chess engine supports **Ren'Py 8**. It is not backward compatible with **Ren'Py 7**. See the other branches (ex. `renpy-7.4`, `renpy-7.3.5` for older Ren'Py versions)

### Gameplay Example: Fool's Mate
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/master/gif-demo/foolsmate.gif" alt="Gameplay Example" width=600>

## Differences between Ren'Py Chess 1.0 and Ren'Py Chess 2.0

|   | Pros  | Cons  |
|---|---|---|
| [Ren'Py Chess 1.0](https://github.com/RuolinZheng08/renpy-chess-engine)  | <ul><li>Has no Python package dependency hence supports any OS: Windows, Mac, Linux, Android, iOS, and even Web browser-play</li></ul> | <ul><li>Does not support en passant, castling, or promotion</li> <li>Does not support claiming a draw for the threefold repetition or the fifty-move rule</li> <li>Player can only play as White in Player vs. Computer</li> <li>Uses a chess AI of minimal implementation with no support for customizing the strength of the AI</li></ul>   |
| [Ren'Py Chess 2.0 (This project)](https://github.com/RuolinZheng08/renpy-chess)  | <ul><li>Has full support for en passant and castling, plus a special UI for promotion</li> <li>Has full support and a special UI for claiming a draw for the threefold repetition or the fifty-move rule</li> <li>Supports flipping board view</li> <li>Uses Stockfish and supports customization of the strength (thinking time, depth) of the chess AI</li></ul>  | <ul><li>Only tested on Mac and Windows. If you are on Linux and encounter a problem, please submit a GitHub issue. Does not support iOS, Android, or Web</li> </ul>  |

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

All files essential to the chess engine are in `game/00-chess-engine`. Therefore, you only need to copy the entire `00-chess-engine` into your Ren'Py `game` directory.

The chess game is full-screen when the screen resolution is 1280x720, but it is customizable to fit any screen size, as described in subsequent sections.

### Structure of `00-chess-engine`

```
00-chess-engine/
    - audio                         # chess game sound effects
    - bin                           # chess AI Stockfish binaries
    - images                        # chess board and piece images
    - python-packages               # Python libraries
    - chess_displayable.rpy         # core GUI class
```

The core GUI class is a [Ren'Py Creator-Defined Displayable](https://www.renpy.org/doc/html/udd.html) named `ChessDisplayable` inside `00-chess-engine/chess_displayable.rpy`.

In your Ren'Py script, for example, `script.rpy`, pass the following configuration variables for the chess engine to the chess screen defined as `screen chess(fen, player_color, movetime, depth)`:

- `fen`: the [Forsyth–Edwards Notation](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation) of the board
- `player_color`: `None` for PvP. For PvC, `chess.WHITE` or `chess.BLACK`.
- `movetime`: `None` for PvP. For PvC, between `0` and `MAX_MOVETIME = 3000` milliseconds.
- `depth`: `None` for PvP. For PvC, between `0` and `MAX_DEPTH = 20`.

**See `game/script.rpy` for an example that calls the chess displayable screen.**

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

## Asset Credits

- Chess image: Photo by <a href="https://unsplash.com/@neon845b?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Jani Kaasinen</a> on <a href="https://unsplash.com/s/photos/chess?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a>. Resized and cropped to fit the screen.
- Chess background: [Chess - Wikipedia](https://images.app.goo.gl/MNkrhBteWb7VpPGN7)
- [Chess pieces](https://github.com/ljordan51/ChessGame/tree/master/pieces)
