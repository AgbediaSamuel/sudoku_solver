"""
Sudoku Solver - Test Suite
"""

from board import SudokuBoard
from solver import SudokuSolver


def test_4x4():
    """Test 4x4 Sudoku."""
    print("=" * 60)
    print("Test 1: 4x4 Sudoku")
    print("=" * 60)

    # Valid 4x4 with unique solution: 1234/3412/2143/4321
    puzzle = "1.3...1...4.4.2."
    board = SudokuBoard(2).from_string(puzzle)

    print("Initial board:")
    print(board)

    solver = SudokuSolver()
    success, solution = solver.solve(board)

    if success:
        print("\n[OK] Solution:")
        print(solution)
        print(solver.explain_solution(solution))
        assert solution.is_valid_solution(), "Solution is invalid!"
    else:
        print("\n[X] Failed to solve")
        return False

    return True


def test_9x9_easy():
    """Test easy 9x9 Sudoku."""
    print("\n" + "=" * 60)
    print("Test 2: 9x9 Sudoku (Easy)")
    print("=" * 60)

    puzzle = (
        "53..7....6..195....98....6.8...6...34..8.3..17...2...6."
        "6....28....419..5....8..79"
    )
    board = SudokuBoard(3).from_string(puzzle)

    print("Initial board:")
    print(board)

    solver = SudokuSolver()
    success, solution = solver.solve(board)

    if success:
        print("\n[OK] Solution:")
        print(solution)
        print(solver.explain_solution(solution))
        assert solution.is_valid_solution(), "Solution is invalid!"
    else:
        print("\n[X] Failed to solve")
        return False

    return True


def test_9x9_hard():
    """Test hard 9x9 Sudoku."""
    print("\n" + "=" * 60)
    print("Test 3: 9x9 Sudoku (Hard)")
    print("=" * 60)

    # World's hardest Sudoku
    puzzle = (
        "8..........36......7..9.2...5...7.......457.....1...3..."
        "1....68..85...1..9....4.."
    )
    board = SudokuBoard(3).from_string(puzzle)

    print("Initial board:")
    print(board)

    solver = SudokuSolver()
    success, solution = solver.solve(board)

    if success:
        print("\n[OK] Solution:")
        print(solution)
        print(solver.explain_solution(solution))
        assert solution.is_valid_solution(), "Solution is invalid!"
    else:
        print("\n[X] Failed to solve")
        return False

    return True


def test_16x16():
    """Test 16x16 Sudoku."""
    print("\n" + "=" * 60)
    print("Test 4: 16x16 Sudoku")
    print("=" * 60)

    # 16x16 with enough clues for reasonable solve time
    # This is a partially filled 16x16 with strategic clues
    puzzle = (
        "1234567890ABCDEF"
        + "." * 16
        + "." * 16
        + "." * 16
        + "." * 16
        + "." * 16
        + "." * 16
        + "." * 16
        + "." * 16
        + "." * 16
        + "." * 16
        + "." * 16
        + "." * 16
        + "." * 16
        + "." * 16
        + "FEDCBA0987654321"
    )

    board = SudokuBoard(4).from_string(puzzle)

    print("Initial board (first and last rows filled):")
    print(board)

    print("\nSolving 16x16 puzzle (this may take 10-30 seconds)...")
    solver = SudokuSolver()
    success, solution = solver.solve(board)

    if success:
        print("\n[OK] Solution:")
        print(solution)
        print(solver.explain_solution(solution))
        assert solution.is_valid_solution(), "Solution is invalid!"
    else:
        print("\n[X] Failed to solve")
        stats = solver.get_stats()
        print(f"Nodes explored: {stats['nodes_explored']}")
        print(f"Time: {stats['time']:.4f}s")
        return False

    return True


def test_heuristics():
    """Compare solver with and without heuristics."""
    print("\n" + "=" * 60)
    print("Test 5: Heuristic Comparison")
    print("=" * 60)

    puzzle = (
        "53..7....6..195....98....6.8...6...34..8.3..17...2...6."
        "6....28....419..5....8..79"
    )

    # Without heuristics
    print("\nSolving WITHOUT heuristics...")
    board1 = SudokuBoard(3).from_string(puzzle)
    solver1 = SudokuSolver(use_mrv=False, use_forward_checking=False)
    success1, _ = solver1.solve(board1)
    stats1 = solver1.get_stats()

    # With heuristics
    print("Solving WITH heuristics...")
    board2 = SudokuBoard(3).from_string(puzzle)
    solver2 = SudokuSolver(use_mrv=True, use_forward_checking=True)
    success2, _ = solver2.solve(board2)
    stats2 = solver2.get_stats()

    print("\nResults:")
    print(
        f"  Without heuristics: {stats1['nodes_explored']} nodes, "
        f"{stats1['time']:.4f}s"
    )
    print(
        f"  With heuristics:    {stats2['nodes_explored']} nodes, "
        f"{stats2['time']:.4f}s"
    )

    if stats1["nodes_explored"] > 0:
        speedup = stats1["nodes_explored"] / stats2["nodes_explored"]
        print(f"  Speedup: {speedup:.2f}x fewer nodes explored")

    return success1 and success2


def test_heuristic_breakdown():
    """Detailed comparison of different heuristic combinations."""
    print("\n" + "=" * 60)
    print("Test 6: Detailed Heuristic Breakdown")
    print("=" * 60)

    puzzle = (
        "53..7....6..195....98....6.8...6...34..8.3..17...2...6."
        "6....28....419..5....8..79"
    )

    print("\nTesting different heuristic combinations on 9x9 Easy:")
    print("-" * 60)

    configs = [
        ("Naive Backtracking", False, False, False),
        ("MRV Only", True, False, False),
        ("Forward Checking Only", False, True, False),
        ("MRV + Forward Checking", True, True, False),
        ("Full (MRV + FC + Prolog)", True, True, True),
    ]

    results = []
    baseline_nodes = None

    for name, use_mrv, use_fc, use_prolog in configs:
        print(f"\n{name}...")
        board = SudokuBoard(3).from_string(puzzle)
        solver = SudokuSolver(
            use_mrv=use_mrv,
            use_forward_checking=use_fc,
            use_prolog=use_prolog,
            generate_explanations=False,  # Disable for speed
        )
        success, _ = solver.solve(board)
        stats = solver.get_stats()

        if baseline_nodes is None:
            baseline_nodes = stats["nodes_explored"]

        if stats["nodes_explored"] > 0:
            speedup = baseline_nodes / stats["nodes_explored"]
        else:
            speedup = 0

        results.append((name, stats, speedup, success))

        print(
            f"  Nodes: {stats['nodes_explored']:5d} | "
            f"Backtracks: {stats['backtracks']:5d} | "
            f"Time: {stats['time']:.4f}s | "
            f"Speedup: {speedup:.2f}x"
        )

    # Summary table
    print("\n" + "=" * 60)
    print("SUMMARY TABLE")
    print("=" * 60)
    print(
        f"{'Configuration':<30} {'Nodes':>8} {'Backtracks':>12} "
        f"{'Time':>8} {'Speedup':>8}"
    )
    print("-" * 60)

    for name, stats, speedup, success in results:
        status = "[OK]" if success else "[X]"
        print(
            f"{status} {name:<28} {stats['nodes_explored']:>8} "
            f"{stats['backtracks']:>12} {stats['time']:>8.4f}s "
            f"{speedup:>7.2f}x"
        )

    print("=" * 60)

    return all(success for _, _, _, success in results)


def run_all_tests():
    """Run all test cases."""
    print("\n" + "=" * 60)
    print("SUDOKU SOLVER TEST SUITE")
    print("=" * 60 + "\n")

    tests = [
        ("4x4 Sudoku", test_4x4),
        ("9x9 Easy", test_9x9_easy),
        ("9x9 Hard", test_9x9_hard),
        ("16x16 Sudoku", test_16x16),
        ("Heuristic Comparison", test_heuristics),
        ("Heuristic Breakdown", test_heuristic_breakdown),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[X] Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, result in results:
        status = "[OK] PASS" if result else "[X] FAIL"
        print(f"{status}: {name}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
