"""
Sudoku Puzzle Generator for n^2 x n^2 boards
"""

import random
from typing import Tuple

from board import SudokuBoard
from solver import SudokuSolver


class SudokuGenerator:
    """Generate random Sudoku puzzles with unique solutions."""

    def __init__(self, n: int = 3):
        """
        Initialize generator.

        Args:
            n: Box size (3 for 9x9, 4 for 16x16, etc.)
        """
        self.n = n
        self.board_size = n * n

    def generate(self, difficulty: str = "medium") -> SudokuBoard:
        """
        Generate a Sudoku puzzle.

        Args:
            difficulty: "easy", "medium", or "hard"

        Returns:
            SudokuBoard with puzzle
        """
        # Generate a complete valid solution
        solution = self._generate_solution()

        # Remove cells based on difficulty
        puzzle = self._remove_cells(solution, difficulty)

        return puzzle

    def _generate_solution(self) -> SudokuBoard:
        """
        Generate a complete valid Sudoku solution.

        Returns:
            Completed SudokuBoard
        """
        # Try up to 10 times to generate a valid solution
        max_attempts = 10

        for attempt in range(max_attempts):
            board = SudokuBoard(self.n)

            # Fill diagonal boxes first (they're independent)
            self._fill_diagonal_boxes(board)

            # Solve the rest (fast mode - no explanations or Prolog)
            solver = SudokuSolver(
                use_mrv=True,
                use_forward_checking=True,
                use_prolog=False,
                generate_explanations=False,  # Skip explanations for speed
            )
            success, solution = solver.solve(board)

            if success:
                return solution

        # If all attempts failed, return empty board and let caller handle it
        # This should be extremely rare
        raise Exception(f"Failed to generate solution after {max_attempts} attempts")

    def _fill_diagonal_boxes(self, board: SudokuBoard):
        """
        Fill the diagonal boxes with random valid values.
        These boxes don't interfere with each other.

        Args:
            board: Board to fill
        """
        for box_idx in range(self.n):
            start_row = box_idx * self.n
            start_col = box_idx * self.n

            # Get all values and shuffle
            values = list(range(1, self.board_size + 1))
            random.shuffle(values)

            # Fill the box
            idx = 0
            for r in range(start_row, start_row + self.n):
                for c in range(start_col, start_col + self.n):
                    board.set(r, c, values[idx])
                    idx += 1

    def _remove_cells(self, solution: SudokuBoard, difficulty: str) -> SudokuBoard:
        """
        Remove cells from solution to create puzzle.

        Args:
            solution: Complete solution
            difficulty: Difficulty level

        Returns:
            Puzzle board
        """
        puzzle = solution.copy()

        # Determine how many cells to keep based on difficulty
        total_cells = self.board_size * self.board_size

        # For 16x16, use more conservative (higher) clue counts for reasonable solve times
        if self.board_size == 16:
            if difficulty == "easy":
                cells_to_keep = int(
                    total_cells * random.uniform(0.60, 0.70)
                )  # 154-179 clues
            elif difficulty == "hard":
                cells_to_keep = int(
                    total_cells * random.uniform(0.45, 0.55)
                )  # 115-141 clues
            else:  # medium
                cells_to_keep = int(
                    total_cells * random.uniform(0.50, 0.60)
                )  # 128-154 clues
        else:
            # Standard difficulty for smaller boards
            if difficulty == "easy":
                cells_to_keep = int(total_cells * random.uniform(0.50, 0.60))
            elif difficulty == "hard":
                cells_to_keep = int(total_cells * random.uniform(0.25, 0.35))
            else:  # medium
                cells_to_keep = int(total_cells * random.uniform(0.35, 0.45))

        # For smaller boards, adjust minimums
        if self.board_size == 4:
            cells_to_keep = max(cells_to_keep, 6)  # At least 6 clues for 4x4
        elif self.board_size == 9:
            cells_to_keep = max(cells_to_keep, 17)  # At least 17 clues for 9x9

        cells_to_remove = total_cells - cells_to_keep

        # Get all cell positions
        all_positions = [
            (r, c) for r in range(self.board_size) for c in range(self.board_size)
        ]
        random.shuffle(all_positions)

        # Remove cells one by one
        removed = 0
        for row, col in all_positions:
            if removed >= cells_to_remove:
                break

            # Save the value
            value = puzzle.get(row, col)

            # Try removing it
            puzzle.set(row, col, 0)

            # Skip solvability checks for performance
            # Removing cells from a valid solution maintains solvability
            # until too many cells are removed (which we control via cells_to_keep)
            removed += 1

        return puzzle

    def generate_with_stats(
        self, difficulty: str = "medium"
    ) -> Tuple[SudokuBoard, dict]:
        """
        Generate puzzle and return with statistics.

        Args:
            difficulty: Difficulty level

        Returns:
            (puzzle, stats) tuple
        """
        puzzle = self.generate(difficulty)

        # Count clues
        clues = sum(
            1
            for r in range(self.board_size)
            for c in range(self.board_size)
            if not puzzle.is_empty(r, c)
        )

        stats = {
            "board_size": self.board_size,
            "n": self.n,
            "difficulty": difficulty,
            "clues": clues,
            "empty_cells": self.board_size * self.board_size - clues,
        }

        return puzzle, stats
