"""
Generalized Sudoku Solver using backtracking with heuristics and Prolog integration
"""

import time
from typing import Callable, List, Optional, Tuple

from board import SudokuBoard
from prolog_validator import PrologValidator, is_prolog_available


class SudokuSolver:
    """Solver for generalized n^2 x n^2 Sudoku puzzles."""

    def __init__(
        self,
        use_mrv: bool = True,
        use_forward_checking: bool = True,
        use_prolog: bool = True,
        step_callback: Optional[Callable] = None,
        generate_explanations: bool = True,
    ):
        """
        Initialize the solver.

        Args:
            use_mrv: Use Minimum Remaining Values heuristic
            use_forward_checking: Use forward checking for constraint propagation
            use_prolog: Use Prolog for constraint checking (if available)
            step_callback: Optional callback function for step-by-step mode
            generate_explanations: Generate human-readable explanations (disable for speed)
        """
        self.use_mrv = use_mrv
        self.use_forward_checking = use_forward_checking
        self.step_callback = step_callback
        self.generate_explanations = generate_explanations

        self.nodes_explored = 0
        self.backtrack_count = 0
        self.solve_time = 0.0
        self.explanations = []
        self.paused = False

        # Initialize Prolog validator
        self.prolog_validator = PrologValidator(enable_prolog=use_prolog)
        self.use_prolog = self.prolog_validator.is_available()

        if use_prolog:
            if self.use_prolog:
                self._add_explanation("Prolog constraint checker initialized")
            else:
                error_msg = self.prolog_validator.get_error_message()
                if error_msg:
                    self._add_explanation(
                        f"[WARN] Prolog initialization failed: {error_msg}"
                    )
                else:
                    self._add_explanation(
                        "[WARN] Prolog not available, using Python validation"
                    )

    def solve(self, board: SudokuBoard) -> Tuple[bool, Optional[SudokuBoard]]:
        """
        Solve the Sudoku puzzle.

        Args:
            board: SudokuBoard to solve

        Returns:
            (success, solved_board) tuple
        """
        self.nodes_explored = 0
        self.backtrack_count = 0
        self.explanations = []
        start_time = time.time()

        # Initial explanation
        self._add_explanation(
            f"Starting solver for {board.board_size}x{board.board_size} Sudoku (n={board.n})"
        )
        self._add_explanation(f"MRV heuristic: {'ON' if self.use_mrv else 'OFF'}")
        self._add_explanation(
            f"Forward checking: {'ON' if self.use_forward_checking else 'OFF'}"
        )
        self._add_explanation(
            f"Prolog validation: {'ON' if self.use_prolog else 'OFF'}"
        )
        self._add_explanation("")

        # Work on a copy
        working_board = board.copy()

        # Solve using backtracking
        success = self._backtrack(working_board)

        self.solve_time = time.time() - start_time

        if success:
            self._add_explanation(f"\nSolution found in {self.solve_time:.4f}s!")
            return True, working_board

        self._add_explanation(
            f"\nNo solution exists (explored {self.nodes_explored} nodes)"
        )
        return False, None

    def _backtrack(self, board: SudokuBoard) -> bool:
        """
        Recursive backtracking algorithm with explanations.

        Args:
            board: Current board state

        Returns:
            True if solution found
        """
        self.nodes_explored += 1

        # Check if paused (for step-by-step mode)
        if self.step_callback:
            self.step_callback(
                board, self.explanations[-1] if self.explanations else ""
            )

        # Find next empty cell
        cell = self._select_unassigned_variable(board)

        if cell is None:
            # No empty cells, puzzle solved
            if board.is_valid_solution():
                # Optionally verify with Prolog
                if self.use_prolog:
                    prolog_valid = self._prolog_validate_constraints(board)
                    if prolog_valid:
                        self._add_explanation(
                            "All cells filled - solution validated by Prolog!"
                        )
                    else:
                        self._add_explanation("All cells filled - solution is valid!")
                else:
                    self._add_explanation("All cells filled - solution is valid!")
                return True
            return False

        row, col = cell

        # Get candidates for this cell
        candidates = self._get_candidates_with_explanation(board, row, col)

        if len(candidates) == 0:
            self._add_explanation(
                f"Cell ({row},{col}) has no valid candidates - backtracking"
            )
            return False

        # Try each candidate
        for num in candidates:
            # Explain the move
            self._add_explanation(
                f"-> Trying {self._format_value(num, board.n)} at ({row},{col})"
            )

            # Place number
            board.set(row, col, num)

            # Forward checking: check if this creates impossible state
            if self.use_forward_checking and not self._is_consistent(board):
                self._add_explanation(
                    "  [X] Forward checking failed - creates dead end"
                )
                board.set(row, col, 0)
                self.backtrack_count += 1
                continue

            self._add_explanation("  Move valid - continuing search")

            # Recurse
            if self._backtrack(board):
                return True

            # Backtrack
            self._add_explanation(f"  <- Backtracking from ({row},{col})")
            board.set(row, col, 0)
            self.backtrack_count += 1

        return False

    def _select_unassigned_variable(
        self, board: SudokuBoard
    ) -> Optional[Tuple[int, int]]:
        """
        Select next empty cell to fill with explanation.

        Uses MRV (Minimum Remaining Values) heuristic if enabled.

        Args:
            board: Current board state

        Returns:
            (row, col) of next cell, or None if board is complete
        """
        if not self.use_mrv:
            # Simple: return first empty cell
            for r in range(board.board_size):
                for c in range(board.board_size):
                    if board.is_empty(r, c):
                        return (r, c)
            return None

        # MRV: select cell with fewest candidates
        min_candidates = board.board_size + 1
        best_cell = None
        best_candidates = []

        # Python MRV implementation
        for r in range(board.board_size):
            for c in range(board.board_size):
                if board.is_empty(r, c):
                    candidates = board.get_candidates(r, c)
                    num_candidates = len(candidates)

                    if num_candidates == 0:
                        # Dead end
                        return (r, c)

                    if num_candidates < min_candidates:
                        min_candidates = num_candidates
                        best_cell = (r, c)
                        best_candidates = candidates

        if best_cell:
            r, c = best_cell
            cand_str = ", ".join(
                [self._format_value(v, board.n) for v in best_candidates]
            )
            self._add_explanation(
                f"\n[MRV] Selected cell ({r},{c}) with {min_candidates} candidates: [{cand_str}]"
            )

        return best_cell

    def _get_candidates_with_explanation(
        self, board: SudokuBoard, row: int, col: int
    ) -> List[int]:
        """Get candidates and optionally validate with Prolog."""
        candidates = board.get_candidates(row, col)

        # Double-check with Prolog if available
        if self.use_prolog:
            prolog_candidates = self._prolog_get_candidates(board, row, col)
            if prolog_candidates is not None and set(candidates) != set(
                prolog_candidates
            ):
                self._add_explanation(
                    f"  [WARN] Prolog found different candidates: {prolog_candidates}"
                )

        return candidates

    def _prolog_validate_constraints(self, board: SudokuBoard) -> bool:
        """
        Use Prolog to validate board constraints (demonstration of Prolog integration).
        Called once at the end to verify the solution.

        Args:
            board: Board to validate

        Returns:
            True if board is valid according to Prolog rules
        """
        if not self.use_prolog:
            return True

        board_list = [list(board.board[r]) for r in range(board.board_size)]
        return self.prolog_validator.validate_board(
            board_list, board.n, board.board_size
        )

    def _prolog_get_candidates(
        self, board: SudokuBoard, row: int, col: int
    ) -> Optional[List[int]]:
        """Get possible values using Prolog."""
        if not self.use_prolog:
            return None

        board_list = [list(board.board[r]) for r in range(board.board_size)]
        return self.prolog_validator.get_candidates(
            board_list, row, col, board.n, board.board_size
        )

    def _is_consistent(self, board: SudokuBoard) -> bool:
        """
        Check if current board state is consistent.

        Args:
            board: Current board state

        Returns:
            True if consistent
        """
        for r in range(board.board_size):
            for c in range(board.board_size):
                if board.is_empty(r, c):
                    if len(board.get_candidates(r, c)) == 0:
                        return False
        return True

    def _add_explanation(self, text: str):
        """Add an explanation message (only if enabled)."""
        if self.generate_explanations:
            self.explanations.append(text)

    def _format_value(self, value: int, n: int) -> str:
        """Format a cell value for display."""
        if value == 0:
            return "."
        if value <= 9:
            return str(value)
        # For 16x16 and larger, use letters
        return chr(ord("A") + value - 10)

    def get_stats(self) -> dict:
        """Get solving statistics."""
        return {
            "nodes_explored": self.nodes_explored,
            "backtracks": self.backtrack_count,
            "time": self.solve_time,
            "mrv_enabled": self.use_mrv,
            "forward_checking_enabled": self.use_forward_checking,
            "prolog_enabled": self.use_prolog,
        }

    def get_explanations(self) -> List[str]:
        """Get all explanations generated during solving."""
        return self.explanations

    def explain_solution(self, board: SudokuBoard) -> str:
        """
        Generate explanation of the solving process.

        Args:
            board: Solved board

        Returns:
            Human-readable explanation
        """
        stats = self.get_stats()

        explanation = f"Sudoku Solver Statistics:\n"
        explanation += (
            f"  Board size: {board.board_size}x{board.board_size} (n={board.n})\n"
        )
        explanation += f"  Nodes explored: {stats['nodes_explored']}\n"
        explanation += f"  Backtracks: {stats['backtracks']}\n"
        explanation += f"  Time taken: {stats['time']:.4f}s\n"
        explanation += (
            f"  MRV heuristic: {'Enabled' if stats['mrv_enabled'] else 'Disabled'}\n"
        )
        explanation += f"  Forward checking: {'Enabled' if stats['forward_checking_enabled'] else 'Disabled'}\n"
        explanation += f"  Prolog validation: {'Enabled' if stats['prolog_enabled'] else 'Disabled'}\n"

        return explanation
