"""Cursor on the board."""


class Cursor():
    """Entity that stores a cursor."""
    def __init__(self):
        self._point = [0, 0]

    @property
    def point(self):
        """Return cursor position."""
        return tuple(self._point)

    def _change(self, axis, delta):
        self._point[axis] += delta
        self._point[axis] %= 19

    def move(self, where):
        """Move cursor left, right, up or down."""
        axis = {'left': 0, 'right': 0,
                'up': 1, 'down': 1}[where]
        delta = {'left': -1, 'down': -1,
                 'right': 1, 'up': 1}[where]
        self._change(axis, delta)
