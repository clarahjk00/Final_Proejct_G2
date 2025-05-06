import unittest
import numpy as np
from your_module_name import SudokuBoard, SudokuSolver  # Replace with actual module name if needed

class TestSudokuSolver(unittest.TestCase):

    def setUp(self):
        """Set up a test Sudoku board with a known solvable puzzle."""
        self.board = SudokuBoard()
        # A known solvable puzzle (0 = empty)
        self.board.board = np.array([
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ])

    def test_solver_solves_correctly(self):
        """Test that the solver returns True and fills the board correctly."""
        solver = SudokuSolver(self.board)
        success = solver.solve()
        self.assertTrue(success, "Solver failed on a known solvable puzzle")

        # Check that the board has no empty cells
        for row in solver.solved_board.board:
            self.assertNotIn(0, row, "Solver left empty cells in the solution")

        # Check that the board is valid
        for i in range(9):
            for j in range(9):
                num = solver.solved_board.board[i, j]
                solver.solved_board.board[i, j] = 0  # temporarily clear to validate
                self.assertTrue(solver.solved_board.is_valid(i, j, num), f"Invalid placement at ({i},{j})")
                solver.solved_board.board[i, j] = num  # restore

if __name__ == '__main__':
    unittest.main()
