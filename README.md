# Sudoku Solver (Generalized)

Generalized Sudoku solver for n^2 x n^2 boards (4x4, 9x9, 16x16). Includes a solver, puzzle generator, Tkinter GUI, and a CLI.

## Requirements

- Python 3.8+
- Tkinter (usually included with Python)
- Optional (for Prolog validation): SWI-Prolog + pyswip

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Run

GUI:

```bash
python gui.py        # 9x9 (n=3)
python gui.py 2      # 4x4 (n=2)
python gui.py 4      # 16x16 (n=4)
```

CLI:

```bash
python cli.py                      # interactive mode
python cli.py 3 "<puzzle_string>"   # one-shot solve
```

## Puzzle input format

- Use `.` or `0` for empty cells.
- For 9x9: digits `1-9`.
- For 16x16: `0-9` and `A-G` for values 10-16.
- Length must be (board_size^2): 16 (4x4), 81 (9x9), 256 (16x16).

Example (9x9):

```text
53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79
```

## Tests

```bash
python test_cases.py
```
