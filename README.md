`psgo_emitter` is a (Windows) console utility to create go diagrams for go life-and-death problems (tsumego).

# Requirements

* Unless you are using pre-build executable:

        * Python 3

        * `asciimatics` package

* I recommend to use in a console window some font with good unicode support; "DejaVu Sans Mono" is what I am using (but see `d` below in "Keybindings").

# Usage

Run the program from a console window.

The program accepts two optional arguments:

* the common part of file names to write (`-[sequential number].tex` will be added to it. By default the files will be written in the current directory, with the names `YYYY-mm-dd-HH-MM-problem-[sequential number].tex` where `YYYY-mm-dd-HH-MM` is the date and time when the program was started.
* the first sequential number to use; `1` by default.

# Keybindings

* `d` to switch between unicode and ascii display
* `C` to clear the board
* `Q` to exit the program
* arrows to move the selected point on the board
* space to add / remove stone
* `x` to switch the currently used stone colour
* `s` to switch the currently used stone colour, and, if there is the stone on the board in the selected cell, switch its colour too.
* `m` to switch between "normal", "paint" and "erase" modes (self-explanatory)
* `n` turn on "normal" mode
* `p` turn on "paint" mode
* `e` turn on "erase" mode
* `c` to copy to system clipboard LaTeX string for the position (requires `psgo` package)
* `w` to write LaTeX file for the position (and move on to the next file)

