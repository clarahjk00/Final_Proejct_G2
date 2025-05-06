import unittest
import numpy as np
from unittest.mock import patch, MagicMock
from main_code_block import SudokuBoard, SudokuSolver  

class TestSudokuSolver(unittest.TestCase):

    def setUp(self):
        self.board = SudokuBoard()
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
        solver = SudokuSolver(self.board)
        self.assertTrue(solver.solve())
        solved_board = solver.solved_board.board
        self.assertFalse(0 in solved_board)

    def test_unsolvable_board(self):
        self.board.board[0][2] = 5  # duplicate in row
        solver = SudokuSolver(self.board)
        self.assertFalse(solver.solve())

    def test_is_valid_true(self):
        self.assertTrue(self.board.is_valid(0, 2, 4))

    def test_is_valid_false_row(self):
        self.assertFalse(self.board.is_valid(0, 2, 5))

    def test_is_valid_false_col(self):
        self.assertFalse(self.board.is_valid(2, 0, 6))

    def test_is_valid_false_block(self):
        self.assertFalse(self.board.is_valid(1, 2, 9))

    def test_find_empty(self):
        self.assertEqual(self.board.find_empty(), (0, 2))

    def test_display_runs(self):
        try:
            self.board.display()
        except Exception as e:
            self.fail(f"display() raised an exception: {e}")

    def test_solver_no_change_on_solved_board(self):
        solver = SudokuSolver(self.board)
        solver.solve()
        first_solution = solver.solved_board.board.copy()
        solver2 = SudokuSolver(solver.solved_board)
        solver2.solve()
        np.testing.assert_array_equal(first_solution, solver2.solved_board.board)

    def test_empty_board_can_be_processed(self):
        self.board.board = np.zeros((9, 9), dtype=int)
        solver = SudokuSolver(self.board)
        solver.solve()  # test just that it runs


if __name__ == "__main__":
    unittest.main()
