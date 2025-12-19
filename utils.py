"""
Utility functions for Sudoku Solver UI components.
"""

from typing import List


def filter_key_steps(explanations: List[str]) -> List[str]:
    """
    Filter explanations to show only key/important steps.

    This function intelligently filters solving explanations to show:
    - Initialization steps (first 5)
    - All MRV selections (key decisions)
    - Forward checking failures (dead ends)
    - Backtracks (up to 30)
    - Milestone markers (every 50 steps)
    - Final steps (last 5)

    Args:
        explanations: Full list of explanation strings

    Returns:
        Filtered list containing only key steps
    """
    if len(explanations) <= 100:
        return explanations  # Show all if not too many

    key_steps = []
    backtrack_count = 0
    max_backtracks_to_show = 30

    # Always include first few steps (initialization)
    init_steps = min(5, len(explanations))
    key_steps.extend(explanations[:init_steps])

    # Filter middle steps
    for i, exp in enumerate(explanations[init_steps:-5], start=init_steps):
        # Include MRV selections (key decisions)
        if "[MRV]" in exp:
            key_steps.append(exp)
        # Include forward checking failures (dead ends)
        elif "Forward checking failed" in exp:
            key_steps.append(exp)
        # Include backtracks (up to limit)
        elif "Backtracking" in exp:
            backtrack_count += 1
            if backtrack_count <= max_backtracks_to_show:
                key_steps.append(exp)
        # Include milestone steps (every 50 steps)
        elif i % 50 == 0:
            key_steps.append(f"... [Milestone: Step {i+1}] ...")

    # Always include last few steps (solution found)
    key_steps.extend(explanations[-5:])

    return key_steps
