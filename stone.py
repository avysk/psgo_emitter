"""Stone model."""


class Stone():
    """Entity that stores the stone, which can be put on a diagram."""
    def __init__(self, colour, label=None):
        self._colour = colour
        self._label = label

    @property
    def colour(self):
        """Colour of the stone: 'black' or 'white'."""
        return self._colour

    @colour.setter
    def colour(self, value):
        """Set the colour of the stone."""
        assert value in {'black', 'white'}
        self._colour = value

    @property
    def label(self):
        """Label on the stone; None if no label."""
        return self._label

    def flip(self):
        """Flip the colour of the stone"""
        self._colour = {'white': 'black',
                        'black': 'white'}[self._colour]
