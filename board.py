"""Board model."""

from copy import deepcopy
from operator import itemgetter

import export_support as xp

from cursor import Cursor
from stone import Stone


_MIN_CORNER_SIZE = 4
_MIN_BORDER = 1


class Board():
    """
    Entity that stores position and can render it to screen
    or to TeX string.
    """
    def __init__(self, board=None, solutions=None):
        self._board = board or {}
        self._solution_idx = None
        self._solutions = solutions or []
        self._cursor = Cursor()

    # Cursor {{{1

    def move_cursor(self, where):
        """Move cursor left, right, up or down."""
        self._cursor.move(where)

    def get_cursor(self):
        """Return cursor coordinates."""
        return self._cursor.point

    # }}}1

    # TeX support {{{1

    def _get_psgo_prelude(self, solution_index=None):
        point = (self._get_dim(0, False, solution_index) + 1,
                 self._get_dim(1, False, solution_index) + 1)
        return xp.psgo_prelude(point)

    def _objects_to_tex(self, objects, solution_index=None):

        result = [self._get_psgo_prelude(solution_index=solution_index)]
        for point, stone in objects.items():
            result.append(xp.stone_to_tex(stone, point))

        result.append(xp.psgo_postlude())

        return '\n'.join(result)

    def to_tex(self, main_only=True):
        """Convert the board position to TeX code.
        If main_only is True, only the main position is used.
        Otherwise, the current solution branch is used."""
        if main_only:
            objects = self._board
        else:
            objects = self.get_items()
        return self._objects_to_tex(objects)

    def solutions_to_tex(self):
        """Convert solutions to the list of TeX code strings."""
        results = []
        for idx in range(len(self._solutions)):
            objects = self.get_items(solution_index=idx)
            results.append(self._objects_to_tex(objects, idx))
        return results

    # }}}1

    # Geometry {{{1

    def _get_dim(self, axis, use_cursor, idx):

        maxkey = itemgetter(axis)

        if self._board:
            res = max(self._board.keys(), key=maxkey)[axis]
        else:
            res = 0

        if idx is not None:
            sol = self._solutions[idx]
            if sol:
                res = max(res, max(sol.keys(), key=maxkey)[axis])

        if use_cursor:
            res = max(res, self._cursor.point[axis])

        res = max(_MIN_CORNER_SIZE, res + _MIN_BORDER)

        return min(res, 19)

    def get_width(self, use_cursor=True):
        """Return the width of used part of the board."""
        return self._get_dim(0, use_cursor, self._solution_idx)

    def get_height(self, use_cursor=True):
        """Return the height of used part of the board."""
        return self._get_dim(1, use_cursor, self._solution_idx)

    # }}}1

    # Manipulate stones in main position {{{1

    def put(self, colour):
        """Put stone at cursor."""
        self._board[self._cursor.point] = Stone(colour)

    def remove(self):
        """Remove stone at cursor."""
        point = self._cursor.point
        if point in self._board:
            del self._board[point]

    def toggle(self, colour):
        """Put or remove stone at cursor."""
        point = self._cursor.point
        if point in self._board:
            del self._board[point]
        else:
            self._board[point] = Stone(colour)

    def update_colour(self, colour):
        """Update colour of the stone under the cursor,
        if there is one."""
        point = self._cursor.point
        if point in self._board:
            self._board[point].colour = colour

    # }}}1

    # Manipulate stones in solution branch {{{1

    def put_sol(self, colour, number):
        """Add a stone to solution."""
        assert self._solution_idx is not None
        point = self._cursor.point
        self._solutions[self._solution_idx][point] = \
            Stone(colour, label=number)

    def remove_sol(self):
        """Remove a stone from solution."""
        assert self._solution_idx is not None
        point = self._cursor.point
        if point in self._solutions[self._solution_idx]:
            del self._solutions[self._solution_idx][point]

    def update_colour_sol(self, colour):
        """Update colour of the solution stone under the cursor,
        if there is one."""
        assert self._solution_idx is not None
        sol = self._solutions[self._solution_idx]
        point = self._cursor.point
        if point in sol:
            sol[point].colour = colour

    def flip_sol(self):
        """Flip colour of the solution stone under the cursor,
        if there is one: white <-> black."""
        assert self._solution_idx is not None
        sol = self._solutions[self._solution_idx]
        point = self._cursor.point
        if point in sol:
            sol[point].flip()

    # }}}1

    # Solution branches management {{{1

    def get_solution(self):
        """Return current solution branch."""
        return self._solution_idx

    def add_solution(self):
        """Add solution branch and switch to it."""
        self._solutions.append({})
        self._solution_idx = len(self._solutions) - 1

    def delete_solution(self):
        """Remove solution branch."""
        del self._solutions[self._solution_idx]
        if self._solutions:
            self._solution_idx %= len(self._solutions)
        else:
            self._solution_idx = None

    def _shift_solution(self, delta):

        branches = len(self._solutions)

        if not branches:
            # no branches - nothing to do
            return

        if self._solution_idx is None:
            # if we are in a main line, move to one of the branches
            self._solution_idx = 0 if delta == 1 else branches - 1
            return

        # we are not in a main line
        self._solution_idx += delta
        if self._solution_idx == branches:
            # To main line after the last
            self._solution_idx = None
        elif self._solution_idx == -1:
            # To main line before the first
            self._solution_idx = None
        else:
            self._solution_idx %= len(self._solutions)

    def next_solution(self):
        """Switch to the next solution."""
        self._shift_solution(1)

    def prev_solution(self):
        """Switch to the previous solution."""
        self._shift_solution(-1)

    # }}}1

    # {{{1 Access to board items

    def get_items(self, solution_index=None):
        """Return board items."""
        res = self._board.copy()
        if solution_index is not None:
            idx = solution_index
        else:
            idx = self._solution_idx
        if idx is not None:
            # Order matters, numbers should overwrite stones!
            res.update(deepcopy(self._solutions[idx]))
        return res

    # }}}1
