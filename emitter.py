"""
Utility to save go positions as psgo tex files.
"""

from time import sleep, strftime

import os
import sys

from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent

import win32clipboard

from renderer import Renderer
from state import State
from board import Board


def _cursor_move_handler(board, state, evt):
    direction = {Screen.KEY_DOWN: 'down',
                 Screen.KEY_UP: 'up',
                 Screen.KEY_LEFT: 'left',
                 Screen.KEY_RIGHT: 'right'}.get(evt.key_code)
    if direction:
        board.move_cursor(direction)
    else:
        return False

    if state.solution() is None:
        if state.mode() == 'paint':
            board.put(state.colour())
        elif state.mode() == 'erase':
            board.remove()

    return True


def _board_keys_handler(board, state, evt):
    """
    Process evt for handling the board.
    Return True if evt was handled, False otherwise.
    """
    if evt.key_code == ord(' '):
        board.toggle(state.colour())
    elif evt.key_code == ord('m'):
        state.cycle_mode()
        if state.mode() == 'paint':
            board.put(state.colour())
        elif state.mode() == 'erase':
            board.remove()
    elif evt.key_code == ord('p'):
        state.set_mode('paint')
        board.put(state.colour())
    elif evt.key_code == ord('n'):
        state.set_mode('normal')
    elif evt.key_code == ord('e'):
        state.set_mode('erase')
        board.remove()
    elif evt.key_code == ord('x'):
        state.swap_colour()
    elif evt.key_code == ord('s'):
        state.swap_colour()
        board.update_colour(state.colour())
    else:
        return False

    return True


def _to_clipboard(board, renderer):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(board.to_tex())
    win32clipboard.CloseClipboard()
    renderer.info_flash("Position copied to clipboard.")


def _to_file(fname_pattern, idx, board, renderer):
    fname = fname_pattern.format(idx)
    bname = os.path.basename(fname)
    err = ""
    msg = ""
    if os.path.exists(fname):
        err += "Cannot write {}, file exists".format(bname)
    else:
        try:
            with open(fname, 'w') as out:
                out.writelines(board.to_tex())
        except OSError as ex:
            err += "Failed to write {}: {}.".format(bname, ex)

    sols = board.solutions_to_tex()
    for sol_idx, tex_solution in enumerate(sols):
        fname_sol = fname[:-4]  # remove ".tex"
        fname_sol += "-sol-{}.tex".format(sol_idx + 1)
        bname_sol = os.path.basename(fname_sol)
        if os.path.exists(fname_sol):
            err += "Cannot write {}, file exists".format(bname_sol)
        else:
            try:
                with open(fname_sol, 'w') as out:
                    out.writelines(tex_solution)
            except OSError as ex:
                err += "Failed to write {}: {}.".format(bname, ex)

    if err:
        renderer.error_flash(err)
    else:
        msg = "Board saved to '{}' ({} solutions).".format(bname, len(sols))
        renderer.warning_flash(msg)


def _solution_branch_change_handler(board, state, renderer, evt):
    if evt.key_code == ord('A'):
        board.add_solution()
        renderer.info_flash("Solution branch added.")
    elif evt.key_code == ord('N'):
        board.next_solution()
    elif evt.key_code == ord('P'):
        board.prev_solution()
    elif evt.key_code == ord('D'):
        if state.solution() is None:
            renderer.error_flash("Cannot delete main position.")
        else:
            board.delete_solution()
            renderer.warning_flash("Solution branch deleted.")
    else:
        return False

    state.set_solution(board.get_solution())
    renderer.set_solution_index(state.solution())
    return True


def _handle_solution_keys(board, state, evt):
    code = evt.key_code
    if code == ord('x'):
        state.swap_colour()
    elif code == ord('s'):
        state.swap_colour()
        board.update_solution_colour(state.colour())
    elif code == ord(' '):
        board.swap_solution_colour()
    elif ord('1') <= code <= ord('9'):
        board.add_to_solution(state.colour(), chr(code))
        state.swap_colour()
    elif code == ord('0'):
        board.remove_from_solution()
    else:
        return False

    return True


def _update_title(renderer, fname_pattern, idx):
    fname = fname_pattern.format(idx)
    renderer.set_title("Working on {}".format(fname))


def _redraw(board, state, renderer):
    renderer.begin()
    renderer.set_solution_index(state.solution())
    if state.solution() is None:
        renderer.render_status(state.colour(), state.mode())
    else:
        renderer.render_status(state.colour(), "numbers")
    renderer.render_board(board)
    renderer.end()


def mainloop(fname_pattern, idx):
    """Main loop."""
    def _body(screen, fname_pattern=fname_pattern, idx=idx):

        board = Board()

        state = State()

        config = {'display': 'unicode'}
        renderer = Renderer(config, screen)

        _update_title(renderer, fname_pattern, idx)
        renderer.info_flash("Welcome!")

        _redraw(board, state, renderer)

        while True:
            evt = screen.get_event()
            if not evt or not isinstance(evt, KeyboardEvent):
                sleep(0.1)
                continue

            # QUIT
            if evt.key_code == ord('Q'):
                break

            # META-OPERATIONS

            # Change display
            if evt.key_code == ord('d'):
                config['display'] = {'unicode': 'ascii',
                                     'ascii': 'unicode'}[config['display']]
            # Write to file
            elif evt.key_code == ord('w'):
                _to_file(fname_pattern, idx, board, renderer)
                idx += 1
                _update_title(renderer, fname_pattern, idx)
            # Copy to clipboard
            elif evt.key_code == ord('c'):
                _to_clipboard(board, renderer)
            # Clear the board
            elif evt.key_code == ord('C'):
                board = Board()
                state = State()
                renderer.set_solution_index(None)
                renderer.info_flash("Board cleared.")

            # SOLUTION BRANCHES MANIPULATION
            elif _solution_branch_change_handler(board, state,
                                                 renderer, evt):
                # handled
                pass

            # CURSOR
            elif _cursor_move_handler(board, state, evt):
                # handled
                pass

            # "IN-SOLUTION STATE CHANGES"
            elif state.solution() is not None:
                if _handle_solution_keys(board, state, evt):
                    # handled
                    pass
                # nothing to do in solution

            # "NON-SOLUTION STATE CHANGES"
            elif _board_keys_handler(board, state, evt):
                # handled
                pass

            _redraw(board, state, renderer)

    return _body


def main():
    """Entry point."""
    if len(sys.argv) > 1:
        fname_pattern = sys.argv[1] + "-{}.tex"
    else:
        fname_pattern = strftime("%Y-%m-%d-%H-%M-problem-{}.tex")
    idx = 1
    if len(sys.argv) > 2:
        try:
            idx = int(sys.argv[2])
        except ValueError:
            pass

    Screen.wrapper(mainloop(fname_pattern, idx))


if __name__ == '__main__':
    main()
