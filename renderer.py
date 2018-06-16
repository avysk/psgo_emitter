"""Render things on screen."""
# pylint:disable=too-few-public-methods

from asciimatics.screen import Screen

COLUMN_STEP = 2
COLUMN_SHIFT = 5


class Renderer():
    """The class to render entities to the screen."""
    def __init__(self, config, screen):
        self._screen = screen
        self._config = config
        self._conv_table = {
            'ascii': {'white': 'o', 'black': 'x',
                      'empty': '.', 'hoshi': '*',
                      'cur_left': '[', 'cur_right': ']',
                      'border': '#'},
            'unicode': {'white': '●', 'black': '◯',
                        'empty': '⋅', 'hoshi': '•',
                        'cur_left': '[', 'cur_right': ']',
                        'border': '█'}
            }
        # Conversion table will be updated at render() call
        self._ctbl = None

        self._borders = {}

        self._flash = ()
        self._title = ""
        self._solution_idx = None

    def _update_borders(self):
        self._borders = {'left': self._sc_col(-1) - 1,
                         'right': self._sc_col(19) + 1,
                         'bottom': self._sc_row(-1) + 1,
                         'top': self._sc_row(19) - 1}

    def _update_ctbl(self):
        self._ctbl = self._conv_table[self._config['display']]

    # pylint:disable=no-self-use
    def _sc_col(self, col):
        return COLUMN_STEP * col + COLUMN_SHIFT

    def _sc_row(self, row):
        return self._screen.dimensions[0] - row - 6

    def _to_scr(self, col, row):
        return (self._sc_col(col), self._sc_row(row))

    # pylint:disable=no-self-use
    def _is_hoshi(self, col, row):
        return (col - 3) % 6 == 0 and (row - 3) % 6 == 0

    def _pr(self, piece, scr_coord):
        self._screen.print_at(self._ctbl[piece], *scr_coord)

    def _bd(self, piece, scr_coord):
        self._screen.print_at(self._ctbl[piece], *scr_coord,
                              Screen.COLOUR_WHITE, Screen.A_BOLD)

    def _is_stone(self, thing):
        return thing == 'white' or thing == 'black'

    def _is_numbered(self, thing):
        return 'label' in thing

    def _pr_labeled(self, stone, scr_coord):
        scr_colour = {'white': Screen.COLOUR_YELLOW,
                      'black': Screen.COLOUR_BLUE}[stone.colour]
        # No configurable display for numbers yet. Fix!
        self._screen.print_at(stone.label, *scr_coord,
                              scr_colour, Screen.A_BOLD)

    def _disp(self, point, stone):
        self._update_ctbl()
        scr_coord = self._to_scr(*point)
        if stone:
            if stone.label:
                self._pr_labeled(stone, scr_coord)
            else:
                self._pr(stone.colour, scr_coord)
        elif self._is_hoshi(*point):
            self._bd('hoshi', scr_coord)
        else:
            self._pr('empty', scr_coord)

    def _render_cursor(self, cur_pos):
        cur_x, cur_y = self._to_scr(*cur_pos)
        self._pr('cur_left', (cur_x - 1, cur_y))
        self._pr('cur_right', (cur_x + 1, cur_y))

    def begin(self):
        """Start rendering."""
        self._screen.clear()

    def end(self):
        """End rendering."""
        self._screen.refresh()

    def set_title(self, title):
        """Set title."""
        self._title = title

    def set_solution_index(self, idx):
        """Set variation line."""
        self._solution_idx = idx

    def info_flash(self, message):
        """Show info flash at next status render."""
        self._flash = (message, 'INFO')

    def warning_flash(self, message):
        """Show warning flash at next status render."""
        self._flash = (message, 'WARNING')

    def error_flash(self, message):
        """Show error flash at next status render."""
        self._flash = (message, 'ERROR')

    def render_status(self, colour, mode):
        """Render status line and title."""
        self._update_ctbl()
        schar = self._ctbl[colour]
        line = self._screen.dimensions[0] - 1
        self._screen.print_at("Mode: {} Colour: {}".format(mode, schar),
                              4, line,
                              Screen.COLOUR_GREEN, Screen.A_BOLD)
        if self._flash:
            message, severity = self._flash
            msg_colour = {'INFO': Screen.COLOUR_BLUE,
                          'WARNING': Screen.COLOUR_YELLOW,
                          'ERROR': Screen.COLOUR_RED}[severity]
            self._screen.print_at(message, 28, line, msg_colour, Screen.A_BOLD)
            self._flash = ()

        self._screen.print_at(self._title, 0, 0,
                              Screen.COLOUR_BLUE, Screen.A_BOLD)
        if self._solution_idx is not None:
            line = "[Solution: {}]".format(self._solution_idx + 1)
            self._screen.print_at(line, 0, 1,
                                  Screen.COLOUR_RED, Screen.A_BOLD)

    def render_board(self, board):
        """Render stuff to the screen"""

        # We need border around active area, hence +1
        max_width = min(19, board.get_width() + 1)
        max_height = min(19, board.get_height() + 1)

        stuff_dict = board.get_items()
        cur_pos = board.get_cursor()

        self._update_ctbl()
        self._update_borders()
        for row in range(max_height):
            for column in range(max_width):
                point = (column, row)
                thing = stuff_dict.get(point)
                self._disp(point, thing)

        # Borders
        bchar = self._ctbl['border']
        highest = self._sc_row(max_height) - 1
        widest = self._sc_col(max_width) + 1

        # Left border
        self._screen.move(self._borders['left'], self._borders['bottom'])
        self._screen.draw(self._borders['left'], highest, char=bchar)

        # Bottom border
        self._screen.move(self._borders['left'], self._borders['bottom'])
        self._screen.draw(widest, self._borders['bottom'], char=bchar)

        # Right border
        if max_width == 19:
            self._screen.move(self._borders['right'], self._borders['bottom'])
            self._screen.draw(self._borders['right'], highest, char=bchar)

        # Top border
        if max_height == 19:
            self._screen.move(self._borders['left'], self._borders['top'])
            self._screen.draw(widest, self._borders['top'], char=bchar)

        self._render_cursor(cur_pos)
