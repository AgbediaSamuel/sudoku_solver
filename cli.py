"""
Sudoku Solver - Interactive Command Line Interface
"""

import sys
from typing import Optional

from board import SudokuBoard
from generator import SudokuGenerator
from solver import SudokuSolver
from utils import filter_key_steps


class InteractiveCLI:
    """Interactive command-line interface for Sudoku Solver."""

    def __init__(self):
        """Initialize the interactive CLI."""
        self.size = 3
        self.board_size = 9
        self.board: Optional[SudokuBoard] = None
        self.last_solver: Optional[SudokuSolver] = None
        self.last_explanations = []

    def display_menu(self):
        """Display the main menu."""
        print("\n" + "=" * 60)
        print("INTERACTIVE SUDOKU SOLVER")
        print("=" * 60)
        print(f"\nCurrent board: {self.board_size}x{self.board_size} (n={self.size})")

        if self.board is None:
            print("Status: Empty")
        else:
            filled = sum(
                1
                for r in range(self.board_size)
                for c in range(self.board_size)
                if not self.board.is_empty(r, c)
            )
            total = self.board_size * self.board_size
            print(f"Status: {filled}/{total} cells filled")

        print("\nOptions:")
        print("  [1] Set Board Size (n = 2, 3, or 4)")
        print("  [2] Generate Puzzle (with difficulty)")
        print("  [3] Enter Puzzle Manually")
        print("  [4] Solve Current Puzzle")
        print("  [5] View Last Explanations")
        print("  [6] Display Current Board")
        print("  [7] Clear Board")
        print("  [8] Exit")
        print()

    def set_board_size(self):
        """Set the board size."""
        print("\nSelect board size:")
        print("  [2] 4x4 Sudoku")
        print("  [3] 9x9 Sudoku")
        print("  [4] 16x16 Sudoku")

        try:
            choice = input("\nEnter n (2, 3, or 4): ").strip()
            new_size = int(choice)

            if new_size not in [2, 3, 4]:
                print("[X] Invalid size. Must be 2, 3, or 4.")
                return

            self.size = new_size
            self.board_size = new_size * new_size
            self.board = None  # Clear current board
            print(
                f"[OK] Board size set to {self.board_size}x{self.board_size} (n={new_size})"
            )

        except ValueError:
            print("[X] Invalid input. Please enter a number.")

    def generate_puzzle(self):
        """Generate a puzzle."""
        if self.board_size > 16:
            print("[WARN] Generation may take a while for large boards...")

        print("\nSelect difficulty:")
        print("  [1] Easy")
        print("  [2] Medium")
        print("  [3] Hard")

        try:
            choice = input("\nEnter difficulty (1-3): ").strip()
            diff_map = {"1": "easy", "2": "medium", "3": "hard"}

            if choice not in diff_map:
                print("[X] Invalid choice. Using medium.")
                difficulty = "medium"
            else:
                difficulty = diff_map[choice]

            print(f"\nGenerating {difficulty} puzzle...")
            generator = SudokuGenerator(self.size)
            puzzle, stats = generator.generate_with_stats(difficulty)

            self.board = puzzle
            self.last_solver = None
            self.last_explanations = []

            print(f"\n[OK] Generated {difficulty} puzzle!")
            print(f"  Clues: {stats['clues']}")
            print(f"  Empty cells: {stats['empty_cells']}")
            print("\nCurrent board:")
            print(self.board)

        except Exception as e:
            print(f"[X] Error generating puzzle: {e}")

    def enter_puzzle_manually(self):
        """Enter puzzle manually."""
        print(f"\nEnter puzzle as {self.board_size**2} characters")
        print("Use digits 1-9 (and A-P for 16x16)")
        print("Use . or 0 for empty cells")
        print("You can enter all at once or row by row")
        print()

        puzzle_str = ""

        if self.board_size <= 9:
            # For smaller boards, allow single-line input
            print("Enter puzzle (all at once or row by row):")
            puzzle_str = input().strip().replace(" ", "").replace("\n", "")
        else:
            # For larger boards, enter row by row
            print(f"Enter {self.board_size} rows (one per line):")
            rows = []
            for i in range(self.board_size):
                row = input(f"Row {i+1}: ").strip().replace(" ", "")
                if len(row) != self.board_size:
                    print(f"[X] Row must have {self.board_size} characters")
                    return
                rows.append(row)
            puzzle_str = "".join(rows)

        try:
            board = SudokuBoard(self.size)
            board.from_string(puzzle_str)
            self.board = board
            self.last_solver = None
            self.last_explanations = []

            print("\n[OK] Puzzle loaded!")
            print("\nCurrent board:")
            print(self.board)

        except Exception as e:
            print(f"[X] Error loading puzzle: {e}")

    def solve_puzzle(self):
        """Solve the current puzzle."""
        if self.board is None:
            print("[X] No puzzle loaded. Generate or enter a puzzle first.")
            return

        print("\nSolving puzzle...")
        print("=" * 60)

        try:
            solver = SudokuSolver(
                use_mrv=True, use_forward_checking=True, use_prolog=True
            )
            success, solution = solver.solve(self.board)

            self.last_solver = solver
            self.last_explanations = solver.get_explanations()

            if success:
                print("\n[OK] SOLUTION FOUND!")
                print("\n" + "=" * 60)
                print("SOLUTION:")
                print("=" * 60)
                print(solution)

                stats = solver.get_stats()
                print("\n" + "=" * 60)
                print("STATISTICS:")
                print("=" * 60)
                print(f"  Nodes explored: {stats['nodes_explored']}")
                print(f"  Backtracks: {stats['backtracks']}")
                print(f"  Time: {stats['time']:.4f}s")
                print(f"  MRV heuristic: {'ON' if stats['mrv_enabled'] else 'OFF'}")
                print(
                    f"  Forward checking: {'ON' if stats['forward_checking_enabled'] else 'OFF'}"
                )
                print(
                    f"  Prolog validation: {'ON' if stats['prolog_enabled'] else 'OFF'}"
                )

                # Update board to solution
                self.board = solution

            else:
                stats = solver.get_stats()
                print("\n[X] NO SOLUTION EXISTS")
                print(f"\nNodes explored: {stats['nodes_explored']}")
                print(f"Time: {stats['time']:.4f}s")

        except Exception as e:
            print(f"[X] Error solving puzzle: {e}")

    def view_explanations(self):
        """View last solving explanations."""
        if not self.last_explanations:
            print("[X] No explanations available. Solve a puzzle first.")
            return

        print("\n" + "=" * 60)
        print("SOLVING PROCESS EXPLANATIONS")
        print("=" * 60)
        print()

        # Use smart filtering
        total_steps = len(self.last_explanations)
        filtered_steps = filter_key_steps(self.last_explanations)
        filtered_count = len(filtered_steps)

        if total_steps <= 100:
            print(f"({total_steps} steps)\n")
            for exp in filtered_steps:
                print(exp)
        else:
            print(f"({total_steps} total steps, showing {filtered_count} key events)\n")
            for exp in filtered_steps:
                print(exp)

        print("\n" + "=" * 60)

    def display_board(self):
        """Display the current board."""
        if self.board is None:
            print("[X] No puzzle loaded.")
            return

        print("\n" + "=" * 60)
        print("CURRENT BOARD:")
        print("=" * 60)
        print(self.board)

        # Show stats
        filled = sum(
            1
            for r in range(self.board_size)
            for c in range(self.board_size)
            if not self.board.is_empty(r, c)
        )
        total = self.board_size * self.board_size
        print(f"\nFilled: {filled}/{total} cells")

    def clear_board(self):
        """Clear the current board."""
        self.board = None
        self.last_solver = None
        self.last_explanations = []
        print("[OK] Board cleared.")

    def run(self):
        """Run the interactive CLI."""
        print("\n" + "=" * 60)
        print("WELCOME TO INTERACTIVE SUDOKU SOLVER")
        print("=" * 60)
        print("\nFeatures:")
        print("  - Generate puzzles with difficulty levels")
        print("  - Solve with human-style explanations")
        print("  - Prolog constraint validation")
        print("  - MRV heuristic & forward checking")
        print("  - Support for 4x4, 9x9, and 16x16 boards")

        while True:
            self.display_menu()

            try:
                choice = input("Enter choice (1-8): ").strip()

                if choice == "1":
                    self.set_board_size()
                elif choice == "2":
                    self.generate_puzzle()
                elif choice == "3":
                    self.enter_puzzle_manually()
                elif choice == "4":
                    self.solve_puzzle()
                elif choice == "5":
                    self.view_explanations()
                elif choice == "6":
                    self.display_board()
                elif choice == "7":
                    self.clear_board()
                elif choice == "8":
                    print("\n[OK] Goodbye!")
                    break
                else:
                    print("[X] Invalid choice. Please enter 1-8.")

            except KeyboardInterrupt:
                print("\n\n[OK] Interrupted. Goodbye!")
                break
            except EOFError:
                print("\n\n[OK] Goodbye!")
                break


def main():
    """Main entry point."""
    # Check for command-line arguments (backward compatibility)
    if len(sys.argv) > 1:
        # Old-style CLI: python cli.py [n] [puzzle_string]
        print("=" * 60)
        print("Generalized Sudoku Solver - CLI Mode")
        print("=" * 60)
        print("\nNote: For interactive mode, run without arguments")
        print("      python cli.py")
        print()

        size = 3
        if len(sys.argv) > 1:
            try:
                size = int(sys.argv[1])
            except ValueError:
                print(f"Invalid size: {sys.argv[1]}")
                return 1

        board_size = size * size
        print(f"\nBoard size: {board_size}x{board_size} (n={size})")
        print(
            f"Enter puzzle as {board_size**2} characters (use . or 0 for empty cells)"
        )
        print("For boards > 9x9, use A=10, B=11, etc.")
        print()

        if len(sys.argv) > 2:
            puzzle_str = sys.argv[2]
        else:
            print("Enter puzzle:")
            puzzle_str = input().strip()

        try:
            board = SudokuBoard(size)
            board.from_string(puzzle_str)

            print("\nInitial board:")
            print(board)

            print("\nSolving...")
            solver = SudokuSolver(
                use_mrv=True, use_forward_checking=True, use_prolog=True
            )
            success, solution = solver.solve(board)

            if success:
                print("\n[OK] Solution found!")
                print(solution)
                print()
                print(solver.explain_solution(solution))
            else:
                print("\n[X] No solution exists!")
                stats = solver.get_stats()
                print(f"Nodes explored: {stats['nodes_explored']}")
                print(f"Time: {stats['time']:.4f}s")

        except Exception as e:
            print(f"\nError: {e}")
            return 1

        return 0
    else:
        # Interactive mode
        cli = InteractiveCLI()
        cli.run()
        return 0


if __name__ == "__main__":
    sys.exit(main())
