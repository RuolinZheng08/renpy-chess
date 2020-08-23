# Ren'Py Chess Engine 2.0

## About

This is a chess GUI built with [Ren'Py](http://renpy.org/), [python-chess](https://github.com/niklasf/python-chess), and [Stockfish](https://stockfishchess.org/) (for chess AI). You can use it as a standalone playable or integrate it as a minigame into a Ren'Py visual novel project. Read the [guide for integration](https://github.com/RuolinZheng08/renpy-chess-engine) below.

#### Gameplay Example: Fool's Mate
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/master/foolsmate.gif" alt="Gameplay Example" width=600>

## Differences between Ren'Py Chess 1.0 and Ren'Py Chess 2.0

|   | Pros  | Cons  |
|---|---|---|
| [Ren'Py Chess 1.0](https://github.com/RuolinZheng08/renpy-chess-engine)  |   |   |
| [Ren'Py Chess 2.0](https://github.com/RuolinZheng08/renpy-chess)  |   |   |

## Gameplay

The game supports **Player vs. Player** and **Player vs. Computer**. In PvC, player can choose to play as either Black or White.

Click on a piece and all of its available moves will be highlighted in blue. Click on any of the legal destination squares to make a move.

#### Promotion UI
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/master/promotion.gif" alt="Promotion" width=600>

#### Stalemate
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/master/stalemate.gif" alt="Stalemate" width=600>

#### Player vs. Computer (Stockfish)
<img src="https://github.com/RuolinZheng08/renpy-chess/blob/master/pvc.gif" alt="Play vs Computer" width=600>

## Guide for Integrating into a Ren'Py Project

The core class is a [Ren'Py Creator-Defined Displayable](https://www.renpy.org/doc/html/udd.html) named `ChessDisplayable` inside `game/chess_displayable.rpy`.