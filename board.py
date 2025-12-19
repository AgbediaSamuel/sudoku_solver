"""
Sudoku Board representation for n^2 x n^2 puzzles
"""

import math
from typing import List, Optional, Set, Tuple


class SudokuBoard:
    """Represents a generalized n^2 x n^2 Sudoku board."""

    def __init__(self, size: int = 3):
        """
        Initialize a Sudoku board.

        Args:
            size: The box size (n). Board will be n^2 x n^2 (e.g., 3 -> 9x9)
        """
        self.n = size
        self.board_size = size * size
        self.board: List[List[int]] = [
            [0] * self.board_size for _ in range(self.board_size)
        ]

    def from_string(self, puzzle: str) -> "SudokuBoard":
        """
        Load board from string representation.

        Args:
            puzzle: String with digits and dots/zeros for empty cells

        Returns:
            Self for chaining
        """
        puzzle = puzzle.replace(".", "0").replace(" ", "").replace("\n", "")

        if len(puzzle) != self.board_size**2:
            raise ValueError(f"Puzzle must have {self.board_size ** 2} characters")

        for i in range(self.board_size):
            for j in range(self.board_size):
                idx = i * self.board_size + j
                val = int(puzzle[idx], 36) if puzzle[idx].isalnum() else 0
                if val > self.board_size:
                    raise ValueError(
                        f"Invalid value {val} for board size {self.board_size}"
                    )
                self.board[i][j] = val

        return self

    def from_list(self, board: List[List[int]]) -> "SudokuBoard":
        """
        Load board from 2D list.

        Args:
            board: 2D list of integers

        Returns:
            Self for chaining
        """
        if len(board) != self.board_size or any(
            len(row) != self.board_size for row in board
        ):
            raise ValueError(f"Board must be {self.board_size}x{self.board_size}")

        self.board = [row[:] for row in board]
        return self

    def get(self, row: int, col: int) -> int:
        """Get value at position."""
        return self.board[row][col]

    def set(self, row: int, col: int, value: int):
        """Set value at position."""
        self.board[row][col] = value

    def is_empty(self, row: int, col: int) -> bool:
        """Check if cell is empty."""
        return self.board[row][col] == 0

    def get_box_index(self, row: int, col: int) -> Tuple[int, int]:
        """Get the top-left corner of the box containing (row, col)."""
        box_row = (row // self.n) * self.n
        box_col = (col // self.n) * self.n
        return box_row, box_col

    def is_valid(self, row: int, col: int, num: int) -> bool:
        """
        Check if placing num at (row, col) is valid.

        Args:
            row: Row index
            col: Column index
            num: Number to place (1 to board_size)

        Returns:
            True if placement is valid
        """
        # Check row
        if num in self.board[row]:
            return False

        # Check column
        if any(self.board[r][col] == num for r in range(self.board_size)):
            return False

        # Check box
        box_row, box_col = self.get_box_index(row, col)
        for r in range(box_row, box_row + self.n):
            for c in range(box_col, box_col + self.n):
                if self.board[r][c] == num:
                    return False

        return True

    def get_candidates(self, row: int, col: int) -> Set[int]:
        """
        Get all valid candidates for a cell.

        Args:
            row: Row index
            col: Column index

        Returns:
            Set of valid numbers
        """
        if not self.is_empty(row, col):
            return set()

        candidates = set(range(1, self.board_size + 1))

        # Remove row conflicts
        candidates -= set(self.board[row])

        # Remove column conflicts
        candidates -= {self.board[r][col] for r in range(self.board_size)}

        # Remove box conflicts
        box_row, box_col = self.get_box_index(row, col)
        for r in range(box_row, box_row + self.n):
            for c in range(box_col, box_col + self.n):
                candidates.discard(self.board[r][c])

        return candidates

    def is_complete(self) -> bool:
        """Check if board is completely filled."""
        return all(
            self.board[r][c] != 0
            for r in range(self.board_size)
            for c in range(self.board_size)
        )

    def is_valid_solution(self) -> bool:
        """Check if current board state is a valid solution."""
        if not self.is_complete():
            return False

        # Check all rows, columns, and boxes
        for i in range(self.board_size):
            # Check row
            if len(set(self.board[i])) != self.board_size:
                return False

            # Check column
            if (
                len({self.board[r][i] for r in range(self.board_size)})
                != self.board_size
            ):
                return False

        # Check all boxes
        for box_r in range(0, self.board_size, self.n):
            for box_c in range(0, self.board_size, self.n):
                box_vals = []
                for r in range(box_r, box_r + self.n):
                    for c in range(box_c, box_c + self.n):
                        box_vals.append(self.board[r][c])
                if len(set(box_vals)) != self.board_size:
                    return False

        return True

    def copy(self) -> "SudokuBoard":
        """Create a deep copy of the board."""
        new_board = SudokuBoard(self.n)
        new_board.board = [row[:] for row in self.board]
        return new_board

    def __str__(self) -> str:
        """String representation of the board."""
        lines = []
        h_line = "+" + ("+".join(["-" * (self.n * 2 + 1)] * self.n)) + "+"

        for i in range(self.board_size):
            if i % self.n == 0:
                lines.append(h_line)

            row_str = "|"
            for j in range(self.board_size):
                if j % self.n == 0 and j > 0:
                    row_str += "|"

                val = self.board[i][j]
                if val == 0:
                    row_str += " ."
                elif val < 10:
                    row_str += f" {val}"
                else:
                    # Use letters for values > 9 (for 16x16, 25x25 boards)
                    row_str += f" {chr(55 + val)}"  # A=10, B=11, etc.

            row_str += " |"
            lines.append(row_str)

        lines.append(h_line)
        return "\n".join(lines)

    def to_string(self) -> str:
        """Convert board to compact string format."""
        result = ""
        for row in self.board:
            for val in row:
                if val == 0:
                    result += "."
                elif val < 10:
                    result += str(val)
                else:
                    result += chr(55 + val)
        return result
