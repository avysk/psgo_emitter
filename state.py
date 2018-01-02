"""UI state."""


class State():
    """UI state."""
    def __init__(self):
        self._colour = 'black'
        self._mode = 'normal'
        self._solution = None

    # Access state

    def colour(self):
        """Return current colour."""
        return self._colour

    def mode(self):
        """Return current mode."""
        return self._mode

    def solution(self):
        """Return index of current solution branch."""
        return self._solution

    # Change state

    def swap_colour(self):
        """Change colour: black <-> white."""
        self._colour = {'white': 'black',
                        'black': 'white'}[self._colour]

    def cycle_mode(self):
        """Cycle mode: normal -> paint -> erase -> normal."""
        self._mode = {'normal': 'paint',
                      'paint': 'erase',
                      'erase': 'normal'}[self._mode]

    def set_mode(self, mode):
        """Set mode."""
        self._mode = mode

    def set_solution(self, solution):
        """Set solution index."""
        self._solution = solution
