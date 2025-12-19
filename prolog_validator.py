"""
Prolog integration wrapper for Sudoku constraint validation.
"""

import os
from typing import List, Optional

# Try to import Prolog - gracefully degrade if not available
try:
    from pyswip import Prolog

    PROLOG_AVAILABLE = True
except ImportError:
    PROLOG_AVAILABLE = False
    Prolog = None


class PrologValidator:
    """Wrapper for Prolog constraint validation."""

    def __init__(self, enable_prolog: bool = True):
        """
        Initialize Prolog validator.

        Args:
            enable_prolog: Whether to enable Prolog (if available)
        """
        self.enabled = enable_prolog and PROLOG_AVAILABLE
        self.prolog = None
        self.error_message = None

        if self.enabled:
            try:
                self.prolog = Prolog()
                # Load Prolog rules
                rules_path = os.path.join(os.path.dirname(__file__), "sudoku_rules.pl")
                if os.path.exists(rules_path):
                    self.prolog.consult(rules_path)
                else:
                    self.enabled = False
                    self.error_message = "Prolog rules file not found"
            except Exception as e:
                self.enabled = False
                self.error_message = str(e)

    def is_available(self) -> bool:
        """Check if Prolog validation is available and enabled."""
        return self.enabled and self.prolog is not None

    def get_error_message(self) -> Optional[str]:
        """Get error message if initialization failed."""
        return self.error_message

    def validate_board(
        self, board_list: List[List[int]], n: int, board_size: int
    ) -> bool:
        """
        Validate entire board using Prolog constraints.

        Args:
            board_list: 2D list representation of board
            n: Box size (n x n boxes in an n^2 x n^2 board)
            board_size: Size of board (n^2)

        Returns:
            True if board is valid according to Prolog rules
        """
        if not self.is_available():
            return True  # Fall back to Python validation

        try:
            query = f"valid_board({board_list}, {n}, {board_size})"
            results = list(self.prolog.query(query))
            return len(results) > 0
        except Exception:
            return True  # Fall back on error

    def get_candidates(
        self, board_list: List[List[int]], row: int, col: int, n: int, board_size: int
    ) -> Optional[List[int]]:
        """
        Get possible values for a cell using Prolog.

        Args:
            board_list: 2D list representation of board
            row: Row index
            col: Column index
            n: Box size
            board_size: Size of board

        Returns:
            List of possible values, or None if Prolog unavailable
        """
        if not self.is_available():
            return None

        try:
            query = (
                f"possible_values({board_list}, {row}, {col}, " f"{n}, {board_size}, X)"
            )
            results = list(self.prolog.query(query))
            if results:
                return results[0]["X"]
        except Exception:
            pass
        return None


def is_prolog_available() -> bool:
    """Check if pyswip/Prolog is available on the system."""
    return PROLOG_AVAILABLE
