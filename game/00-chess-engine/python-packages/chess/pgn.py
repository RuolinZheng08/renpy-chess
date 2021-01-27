# -*- coding: utf-8 -*-
#
# This file is part of the python-chess library.
# Copyright (C) 2012-2018 Niklas Fiekas <niklas.fiekas@backscattering.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import chess
import collections
import itertools
import re
import logging

try:
    from collections.abc import MutableMapping  # Python 3
except ImportError:
    from collections import MutableMapping  # Python 2


LOGGER = logging.getLogger(__name__)


# Reference of Numeric Annotation Glyphs (NAGs):
# https://en.wikipedia.org/wiki/Numeric_Annotation_Glyphs

NAG_NULL = 0

NAG_GOOD_MOVE = 1
"""A good move. Can also be indicated by ``!`` in PGN notation."""

NAG_MISTAKE = 2
"""A mistake. Can also be indicated by ``?`` in PGN notation."""

NAG_BRILLIANT_MOVE = 3
"""A brilliant move. Can also be indicated by ``!!`` in PGN notation."""

NAG_BLUNDER = 4
"""A blunder. Can also be indicated by ``??`` in PGN notation."""

NAG_SPECULATIVE_MOVE = 5
"""A speculative move. Can also be indicated by ``!?`` in PGN notation."""

NAG_DUBIOUS_MOVE = 6
"""A dubious move. Can also be indicated by ``?!`` in PGN notation."""

NAG_FORCED_MOVE = 7
NAG_SINGULAR_MOVE = 8
NAG_WORST_MOVE = 9
NAG_DRAWISH_POSITION = 10
NAG_QUIET_POSITION = 11
NAG_ACTIVE_POSITION = 12
NAG_UNCLEAR_POSITION = 13
NAG_WHITE_SLIGHT_ADVANTAGE = 14
NAG_BLACK_SLIGHT_ADVANTAGE = 15
NAG_WHITE_MODERATE_ADVANTAGE = 16
NAG_BLACK_MODERATE_ADVANTAGE = 17
NAG_WHITE_DECISIVE_ADVANTAGE = 18
NAG_BLACK_DECISIVE_ADVANTAGE = 19

NAG_WHITE_ZUGZWANG = 22
NAG_BLACK_ZUGZWANG = 23

NAG_WHITE_MODERATE_COUNTERPLAY = 132
NAG_BLACK_MODERATE_COUNTERPLAY = 133
NAG_WHITE_DECISIVE_COUNTERPLAY = 134
NAG_BLACK_DECISIVE_COUNTERPLAY = 135
NAG_WHITE_MODERATE_TIME_PRESSURE = 136
NAG_BLACK_MODERATE_TIME_PRESSURE = 137
NAG_WHITE_SEVERE_TIME_PRESSURE = 138
NAG_BLACK_SEVERE_TIME_PRESSURE = 139

NAG_NOVELTY = 146


TAG_REGEX = re.compile(r"^\[([A-Za-z0-9_]+)\s+\"(.*)\"\]\s*$")

TAG_NAME_REGEX = re.compile(r"^[A-Za-z0-9_]+\Z")

MOVETEXT_REGEX = re.compile(r"""
    (
        [NBKRQ]?[a-h]?[1-8]?[\-x]?[a-h][1-8](?:=?[nbrqkNBRQK])?
        |[PNBRQK]?@[a-h][1-8]
        |--
        |Z0
        |O-O(?:-O)?
        |0-0(?:-0)?
    )
    |(\{.*)
    |(;.*)
    |(\$[0-9]+)
    |(\()
    |(\))
    |(\*|1-0|0-1|1/2-1/2)
    |([\?!]{1,2})
    """, re.DOTALL | re.VERBOSE)


TAG_ROSTER = ["Event", "Site", "Date", "Round", "White", "Black", "Result"]


class GameNode(object):

    def __init__(self):
        self.parent = None
        self.move = None
        self.nags = set()
        self.starting_comment = ""
        self.comment = ""
        self.variations = []

        self.board_cached = None

    def board(self, _cache=True):
        """
        Gets a board with the position of the node.

        It's a copy, so modifying the board will not alter the game.
        """
        if self.board_cached:
            return self.board_cached.copy()

        board = self.parent.board(_cache=False)
        board.push(self.move)

        if _cache:
            self.board_cached = board
            return board.copy()
        else:
            return board

    def san(self):
        """
        Gets the standard algebraic notation of the move leading to this node.
        See :func:`chess.Board.san()`.

        Do not call this on the root node.
        """
        return self.parent.board().san(self.move)

    def uci(self, chess960=None):
        """
        Gets the UCI notation of the move leading to this node.
        See :func:`chess.Board.uci()`.

        Do not call this on the root node.
        """
        return self.parent.board().uci(self.move, chess960=chess960)

    def root(self):
        """Gets the root node, i.e. the game."""
        node = self

        while node.parent:
            node = node.parent

        return node

    def end(self):
        """Follows the main variation to the end and returns the last node."""
        node = self

        while node.variations:
            node = node.variations[0]

        return node

    def is_end(self):
        """Checks if this node is the last node in the current variation."""
        return not self.variations

    def starts_variation(self):
        """
        Checks if this node starts a variation (and can thus have a starting
        comment). The root node does not start a variation and can have no
        starting comment.

        For example in ``1. e4 e5 (1... c5 2. Nf3) 2. Nf3`` the node holding
        1... c5 starts a variation.
        """
        if not self.parent or not self.parent.variations:
            return False

        return self.parent.variations[0] != self

    def is_main_line(self):
        """Checks if the node is in the main line of the game."""
        node = self

        while node.parent:
            parent = node.parent

            if not parent.variations or parent.variations[0] != node:
                return False

            node = parent

        return True

    def is_main_variation(self):
        """
        Checks if this node is the first variation from the point of view of its
        parent. The root node is also in the main variation.
        """
        if not self.parent:
            return True

        return not self.parent.variations or self.parent.variations[0] == self

    def variation(self, move):
        """
        Gets a child node by either the move or the variation index.
        """
        for index, variation in enumerate(self.variations):
            if move == variation.move or index == move or move == variation:
                return variation

        raise KeyError("variation not found")

    def has_variation(self, move):
        """Checks if the given *move* appears as a variation."""
        return move in (variation.move for variation in self.variations)

    def promote_to_main(self, move):
        """Promotes the given *move* to the main variation."""
        variation = self.variation(move)
        self.variations.remove(variation)
        self.variations.insert(0, variation)

    def promote(self, move):
        """Moves a variation one up in the list of variations."""
        variation = self.variation(move)
        i = self.variations.index(variation)
        if i > 0:
            self.variations[i - 1], self.variations[i] = self.variations[i], self.variations[i - 1]

    def demote(self, move):
        """Moves a variation one down in the list of variations."""
        variation = self.variation(move)
        i = self.variations.index(variation)
        if i < len(self.variations) - 1:
            self.variations[i + 1], self.variations[i] = self.variations[i], self.variations[i + 1]

    def remove_variation(self, move):
        """Removes a variation."""
        self.variations.remove(self.variation(move))

    def add_variation(self, move, comment="", starting_comment="", nags=()):
        """Creates a child node with the given attributes."""
        node = GameNode()
        node.move = move
        node.nags = set(nags)
        node.parent = self
        node.comment = comment
        node.starting_comment = starting_comment
        self.variations.append(node)
        return node

    def add_main_variation(self, move, comment=""):
        """
        Creates a child node with the given attributes and promotes it to the
        main variation.
        """
        node = self.add_variation(move, comment=comment)
        self.variations.remove(node)
        self.variations.insert(0, node)
        return node

    def main_line(self):
        """Yields the moves of the main line starting in this node."""
        node = self
        while node.variations:
            node = node.variations[0]
            yield node.move

    def add_line(self, moves, comment="", starting_comment="", nags=()):
        """
        Creates a sequence of child nodes for the given list of moves.
        Adds *comment* and *nags* to the last node of the line and returns it.
        """
        node = self

        # Add line.
        for move in moves:
            node = node.add_variation(move, starting_comment=starting_comment)
            starting_comment = ""

        # Merge comment and NAGs.
        if node.comment:
            node.comment += " " + comment
        else:
            node.comment = comment

        node.nags.update(nags)

        return node

    def accept(self, visitor, _board=None):
        """
        Traverse game nodes in PGN order using the given *visitor*. Returns
        the visitor result.
        """
        board = self.board() if _board is None else _board

        # The first move of the main line goes first.
        if self.variations:
            main_variation = self.variations[0]
            visitor.visit_move(board, main_variation.move)

            # Visit NAGs.
            for nag in sorted(main_variation.nags):
                visitor.visit_nag(nag)

            # Visit the comment.
            if main_variation.comment:
                visitor.visit_comment(main_variation.comment)

        # Then visit side lines.
        for variation in itertools.islice(self.variations, 1, None):
            # Start variation.
            visitor.begin_variation()

            # Append starting comment.
            if variation.starting_comment:
                visitor.visit_comment(variation.starting_comment)

            # Visit move.
            visitor.visit_move(board, variation.move)

            # Visit NAGs.
            for nag in sorted(variation.nags):
                visitor.visit_nag(nag)

            # Visit comment.
            if variation.comment:
                visitor.visit_comment(variation.comment)

            # Recursively append the next moves.
            board.push(variation.move)
            variation.accept(visitor, _board=board)
            board.pop()

            # End variation.
            visitor.end_variation()

        # The main line is continued last.
        if self.variations:
            main_variation = self.variations[0]

            # Recursively append the next moves.
            board.push(main_variation.move)
            main_variation.accept(visitor, _board=board)
            board.pop()

        # Get the result if not called recursively.
        if _board is None:
            return visitor.result()

    def accept_subgame(self, visitor):
        """
        Traverses headers and game nodes in PGN order, as if the game was
        starting from this node. Returns the visitor result.
        """
        game = self.root()
        visitor.begin_game()

        dummy_game = Game.without_tag_roster()
        dummy_game.setup(self.board())

        visitor.begin_headers()
        for tagname, tagvalue in game.headers.items():
            if tagname not in dummy_game.headers:
                visitor.visit_header(tagname, tagvalue)
        for tagname, tagvalue in dummy_game.headers.items():
            visitor.visit_header(tagname, tagvalue)
        visitor.end_headers()

        self.accept(visitor)

        visitor.visit_result(game.headers.get("Result", "*"))
        visitor.end_game()
        return visitor.result()

    def __str__(self):
        return self.accept(StringExporter(columns=None))


class Game(GameNode):
    """
    The root node of a game with extra information such as headers and the
    starting position. Also has all the other properties and methods of
    :class:`~chess.pgn.GameNode`.
    """

    def __init__(self, headers=None):
        super(Game, self).__init__()
        self.headers = Headers(headers)
        self.errors = []

    def board(self, _cache=False):
        """
        Gets the starting position of the game.

        Unless the ``FEN`` header tag is set, this is the default starting
        position (for the ``Variant``).
        """
        chess960 = self.headers.get("Variant", "").lower() in [
            "chess960",
            "chess 960",
            "fischerandom",  # Cute Chess
            "fischerrandom"]

        # http://www.freechess.org/Help/HelpFiles/wild.html
        wild = self.headers.get("Variant", "").lower() in [
            "wild/0", "wild/1", "wild/2", "wild/3", "wild/4", "wild/5",
            "wild/6", "wild/7", "wild/8", "wild/8a"]

        if chess960 or wild or "Variant" not in self.headers:
            VariantBoard = chess.Board
        else:
            from chess.variant import find_variant
            VariantBoard = find_variant(self.headers["Variant"])

        fen = self.headers.get("FEN", VariantBoard.starting_fen)
        board = VariantBoard(fen, chess960=chess960)
        board.chess960 = board.chess960 or board.has_chess960_castling_rights()
        return board

    def setup(self, board):
        """
        Setup a specific starting position. This sets (or resets) the
        ``FEN``, ``SetUp``, and ``Variant`` header tags.
        """
        try:
            fen = board.fen()
        except AttributeError:
            board = chess.Board(board)
            board.chess960 = board.has_chess960_castling_rights()
            fen = board.fen()

        if fen == type(board).starting_fen:
            self.headers.pop("SetUp", None)
            self.headers.pop("FEN", None)
        else:
            self.headers["SetUp"] = "1"
            self.headers["FEN"] = fen

        if type(board).aliases[0] == "Standard" and board.chess960:
            self.headers["Variant"] = "Chess960"
        elif type(board).aliases[0] != "Standard":
            self.headers["Variant"] = type(board).aliases[0]
            self.headers["FEN"] = board.fen()
        else:
            self.headers.pop("Variant", None)

    def accept(self, visitor):
        """
        Traverses the game in PGN order using the given *visitor*. Returns
        the visitor result.
        """
        visitor.begin_game()

        visitor.begin_headers()
        for tagname, tagvalue in self.headers.items():
            visitor.visit_header(tagname, tagvalue)
        visitor.end_headers()

        if self.comment:
            visitor.visit_comment(self.comment)

        super(Game, self).accept(visitor, _board=self.board())

        visitor.visit_result(self.headers.get("Result", "*"))
        visitor.end_game()
        return visitor.result()

    @classmethod
    def from_board(cls, board):
        """Creates a game from the move stack of a :class:`~chess.Board()`."""
        # Undo all moves.
        switchyard = collections.deque()
        while board.move_stack:
            switchyard.append(board.pop())

        # Setup the initial position.
        game = cls()
        game.setup(board)
        node = game

        # Replay all moves.
        while switchyard:
            move = switchyard.pop()
            node = node.add_variation(move)
            board.push(move)

        game.headers["Result"] = board.result()
        return game

    @classmethod
    def without_tag_roster(cls):
        """Creates an empty game without the default 7 tag roster."""
        return cls(headers={})


class Headers(MutableMapping):
    def __init__(self, data=None, **kwargs):
        self._tag_roster = {}
        self._others = {}

        if data is None:
            data = {
                "Event": "?",
                "Site": "?",
                "Date": "????.??.??",
                "Round": "?",
                "White": "?",
                "Black": "?",
                "Result": "*"
            }

        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        if key in TAG_ROSTER:
            self._tag_roster[key] = value
        elif not TAG_NAME_REGEX.match(key):
            raise ValueError("non-alphanumeric pgn header tag: {}".format(repr(key)))
        elif "\n" in value or "\r" in value:
            raise ValueError("line break in pgn header {}: {}".format(key, repr(value)))
        else:
            self._others[key] = value

    def __getitem__(self, key):
        if key in TAG_ROSTER:
            return self._tag_roster[key]
        else:
            return self._others[key]

    def __delitem__(self, key):
        if key in TAG_ROSTER:
            del self._tag_roster[key]
        else:
            del self._others[key]

    def __iter__(self):
        for key in TAG_ROSTER:
            if key in self._tag_roster:
                yield key

        for key in sorted(self._others):
            yield key

    def __len__(self):
        return len(self._tag_roster) + len(self._others)

    def copy(self):
        return type(self)(self)

    def __copy__(self):
        return self.copy()

    def __repr__(self):
        return "{}({})".format(
            type(self).__name__,
            ", ".join("{}={}".format(key, repr(value)) for key, value in self.items()))


class BaseVisitor(object):
    """
    Base class for visitors.

    Use with :func:`chess.pgn.Game.accept()` or
    :func:`chess.pgn.GameNode.accept()` or :func:`chess.pgn.read_game()`.

    The methods are called in PGN order.
    """

    def begin_game(self):
        """Called at the start of a game."""
        pass

    def begin_headers(self):
        """Called at the start of game headers."""
        pass

    def visit_header(self, tagname, tagvalue):
        """Called for each game header."""
        pass

    def end_headers(self):
        """Called at the end of the game headers."""
        pass

    def visit_move(self, board, move):
        """
        Called for each move.

        *board* is the board state before the move. The board state must be
        restored before the traversal continues.
        """
        pass

    def visit_comment(self, comment):
        """Called for each comment."""
        pass

    def visit_nag(self, nag):
        """Called for each NAG."""
        pass

    def begin_variation(self):
        """
        Called at the start of a new variation. It is not called for the
        main line of the game.
        """
        pass

    def end_variation(self):
        """Concludes a variation."""
        pass

    def visit_result(self, result):
        """
        Called at the end of a game with the value from the ``Result`` header.
        """
        pass

    def end_game(self):
        """Called at the end of a game."""
        pass

    def result(self):
        """Called to get the result of the visitor. Defaults to ``True``."""
        return True

    def handle_error(self, error):
        """Called for encountered errors. Defaults to raising an exception."""
        raise error


class GameModelCreator(BaseVisitor):
    """
    Creates a game model. Default visitor for :func:`~chess.pgn.read_game()`.
    """

    def __init__(self):
        self.game = Game()

        self.variation_stack = [self.game]
        self.starting_comment = ""
        self.in_variation = False

    def visit_header(self, tagname, tagvalue):
        self.game.headers[tagname] = tagvalue

    def visit_nag(self, nag):
        self.variation_stack[-1].nags.add(nag)

    def begin_variation(self):
        self.variation_stack.append(self.variation_stack[-1].parent)
        self.in_variation = False

    def end_variation(self):
        self.variation_stack.pop()

    def visit_result(self, result):
        if self.game.headers.get("Result", "*") == "*":
            self.game.headers["Result"] = result

    def visit_comment(self, comment):
        if self.in_variation or (self.variation_stack[-1].parent is None and self.variation_stack[-1].is_end()):
            # Add as a comment for the current node if in the middle of
            # a variation. Add as a comment for the game if the comment
            # starts before any move.
            new_comment = [self.variation_stack[-1].comment, comment]
            self.variation_stack[-1].comment = "\n".join(new_comment).strip()
        else:
            # Otherwise, it is a starting comment.
            new_comment = [self.starting_comment, comment]
            self.starting_comment = "\n".join(new_comment).strip()

    def visit_move(self, board, move):
        self.variation_stack[-1] = self.variation_stack[-1].add_variation(move)
        self.variation_stack[-1].starting_comment = self.starting_comment
        self.starting_comment = ""
        self.in_variation = True

    def handle_error(self, error):
        """
        Populates :data:`chess.pgn.Game.errors` with encountered errors and
        logs them.
        """
        LOGGER.exception("error during pgn parsing")
        self.game.errors.append(error)

    def result(self):
        """
        Returns the visited :class:`~chess.pgn.Game()`.
        """
        return self.game


class StringExporter(BaseVisitor):
    """
    Allows exporting a game as a string.

    >>> import chess.pgn
    >>>
    >>> game = chess.pgn.Game()
    >>>
    >>> exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
    >>> pgn_string = game.accept(exporter)

    Only *columns* characters are written per line. If *columns* is ``None``
    then the entire movetext will be on a single line. This does not affect
    header tags and comments.

    There will be no newline characters at the end of the string.
    """

    def __init__(self, columns=80, headers=True, comments=True, variations=True):
        self.columns = columns
        self.headers = headers
        self.comments = comments
        self.variations = variations

        self.found_headers = False

        self.force_movenumber = True

        self.lines = []
        self.current_line = ""
        self.variation_depth = 0

    def flush_current_line(self):
        if self.current_line:
            self.lines.append(self.current_line.rstrip())
        self.current_line = ""

    def write_token(self, token):
        if self.columns is not None and self.columns - len(self.current_line) < len(token):
            self.flush_current_line()
        self.current_line += token

    def write_line(self, line=""):
        self.flush_current_line()
        self.lines.append(line.rstrip())

    def end_game(self):
        self.write_line()

    def begin_headers(self):
        self.found_headers = False

    def visit_header(self, tagname, tagvalue):
        if self.headers:
            self.found_headers = True
            self.write_line("[{} \"{}\"]".format(tagname, tagvalue))

    def end_headers(self):
        if self.found_headers:
            self.write_line()

    def begin_variation(self):
        self.variation_depth += 1

        if self.variations:
            self.write_token("( ")
            self.force_movenumber = True

    def end_variation(self):
        self.variation_depth -= 1

        if self.variations:
            self.write_token(") ")
            self.force_movenumber = True

    def visit_comment(self, comment):
        if self.comments and (self.variations or not self.variation_depth):
            self.write_token("{ " + comment.replace("}", "").strip() + " } ")
            self.force_movenumber = True

    def visit_nag(self, nag):
        if self.comments and (self.variations or not self.variation_depth):
            self.write_token("$" + str(nag) + " ")

    def visit_move(self, board, move):
        if self.variations or not self.variation_depth:
            # Write the move number.
            if board.turn == chess.WHITE:
                self.write_token(str(board.fullmove_number) + ". ")
            elif self.force_movenumber:
                self.write_token(str(board.fullmove_number) + "... ")

            # Write the SAN.
            self.write_token(board.san(move) + " ")

            self.force_movenumber = False

    def visit_result(self, result):
        self.write_token(result + " ")

    def result(self):
        if self.current_line:
            return "\n".join(itertools.chain(self.lines, [self.current_line.rstrip()])).rstrip()
        else:
            return "\n".join(self.lines).rstrip()

    def __str__(self):
        return self.result()


class FileExporter(StringExporter):
    """
    Acts like a :class:`~chess.pgn.StringExporter`, but games are written
    directly into a text file.

    There will always be a blank line after each game. Handling encodings is up
    to the caller.

    >>> import chess.pgn
    >>>
    >>> game = chess.pgn.Game()
    >>>
    >>> new_pgn = open("/dev/null", "w", encoding="utf-8")
    >>> exporter = chess.pgn.FileExporter(new_pgn)
    >>> game.accept(exporter)
    """

    def __init__(self, handle, columns=80, headers=True, comments=True, variations=True):
        super(FileExporter, self).__init__(columns=columns, headers=headers, comments=comments, variations=variations)
        self.handle = handle

    def flush_current_line(self):
        if self.current_line:
            self.handle.write(self.current_line.rstrip())
            self.handle.write("\n")
        self.current_line = ""

    def write_line(self, line=""):
        self.flush_current_line()
        self.handle.write(line.rstrip())
        self.handle.write("\n")

    def result(self):
        return None

    def __repr__(self):
        return "<FileExporter at {}>".format(hex(id(self)))

    def __str__(self):
        return self.__repr__()


def read_game(handle, Visitor=GameModelCreator):
    """
    Reads a game from a file opened in text mode.

    >>> import chess.pgn
    >>>
    >>> pgn = open("data/pgn/kasparov-deep-blue-1997.pgn")
    >>>
    >>> first_game = chess.pgn.read_game(pgn)
    >>> second_game = chess.pgn.read_game(pgn)
    >>>
    >>> first_game.headers["Event"]
    'IBM Man-Machine, New York USA'
    >>>
    >>> # Iterate through all moves and play them on a board.
    >>> board = first_game.board()
    >>> for move in first_game.main_line():
    ...     board.push(move)
    ...
    >>> board
    Board('4r3/6P1/2p2P1k/1p6/pP2p1R1/P1B5/2P2K2/3r4 b - - 0 45')

    By using text mode, the parser does not need to handle encodings. It is the
    caller's responsibility to open the file with the correct encoding.
    PGN files are ASCII or UTF-8 most of the time. So, the following should
    cover most relevant cases (ASCII, UTF-8, UTF-8 with BOM).

    >>> # Python 3
    >>> pgn = open("data/pgn/kasparov-deep-blue-1997.pgn", encoding="utf-8-sig")

    Use :class:`~io.StringIO` to parse games from a string.

    >>> pgn_string = "1. e4 e5 2. Nf3 *"
    >>>
    >>> try:
    ...     from StringIO import StringIO  # Python 2
    ... except ImportError:
    ...     from io import StringIO  # Python 3
    ...
    >>> pgn = StringIO(pgn_string)
    >>> game = chess.pgn.read_game(pgn)

    The end of a game is determined by a completely blank line or the end of
    the file. (Of course, blank lines in comments are possible.)

    According to the PGN standard, at least the usual 7 header tags are
    required for a valid game. This parser also handles games without any
    headers just fine.

    The parser is relatively forgiving when it comes to errors. It skips over
    tokens it can not parse. Any exceptions are logged and collected in
    :data:`Game.errors <chess.pgn.Game.errors>`. This behavior can be
    :func:`overriden <chess.pgn.GameModelCreator.handle_error>`.

    Returns the parsed game or ``None`` if the end of file is reached.
    """
    visitor = Visitor()

    dummy_game = Game.without_tag_roster()
    found_game = False

    # Skip leading empty lines and comments.
    line = handle.readline()
    while line.isspace() or line.startswith("%") or line.startswith(";"):
        line = handle.readline()

    # Parse game headers.
    while line:
        # Skip comments.
        if line.startswith("%") or line.startswith(";"):
            line = handle.readline()
            continue

        # Read header tags.
        tag_match = TAG_REGEX.match(line)
        if tag_match:
            if not found_game:
                found_game = True
                visitor.begin_game()
                visitor.begin_headers()

            dummy_game.headers[tag_match.group(1)] = tag_match.group(2)
            visitor.visit_header(tag_match.group(1), tag_match.group(2))
        else:
            break

        line = handle.readline()

    if found_game:
        visitor.end_headers()

    # Skip a single empty line after headers.
    if line.isspace():
        line = handle.readline()

    # Movetext parser state.
    try:
        board_stack = [dummy_game.board()]
    except ValueError as error:
        visitor.handle_error(error)
        board_stack = [chess.Board()]

    # Parse movetext.
    while line:
        read_next_line = True

        if line.startswith("%") or line.startswith(";"):
            # Ignore comments.
            line = handle.readline()
            continue

        # An empty line means the end of a game. But gracefully try to find
        # at least some content if we didn't even see headers so far.
        if found_game and line.isspace():
            visitor.end_game()
            return visitor.result()

        for match in MOVETEXT_REGEX.finditer(line):
            token = match.group(0)

            if not found_game:
                found_game = True
                visitor.begin_game()

            if token.startswith("{"):
                # Consume until the end of the comment.
                line = token[1:]
                comment_lines = []
                while line and "}" not in line:
                    comment_lines.append(line.rstrip())
                    line = handle.readline()
                end_index = line.find("}")
                comment_lines.append(line[:end_index])
                if "}" in line:
                    line = line[end_index:]
                else:
                    line = ""

                visitor.visit_comment("\n".join(comment_lines).strip())

                # Continue with the current or the next line.
                if line:
                    read_next_line = False
                break
            elif token.startswith(";"):
                break
            elif token.startswith("$"):
                # Found a NAG.
                try:
                    nag = int(token[1:])
                except ValueError as error:
                    visitor.handle_error(error)
                else:
                    visitor.visit_nag(nag)
            elif token == "?":
                visitor.visit_nag(NAG_MISTAKE)
            elif token == "??":
                visitor.visit_nag(NAG_BLUNDER)
            elif token == "!":
                visitor.visit_nag(NAG_GOOD_MOVE)
            elif token == "!!":
                visitor.visit_nag(NAG_BRILLIANT_MOVE)
            elif token == "!?":
                visitor.visit_nag(NAG_SPECULATIVE_MOVE)
            elif token == "?!":
                visitor.visit_nag(NAG_DUBIOUS_MOVE)
            elif token == "(" and board_stack[-1].move_stack:
                visitor.begin_variation()

                board = board_stack[-1].copy()
                board.pop()
                board_stack.append(board)
            elif token == ")" and len(board_stack) > 1:
                # Always leave at least the root node on the stack.
                visitor.end_variation()
                board_stack.pop()
            elif token in ["1-0", "0-1", "1/2-1/2", "*"] and len(board_stack) == 1:
                visitor.visit_result(token)
            else:
                # Replace zeros castling notation.
                if token == "0-0":
                    token = "O-O"
                elif token == "0-0-0":
                    token = "O-O-O"

                # Parse SAN tokens.
                try:
                    move = board_stack[-1].parse_san(token)
                except ValueError as error:
                    visitor.handle_error(error)
                else:
                    visitor.visit_move(board_stack[-1], move)
                    board_stack[-1].push(move)

        if read_next_line:
            line = handle.readline()

    if found_game:
        visitor.end_game()
        return visitor.result()


def scan_headers(handle):
    """
    Scan a PGN file opened in text mode for game offsets and headers.

    Yields a tuple for each game. The first element is the offset and the
    second element is a mapping of game headers.

    Since actually parsing many games from a big file is relatively expensive,
    this is a better way to look only for specific games and then seek and
    parse them later.

    This example scans for the first game with Kasparov as the white player.

    >>> import chess.pgn
    >>>
    >>> pgn = open("data/pgn/kasparov-deep-blue-1997.pgn")
    >>>
    >>> for offset, headers in chess.pgn.scan_headers(pgn):
    ...     if "Kasparov" in headers["White"]:
    ...         kasparov_offset = offset
    ...         break

    Then it can later be seeked an parsed.

    >>> pgn.seek(kasparov_offset)
    0
    >>> game = chess.pgn.read_game(pgn)

    This also works nicely with generators, scanning lazily only when the next
    offset is required.

    >>> white_win_offsets = (offset for offset, headers in chess.pgn.scan_headers(pgn)
    ...                             if headers["Result"] == "1-0")
    >>> first_white_win = next(white_win_offsets)
    >>> second_white_win = next(white_win_offsets)

    :warning: Be careful when seeking a game in the file while more offsets are
        being generated.
    """
    in_comment = False

    game_headers = None
    game_pos = None

    last_pos = handle.tell()
    line = handle.readline()

    while line:
        # Skip single-line comments.
        if line.startswith("%"):
            last_pos = handle.tell()
            line = handle.readline()
            continue

        # Reading a header tag. Parse it and add it to the current headers.
        if not in_comment and line.startswith("["):
            tag_match = TAG_REGEX.match(line)
            if tag_match:
                if game_pos is None:
                    game_headers = Headers()
                    game_pos = last_pos

                game_headers[tag_match.group(1)] = tag_match.group(2)

                last_pos = handle.tell()
                line = handle.readline()
                continue

        # Reading movetext. Update parser's in_comment state in order to skip
        # comments that look like header tags.
        if (not in_comment and "{" in line) or (in_comment and "}" in line):
            in_comment = line.rfind("{") > line.rfind("}")

        # Reading movetext. If there were headers previously, those are now
        # complete and can be yielded.
        if game_pos is not None:
            yield game_pos, game_headers
            game_pos = None

        last_pos = handle.tell()
        line = handle.readline()

    # Yield the headers of the last game.
    if game_pos is not None:
        yield game_pos, game_headers


def scan_offsets(handle):
    """
    Scan a PGN file opened in text mode for game offsets.

    Yields the starting offsets of all the games, so that they can be seeked
    later. This is just like :func:`~chess.pgn.scan_headers()` but more
    efficient if you do not actually need the header information.

    The PGN standard requires each game to start with an ``Event`` tag. So does
    this scanner.
    """
    in_comment = False

    last_pos = handle.tell()
    line = handle.readline()

    while line:
        if not in_comment and line.startswith("[Event \""):
            yield last_pos
        elif (not in_comment and "{" in line) or (in_comment and "}" in line):
            in_comment = line.rfind("{") > line.rfind("}")

        last_pos = handle.tell()
        line = handle.readline()
