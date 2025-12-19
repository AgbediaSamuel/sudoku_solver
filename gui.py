"""
Sudoku Solver - Enhanced GUI with step-by-step solving and puzzle generation
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from board import SudokuBoard
from generator import SudokuGenerator
from solver import SudokuSolver
from utils import filter_key_steps


class SudokuGUI:
    """Enhanced GUI for the Sudoku Solver."""

    def __init__(self, size: int = 3):
        """
        Initialize the Sudoku GUI.

        Args:
            size: Board size (n for n^2 x n^2 board)
        """
        self.size = size
        self.board_size = size * size
        self.board = SudokuBoard(size)
        self.solver = None
        self.solving = False
        self.cell_size = 50

        # Create main window
        self.root = tk.Tk()
        self.root.title(f"Sudoku Solver - {self.board_size}x{self.board_size}")
        self.root.geometry("1200x750")

        # Cell entries
        self.cells = []

        self._create_widgets()

    def _create_widgets(self):
        """Create UI widgets."""
        # Main container
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Top frame - Controls
        top_frame = ttk.Frame(main_container)
        top_frame.pack(fill=tk.X, pady=(0, 20))

        # Size selector
        size_frame = ttk.LabelFrame(
            top_frame, text="Board Size", padding="10", labelanchor="n"
        )
        size_frame.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(size_frame, text="n =").pack(side=tk.LEFT, padx=(0, 5))
        self.size_var = tk.StringVar(value=str(self.size))
        size_combo = ttk.Combobox(
            size_frame,
            textvariable=self.size_var,
            values=["2", "3", "4"],
            width=5,
            state="readonly",
        )
        size_combo.pack(side=tk.LEFT, padx=(0, 10))
        size_combo.bind("<<ComboboxSelected>>", self._on_size_change)

        # Dynamic label that updates when size changes
        self.size_label = ttk.Label(
            size_frame, text=f"({self.board_size}x{self.board_size})"
        )
        self.size_label.pack(side=tk.LEFT)

        # Generator controls
        gen_frame = ttk.LabelFrame(
            top_frame, text="Generate Puzzle", padding="10", labelanchor="n"
        )
        gen_frame.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(gen_frame, text="Difficulty:").pack(side=tk.LEFT, padx=(0, 5))
        self.difficulty_var = tk.StringVar(value="medium")
        diff_combo = ttk.Combobox(
            gen_frame,
            textvariable=self.difficulty_var,
            values=["easy", "medium", "hard"],
            width=8,
            state="readonly",
        )
        diff_combo.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            gen_frame, text="Generate", command=self._generate_puzzle, width=10
        ).pack(side=tk.LEFT, padx=5)

        # Solver controls
        controls_frame = ttk.LabelFrame(
            top_frame, text="Solver Controls", padding="10", labelanchor="n"
        )
        controls_frame.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Button(
            controls_frame, text="Solve", command=self._solve_puzzle, width=10
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            controls_frame, text="Clear", command=self._clear_board, width=10
        ).pack(side=tk.LEFT, padx=5)

        # Main content area
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left: Board
        board_container = ttk.Frame(content_frame)
        board_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.board_frame = ttk.Frame(board_container)
        self.board_frame.pack(anchor=tk.CENTER, expand=True)

        # Right: Info panel with scrollbar
        info_container = ttk.Frame(content_frame, width=400)
        info_container.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(20, 0))
        info_container.pack_propagate(False)

        ttk.Label(
            info_container, text="Solver Explanations", font=("Arial", 11, "bold")
        ).pack(anchor=tk.W, pady=(0, 10))

        # Add scrollbar
        info_box = ttk.Frame(info_container, borderwidth=1, relief="solid")
        info_box.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(info_box)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.info_text = tk.Text(
            info_box,
            wrap=tk.WORD,
            font=("Courier", 9),
            height=20,
            width=45,
            yscrollcommand=scrollbar.set,
            cursor="arrow",
        )
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.info_text.yview)

        self.info_text.insert(
            "1.0",
            "Welcome to Enhanced Sudoku Solver!\n\n"
            + "Features:\n"
            + "- Generate puzzles with difficulty levels\n"
            + "- Solve with human-style explanations\n"
            + "- Prolog constraint validation\n"
            + "- MRV heuristic & forward checking\n\n"
            + "Getting Started:\n"
            + "- Select board size (n = 2, 3, or 4)\n"
            + "- Choose difficulty and click 'Generate'\n"
            + "- Click 'Solve' to see step-by-step explanations\n\n"
            + "Tips:\n"
            + "- Use 0 or leave blank for empty cells\n"
            + "- For 16x16, use A=10, B=11, etc.\n",
        )
        self.info_text.config(state=tk.DISABLED)

        self._create_board()

    def _create_board(self):
        """Create the Sudoku board grid."""
        # Clear existing board
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        self.cells = []

        # Adjust cell size based on board size
        if self.board_size <= 4:
            font_size = 20
        elif self.board_size <= 9:
            font_size = 16
        else:
            font_size = 12

        # Create grid
        for i in range(self.board_size):
            row = []
            for j in range(self.board_size):
                # Determine border thickness
                top_border = 2 if i % self.size == 0 else 1
                left_border = 2 if j % self.size == 0 else 1
                bottom_border = 2 if i == self.board_size - 1 else 0
                right_border = 2 if j == self.board_size - 1 else 0

                # Create frame for cell
                cell_frame = tk.Frame(
                    self.board_frame,
                    highlightbackground="black",
                    highlightthickness=0,
                    bd=0,
                )
                cell_frame.grid(row=i, column=j, sticky="nsew")

                # Create entry
                entry = tk.Entry(
                    cell_frame,
                    width=2,
                    font=("Arial", font_size, "bold"),
                    justify="center",
                    relief="solid",
                    bd=1,
                )
                entry.pack(
                    padx=(left_border, right_border),
                    pady=(top_border, bottom_border),
                    fill=tk.BOTH,
                    expand=True,
                )

                # Bind validation
                entry.bind(
                    "<KeyRelease>", lambda e, r=i, c=j: self._validate_input(r, c)
                )

                row.append(entry)
            self.cells.append(row)

        # Make grid cells expand
        for i in range(self.board_size):
            self.board_frame.grid_rowconfigure(i, weight=1)
            self.board_frame.grid_columnconfigure(i, weight=1)

    def _validate_input(self, row: int, col: int):
        """Validate user input in a cell."""
        entry = self.cells[row][col]
        value = entry.get().strip().upper()

        if not value:
            return

        # For boards > 9x9, allow letters
        if self.board_size <= 9:
            if not value.isdigit() or int(value) > self.board_size:
                entry.delete(0, tk.END)
        else:
            # Allow digits and letters
            if value.isdigit():
                if int(value) > self.board_size:
                    entry.delete(0, tk.END)
            elif value.isalpha():
                val = ord(value) - 55  # A=10, B=11, etc.
                if val > self.board_size:
                    entry.delete(0, tk.END)
            else:
                entry.delete(0, tk.END)

    def _on_size_change(self, event=None):
        """Handle board size change."""
        new_size = int(self.size_var.get())
        if new_size != self.size:
            self.size = new_size
            self.board_size = new_size * new_size
            self.board = SudokuBoard(new_size)
            self.root.title(f"Sudoku Solver - {self.board_size}x{self.board_size}")
            # Update the size label
            self.size_label.config(text=f"({self.board_size}x{self.board_size})")
            self._create_board()
            self._update_info("Board size changed to {0}x{0}".format(self.board_size))

    def _get_board_from_gui(self) -> SudokuBoard:
        """Extract board state from GUI."""
        board = SudokuBoard(self.size)
        for i in range(self.board_size):
            for j in range(self.board_size):
                value = self.cells[i][j].get().strip().upper()
                if value:
                    if value.isdigit():
                        board.set(i, j, int(value))
                    else:
                        # Letter (A=10, B=11, etc.)
                        board.set(i, j, ord(value) - 55)
        return board

    def _set_board_to_gui(self, board: SudokuBoard, is_solution: bool = False):
        """Display board in GUI."""
        for i in range(self.board_size):
            for j in range(self.board_size):
                value = board.get(i, j)
                entry = self.cells[i][j]
                entry.delete(0, tk.END)

                if value != 0:
                    if value < 10:
                        entry.insert(0, str(value))
                    else:
                        entry.insert(0, chr(55 + value))

                    if is_solution:
                        entry.config(fg="blue")
                    else:
                        entry.config(fg="black")

    def _generate_puzzle(self):
        """Generate a new puzzle."""
        difficulty = self.difficulty_var.get()

        self._update_info(
            f"Generating {difficulty} puzzle for {self.board_size}x{self.board_size}...\n"
        )
        self.root.update_idletasks()

        try:
            generator = SudokuGenerator(self.size)
            puzzle, stats = generator.generate_with_stats(difficulty)

            self._clear_board()
            self._set_board_to_gui(puzzle)

            info = f"[OK] Generated {difficulty} puzzle!\n\n"
            info += f"Board size: {stats['board_size']}x{stats['board_size']}\n"
            info += f"Clues: {stats['clues']}\n"
            info += f"Empty cells: {stats['empty_cells']}\n\n"
            info += "Click 'Solve' to see the solution with explanations!"

            self._update_info(info)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate puzzle: {e}")
            self._update_info(f"Error: {e}")

    def _solve_puzzle(self):
        """Solve the current puzzle with explanations."""
        # Get board from GUI
        try:
            self.board = self._get_board_from_gui()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid board: {e}")
            return

        self._update_info("Solving puzzle with explanations...\n\n")
        self.root.update_idletasks()

        # Solve with explanations (with Prolog validation)
        try:
            solver = SudokuSolver(
                use_mrv=True, use_forward_checking=True, use_prolog=True
            )
            success, solution = solver.solve(self.board)
            self._display_solution(success, solution, solver)
        except Exception as e:
            messagebox.showerror("Error", f"Solving failed: {e}")
            self._update_info(f"Error: {e}")

    def _display_solution(
        self, success: bool, solution: Optional[SudokuBoard], solver: SudokuSolver
    ):
        """Display the solution with explanations."""
        if success:
            self._set_board_to_gui(solution, is_solution=True)

            stats = solver.get_stats()
            explanations = solver.get_explanations()

            # Build info with filtered key steps
            self._display_solution_with_filtered_steps(stats, explanations)
            messagebox.showinfo("Success", f"Puzzle solved in {stats['time']:.4f}s!")
        else:
            stats = solver.get_stats()
            explanations = solver.get_explanations()

            # Use filtered steps for consistency
            filtered_steps = filter_key_steps(explanations)
            total_steps = len(explanations)
            filtered_count = len(filtered_steps)

            info = "[X] NO SOLUTION EXISTS\n"
            info += "=" * 50 + "\n\n"
            info += "STATISTICS:\n"
            info += f"  Nodes explored: {stats['nodes_explored']}\n"
            info += f"  Time: {stats['time']:.4f}s\n\n"
            info += "=" * 50 + "\n\n"

            if total_steps <= 100:
                info += f"SEARCH PROCESS ({total_steps} steps):\n"
                info += "-" * 50 + "\n\n"
                info += "\n".join(explanations)
            else:
                info += f"SEARCH PROCESS ({total_steps} total steps, showing {filtered_count} key events):\n"
                info += "-" * 50 + "\n\n"
                info += "\n".join(filtered_steps)

            self._update_info(info)
            messagebox.showerror("No Solution", "This puzzle has no solution.")

    def _clear_board(self):
        """Clear the board."""
        for i in range(self.board_size):
            for j in range(self.board_size):
                self.cells[i][j].delete(0, tk.END)
                self.cells[i][j].config(fg="black")
        self._update_info("Board cleared.")

    def _update_info(self, text: str):
        """Update info panel."""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert("1.0", text)
        self.info_text.see(tk.END)  # Auto-scroll to bottom
        self.info_text.config(state=tk.DISABLED)

    def _display_solution_with_filtered_steps(self, stats: dict, explanations: list):
        """Display solution with filtered key steps."""
        total_steps = len(explanations)

        # Filter to show only key steps
        filtered_steps = filter_key_steps(explanations)
        filtered_count = len(filtered_steps)

        # Enable text widget for editing
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete("1.0", tk.END)

        # Add statistics header
        self.info_text.insert(tk.END, "[OK] SOLUTION FOUND!\n")
        self.info_text.insert(tk.END, "=" * 50 + "\n\n")
        self.info_text.insert(tk.END, "STATISTICS:\n")
        self.info_text.insert(tk.END, f"  Nodes explored: {stats['nodes_explored']}\n")
        self.info_text.insert(tk.END, f"  Backtracks: {stats['backtracks']}\n")
        self.info_text.insert(tk.END, f"  Time: {stats['time']:.4f}s\n")
        self.info_text.insert(
            tk.END, f"  MRV heuristic: {'ON' if stats['mrv_enabled'] else 'OFF'}\n"
        )
        self.info_text.insert(
            tk.END,
            f"  Forward checking: {'ON' if stats['forward_checking_enabled'] else 'OFF'}\n",
        )
        self.info_text.insert(
            tk.END,
            f"  Prolog validation: {'ON' if stats['prolog_enabled'] else 'OFF'}\n\n",
        )
        self.info_text.insert(tk.END, "=" * 50 + "\n\n")

        # Add solving process
        if total_steps <= 100:
            self.info_text.insert(tk.END, f"SOLVING PROCESS ({total_steps} steps):\n")
            self.info_text.insert(tk.END, "-" * 50 + "\n\n")
            self.info_text.insert(tk.END, "\n".join(explanations))
        else:
            self.info_text.insert(
                tk.END,
                f"SOLVING PROCESS ({total_steps} total steps, showing {filtered_count} key events):\n",
            )
            self.info_text.insert(tk.END, "-" * 50 + "\n\n")
            self.info_text.insert(tk.END, "\n".join(filtered_steps))

        self.info_text.config(state=tk.DISABLED)
        self.info_text.see("1.0")  # Scroll to top

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()


def main():
    """Run the Sudoku GUI."""
    import sys

    size = 3
    if len(sys.argv) > 1:
        try:
            size = int(sys.argv[1])
        except ValueError:
            print(f"Invalid size: {sys.argv[1]}")
            return

    print(f"Starting Enhanced Sudoku Solver GUI ({size*size}x{size*size})...")
    print("Features: Puzzle generation, Prolog validation, step-by-step explanations")
    gui = SudokuGUI(size=size)
    gui.run()


if __name__ == "__main__":
    main()
