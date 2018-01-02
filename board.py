"""Board model."""

from copy import deepcopy

from operator import itemgetter


class Board():
    """
    Entity that stores position and can render it to screen
    or to TeX string.
    """
    def __init__(self):
        self._board = {}
        self._solution_idx = None
        self._solutions = []
        self._cursor_row = 0
        self._cursor_column = 0
        self._movers = {'left': self._cur_left,
                        'right': self._cur_right,
                        'up': self._cur_up,
                        'down': self._cur_down}

    def move_cursor(self, where):
        """Move cursor left, right, up or down."""
        self._movers[where]()

    def _cur_left(self):
        self._cursor_column -= 1
        if self._cursor_column < 0:
            self._cursor_column = 0

    def _cur_right(self):
        self._cursor_column += 1
        if self._cursor_column > 18:
            self._cursor_column = 18

    def _cur_down(self):
        self._cursor_row -= 1
        if self._cursor_row < 0:
            self._cursor_row = 0

    def _cur_up(self):
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

    def solutions_to_tex(self):
        """Convert solutions to the list of TeX code strings."""
        results = []
        for idx in range(len(self._solutions)):
            things = self.get_items(solution_index=idx)
            start = r"\begin{psgopartialboard}{(1,1)("
            start += str(self.get_width(use_cursor=False,
                                        solution_index=idx) + 1)
            start += r","
            start += str(self.get_height(use_cursor=False,
                                         solution_index=idx) + 1)
            start += r")}"
            result = [start]
            for (p_x, p_y), thing in things.items():
                line = ' ' * 8
                if isinstance(thing, dict):
                    colour = thing['colour']
                    number = thing['number']
                else:
                    colour = thing
                    number = None
                line += r"\stone"
                if number is not None:
                    line += r"[\marklb{" + number + r"}]"
                line += r"{" + colour + r"}{"
                # no 'i', should jump to j!
                if p_x >= ord('i') - ord('a'):
                    p_x += 1
                line += chr(ord('a') + p_x)
                line += r"}{"
                line += str(p_y + 1)
                line += r"}"
                result.append(line)
            result.append(r"\end{psgopartialboard}")
            results.append('\n'.join(result))

        return results

    def get_width(self, use_cursor=True, solution_index=None):
        """Return the width of used part of the board."""
        if self._board:
            width = max(self._board.keys())[0]
        else:
            width = 0
        idx = solution_index or self._solution_idx
        if idx is not None:
            sol = self._solutions[idx]
            if sol:
                width = max(width, max(sol.keys())[0])
        if use_cursor:
            width = max(width, self._cursor_column)
        width = max(4, width + 1)
        return min(width, 19)

    def get_height(self, use_cursor=True, solution_index=None):
        """Return the height of used part of the board."""
        if self._board:
            height = max(self._board.keys(), key=itemgetter(1))[1]
        else:
            height = 0
        idx = solution_index or self._solution_idx
        if idx is not None:
            sol = self._solutions[idx]
            if sol:
                height = max(height, max(sol.keys(), key=itemgetter(1))[1])
        if use_cursor:
            height = max(height, self._cursor_row)
        height = max(4, height + 1)
        return min(height, 19)

    def get_cursor(self):
        """Return cursor coordinates."""
        return (self._cursor_column, self._cursor_row)

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

    def update_solution_colour(self, colour):
        """Update colour of the solution stone under the cursor,
        if there is one."""
        assert self._solution_idx is not None
        sol = self._solutions[self._solution_idx]
        point = (self._cursor_column, self._cursor_row)
        if point in sol:
            sol['colour'] = colour

    def swap_solution_colour(self):
        """Swap colour of the solution stone under the cursor,
        if there is one: white <-> black."""
        assert self._solution_idx is not None
        sol = self._solutions[self._solution_idx]
        point = (self._cursor_column, self._cursor_row)
        if point in sol:
            stone = sol[point]
            stone['colour'] = {'white': 'black',
                               'black': 'white'}[stone['colour']]

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

    def add_to_solution(self, colour, number):
        """Add a stone to solution."""
        assert self._solution_idx is not None
        point = (self._cursor_column, self._cursor_row)
        self._solutions[self._solution_idx][point] = \
            {'number': number, 'colour': colour}

    def remove_from_solution(self):
        """Remove a stone from solution."""
        assert self._solution_idx is not None
        point = (self._cursor_column, self._cursor_row)
        if point in self._solutions[self._solution_idx]:
            del self._solutions[self._solution_idx][point]
