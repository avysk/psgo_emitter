"""Export support functions."""


def psgo_prelude(point):
    """Prelude for psgo TeX code, for partial board between
    bottom left corner and given point."""
    prelude = r"\begin{psgopartialboard}{(1,1)("
    prelude += str(point[0])
    prelude += r","
    prelude += str(point[1])
    prelude += r")}"
    return prelude


def psgo_postlude():
    """Postlude for psgo TeX code."""
    return r"\end{psgopartialboard}"


def stone_to_tex(stone, point):
    """Convert stone at the given point to psgo TeX code."""
    line = ' ' * 8
    line += r"\stone"
    if stone.label:
        line += r"[\marklb{" + stone.label + r"}]"
    line += r"{" + stone.colour + r"}{"
    p_x, p_y = point
    # no 'i', should jump to 'j'!
    if p_x >= ord('i') - ord('a'):
        p_x += 1
    line += chr(ord('a') + p_x)
    line += r"}{"
    line += str(p_y + 1)
    line += r"}"
    return line
