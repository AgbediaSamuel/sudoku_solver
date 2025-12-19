"""
Generalized Sudoku Solver - CS152 Final Project

A generalized Sudoku solver that works with n^2 x n^2 boards using
backtracking with constraint propagation and heuristics.
"""

from .board import SudokuBoard
from .solver import SudokuSolver

__all__ = ["SudokuSolver", "SudokuBoard"]
