"""Board model."""

from operator import itemgetter


class Board():
    """
    Entity that stores position and can render it to screen
    or to TeX string.
    """
    def __init__(self):
        self._board = {}
        self._cursor_row = 0
        self._cursor_column = 0

    def cur_left(self):
        """Move board cursor left."""
        self._cursor_column -= 1
        if self._cursor_column < 0:
            self._cursor_column = 0

    def cur_right(self):
        """Move board cursor right."""
        self._cursor_column += 1
        if self._cursor_column > 18:
            self._cursor_column = 18

    def cur_down(self):
        """Move board cursor down."""
        self._cursor_row -= 1
        if self._cursor_row < 0:
            self._cursor_row = 0

    def cur_up(self):
        """Move board cursor up."""
        self._cursor_row += 1
        if self._cursor_row > 18:
            self._cursor_row = 18

    def to_tex(self):
        """Convert board position to TeX code."""
        start = r"\begin{psgopartialboard}{(1,1)("
        start += str(self.get_width(use_cursor=False) + 1)
        start += r","
        start += str(self.get_height(use_cursor=False) + 1)
        start += r")}"
        result = [start]
        for (p_x, p_y), colour in self._board.items():
            line = ' ' * 8
            line += r"\stone{" + colour + r"}{"
            # no 'i', should jump to j!
            if p_x >= ord('i') - ord('a'):
                p_x += 1
            line += chr(ord('a') + p_x)
            line += r"}{"
            line += str(p_y + 1)
            line += r"}"
            result.append(line)
        result.append(r"\end{psgopartialboard}")
        return '\n'.join(result)

    def get_width(self, use_cursor=True):
        """Return the width of used part of the board."""
        if self._board:
            width = max(self._board.keys())[0]
        else:
            width = 0
        if use_cursor:
            width = max(width, self._cursor_column)
        width = max(4, width + 1)
        return min(width, 19)

    def get_height(self, use_cursor=True):
        """Return the height of used part of the board."""
        if self._board:
            height = max(self._board.keys(), key=itemgetter(1))[1]
        else:
            height = 0
        if use_cursor:
            height = max(height, self._cursor_row)
        height = max(4, height + 1)
        return min(height, 19)

    def get_cursor(self):
        """Return cursor coordinates."""
        return (self._cursor_column, self._cursor_row)

    def get_items(self):
        """Return board items."""
        return self._board.copy()

    def put(self, colour):
        """Put stone at cursor."""
        point = (self._cursor_column, self._cursor_row)
        self._board[point] = colour

    def update_colour(self, colour):
        """Update colour of the stone under the cursor,
        if there is one."""
        point = (self._cursor_column, self._cursor_row)
        if point in self._board:
            self.put(colour)

    def remove(self):
        """Remove stone at cursor."""
        point = (self._cursor_column, self._cursor_row)
        if point in self._board:
            del self._board[point]

    def toggle(self, colour):
        """Put or remove stone at cursor."""
        point = (self._cursor_column, self._cursor_row)
        if point in self._board:
            del self._board[point]
        else:
            self._board[point] = colour
