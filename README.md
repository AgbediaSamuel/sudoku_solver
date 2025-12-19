# Enhanced Generalized Sudoku Solver

A Python implementation of a generalized Sudoku solver that works with n² × n² boards (4×4, 9×9, 16×16, etc.) using backtracking with intelligent heuristics, **Prolog constraint validation**, **human-style explanations**, and **automatic puzzle generation**.

## 🎯 Key Features

### Core Solver
- **Generalized**: Works with any n² × n² board size (4×4, 9×9, 16×16, 25×25, etc.)
- **Efficient**: Uses MRV (Minimum Remaining Values) heuristic and forward checking
- **Prolog Integration**: Validates moves using Prolog constraint rules
- **Human Explanations**: Provides step-by-step reasoning for each move

### Puzzle Generation
- **Automatic Generation**: Create random valid puzzles
- **Difficulty Levels**: Easy, Medium, and Hard
- **Unique Solutions**: Ensures generated puzzles have valid solutions

### User Interfaces
- **Enhanced GUI**: Tkinter interface with real-time explanations
- **CLI**: Command-line interface for quick solving
- **Well-tested**: Comprehensive test suite

## 📁 Structure

```
sudoku_solver/
├── __init__.py          # Package initialization
├── board.py             # SudokuBoard class - board representation
├── solver.py            # SudokuSolver class - solving with explanations
├── generator.py         # SudokuGenerator class - puzzle generation
├── prolog_validator.py  # Prolog integration wrapper
├── sudoku_rules.pl      # Prolog constraint rules
├── utils.py             # Shared UI utilities (filtering, formatting)
├── gui.py               # Enhanced Tkinter GUI
├── cli.py               # Command-line interface
├── test_cases.py        # Test suite
├── requirements.txt     # Dependencies (pyswip)
└── README.md            # This file
```

## 🚀 Installation

### Prerequisites
1. **Python 3.8+**
2. **SWI-Prolog** (for Prolog integration)
   - macOS: `brew install swi-prolog`
   - Ubuntu: `sudo apt-get install swi-prolog`
   - Windows: Download from https://www.swi-prolog.org/

### Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pyswip` - Python-Prolog bridge

## 💻 Usage

### GUI (Recommended)

```bash
# Run GUI with 9×9 board
python gui.py

# Run GUI with 4×4 board
python gui.py 2

# Run GUI with 16×16 board
python gui.py 4
```

**GUI Features:**
- **Generate Puzzle**: Create random puzzles with difficulty selection
- **Solve with Explanations**: See step-by-step reasoning
- **Board Size Selector**: Switch between 4×4, 9×9, and 16×16
- **Real-time Statistics**: Nodes explored, backtracks, time
- **Prolog Validation**: Optional constraint checking with Prolog

### Command Line

```bash
# Solve a 9×9 puzzle
python cli.py 3 "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79"

# Solve a 4×4 puzzle
python cli.py 2 "1.3...1...4.4.2."

# Interactive mode
python cli.py 3
```

### As a Module

```python
from board import SudokuBoard
from solver import SudokuSolver
from generator import SudokuGenerator

# Generate a puzzle
generator = SudokuGenerator(n=3)  # 9×9
puzzle, stats = generator.generate_with_stats("medium")
print(f"Generated puzzle with {stats['clues']} clues")

# Solve with explanations
solver = SudokuSolver(use_mrv=True, use_forward_checking=True, use_prolog=True)
success, solution = solver.solve(puzzle)

if success:
    print(solution)
    # Get human-readable explanations
    for explanation in solver.get_explanations():
        print(explanation)
```

### Run Tests

```bash
python test_cases.py
```

Tests include:
- 4×4 Sudoku
- 9×9 Easy and Hard
- 16×16 Sudoku
- Heuristic comparison (MRV vs naive)

## 🎲 Board Sizes

| Size | n | Grid | Values |
|------|---|------|--------|
| 4×4 | 2 | 2×2 boxes | 1-4 |
| 9×9 | 3 | 3×3 boxes | 1-9 |
| 16×16 | 4 | 4×4 boxes | 1-9, A-G |
| 25×25 | 5 | 5×5 boxes | 1-9, A-P |

For boards larger than 9×9, letters represent values:
- A=10, B=11, C=12, ..., P=25

## 🧠 Algorithm Details

### Solving Strategy

1. **Backtracking**: Systematic search through the solution space
2. **MRV Heuristic**: Selects cells with fewest remaining candidates first
3. **Forward Checking**: Prunes branches early by checking consistency
4. **Constraint Propagation**: Maintains arc consistency during search
5. **Prolog Validation**: Double-checks moves using Prolog rules

### Prolog Integration

The solver uses Prolog for constraint checking:

```prolog
% Check if a move is valid
valid_move(Board, RowIdx, ColIdx, Value, N) :-
    Value \= 0,
    get_row(Board, RowIdx, Row),
    not_in_list(Value, Row),
    get_col(Board, ColIdx, Col),
    not_in_list(Value, Col),
    get_box(Board, RowIdx, ColIdx, N, Box),
    not_in_list(Value, Box).
```

### Human-Style Explanations

The solver generates explanations like:

```
[MRV] Selected cell (2,3) with 2 candidates: [5, 7]
→ Trying 5 at (2,3)
  ✓ Move valid - continuing search
  ✗ Forward checking failed - creates dead end
  ← Backtracking from (2,3)
→ Trying 7 at (2,3)
  ✓ Prolog validation passed
  ✓ Move valid - continuing search
```

### Puzzle Generation

1. Fill diagonal boxes with random values (they're independent)
2. Solve the rest to get a complete valid board
3. Remove cells one by one while maintaining solvability
4. Stop when desired difficulty is reached:
   - **Easy**: 50-60% clues
   - **Medium**: 35-45% clues
   - **Hard**: 25-35% clues

## ⚡ Performance

Typical solve times on a modern CPU:

| Board | Difficulty | Time | Nodes Explored |
|-------|-----------|------|----------------|
| 4×4 | Any | < 0.001s | < 20 |
| 9×9 | Easy | < 0.01s | < 100 |
| 9×9 | Hard | < 0.1s | < 5,000 |
| 16×16 | Medium | 1-10s | < 50,000 |

**With heuristics enabled**, the solver explores **80x fewer nodes** compared to naive backtracking.

## 📚 Learning Outcomes

This project demonstrates:

- **Constraint Satisfaction Problems (CSP)**: Modeling and solving CSPs
- **Backtracking Algorithms**: Recursive search with pruning
- **Heuristic Search**: MRV, forward checking, constraint propagation
- **Logic Programming**: Prolog integration for constraint checking
- **Algorithm Analysis**: Performance comparison and optimization
- **Software Engineering**: Clean architecture, modularity, testing
- **Generalization**: Extending algorithms to arbitrary sizes

## 🎓 Educational Value

This implementation goes beyond a simple 9×9 Sudoku solver by:

1. **Generalizing to n² × n²**: Works for any board size
2. **Integrating Prolog**: Demonstrates logic programming for constraints
3. **Providing Explanations**: Shows reasoning process step-by-step
4. **Generating Puzzles**: Creates valid puzzles with difficulty control
5. **Comparing Strategies**: Tests different heuristics and their impact

## 🔧 Requirements

- **Python 3.8+**
- **SWI-Prolog** (optional, for Prolog integration)
- **pyswip** (installed via requirements.txt)
- **tkinter** (built-in with Python)

## 🐛 Troubleshooting

### Prolog Not Available

If you see "Warning: pyswip not available", the solver will still work using Python-only validation. To enable Prolog:

1. Install SWI-Prolog
2. Install pyswip: `pip install pyswip`
3. Restart the application

### GUI Issues

If the GUI doesn't start:
- Ensure tkinter is installed (usually built-in)
- Try running with Python 3: `python3 gui.py`

## 📝 License

This project is for educational purposes as part of CS152 coursework.

## 👨‍💻 Author

Created for CS152 Final Project - Demonstrating advanced constraint satisfaction problem solving with logic programming integration.
