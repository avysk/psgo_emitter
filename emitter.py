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
from board import Board


def _swap(colour):
    return {'white': 'black',
            'black': 'white'}[colour]


def _board_keys_handler(board, cur_colour, mode, event):
    """
    Process event for handling the board.
    Return True if event was handled, False otherwise.
    """
    if event.key_code == ord(' '):
        board.toggle(cur_colour)
        return True

    if event.key_code == Screen.KEY_DOWN:
        board.cur_down()
    elif event.key_code == Screen.KEY_UP:
        board.cur_up()
    elif event.key_code == Screen.KEY_LEFT:
        board.cur_left()
    elif event.key_code == Screen.KEY_RIGHT:
        board.cur_right()
    else:
        return False

    if mode == 'paint':
        board.put(cur_colour)
    elif mode == 'erase':
        board.remove()

    return True


def _cycle_mode(mode):
    return {'normal': 'paint', 'paint': 'erase', 'erase': 'normal'}[mode]


def _update_title(renderer, fname_pattern, idx):
    fname = fname_pattern.format(idx)
    renderer.set_title("Working on {}".format(fname))


def mainloop(fname_pattern, idx):
    """Main loop."""
    def _body(screen, fname_pattern=fname_pattern, idx=idx):
        board = Board()
        config = {'display': 'unicode'}
        renderer = Renderer(config, screen)
        colour = 'black'
        mode = 'normal'
        _update_title(renderer, fname_pattern, idx)
        renderer.info_flash("Welcome!")
        renderer.render_status(colour, mode)
        renderer.render_board(board)
        screen.refresh()
        while True:
            evt = screen.get_event()
            if not evt or not isinstance(evt, KeyboardEvent):
                sleep(0.1)
                continue

            if evt.key_code == ord('Q'):
                break

            if _board_keys_handler(board, colour, mode, evt):
                # Already handled
                pass
            elif evt.key_code == ord('m'):
                mode = _cycle_mode(mode)
                if mode == 'paint':
                    board.put(colour)
                elif mode == 'erase':
                    board.remove()
            elif evt.key_code == ord('p'):
                mode = 'paint'
                board.put(colour)
            elif evt.key_code == ord('n'):
                mode = 'normal'
            elif evt.key_code == ord('e'):
                mode = 'erase'
                board.remove()
            elif evt.key_code == ord('d'):
                config['display'] = {'unicode': 'ascii',
                                     'ascii': 'unicode'}[config['display']]
            elif evt.key_code == ord('c'):
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(board.to_tex())
                win32clipboard.CloseClipboard()
                renderer.info_flash("Position copied to clipboard.")
            elif evt.key_code == ord('C'):
                board = Board()
                renderer.info_flash("Board cleared.")
            elif evt.key_code == ord('x'):
                colour = _swap(colour)
                board.update_colour(colour)
            elif evt.key_code == ord('w'):
                fname = fname_pattern.format(idx)
                bname = os.path.basename(fname)
                if os.path.exists(fname):
                    err = "Cannot write {}, file exists".format(bname)
                    renderer.error_flash(err)
                else:
                    try:
                        with open(fname, 'w') as out:
                            out.writelines(board.to_tex())
                        msg = "Board saved to '{}'.".format(bname)
                        renderer.warning_flash(msg)
                    except OSError as ex:
                        err = "Failed to write {}: {}.".format(bname, ex)
                        renderer.error_flash(err)
                idx += 1
                _update_title(renderer, fname_pattern, idx)

            screen.clear()
            renderer.render_status(colour, mode)
            renderer.render_board(board)
            screen.refresh()
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
