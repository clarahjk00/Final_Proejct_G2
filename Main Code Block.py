# Main Code Block
import time
import copy
import numpy as np
# import cv2
# import matplotlib.pyplot as plt
# from PIL import Image
# import pytesseract


class SudokuBoard:
    """
    Class representing a Sudoku board.
    """
    def __init__(self):
        """
        Initialize the Sudoku board (9x9 grid).
        """
        self.board = np.zeros((9, 9), dtype=int)                       # Create a 9x9 grid for the Sudoku board
        self.original = np.zeros((9, 9), dtype=bool)                   # Keep track of original numbers


    def load_user_input(self):
        """
        Prompt the user to input Sudoku row by row.
        """
        print("Enter your sudoku row by row.")
        print("Use 0 or . for empty cells.")
        print("=" * 35)                                                # Separator for better readability

        for i in range(9):
            valid_input = False
            while not valid_input:
                row_input = input(f"Enter row {i + 1} (9 digits): ")
                row_input = row_input.replace(" ", "").replace(".","0") # Remove spaces and replace '.' with '0'

                if len(row_input) !=9:
                    print("Error: Entered row must be 9 digits long.")
                    continue

                try:
                    row = [int(cell) for cell in row_input]             # Convert each character to an integer
                    if not all(0 <= cell <= 9 for cell in row):
                        print("Error: Digits must be between 0 and 9.")
                        continue

                    valid_input = True
                    self.board[i] = row                                 # Save the row to the board

                    for j in range(9):
                        if row[j] != 0:                                 # If the cell is not empty, mark it as original
                            self.original[i][j] = True

                except ValueError:
                    print("Error: Invalid input. Please enter digits only.")
        
        print("=" * 35)
        print("\nSudoku board loaded successfully.\n")
        print("=" * 35)
        self.display()                                                  # Display the loaded Sudoku board


    def display(self):
        """
        Print the Sudoku board in a readable format.
        """
        print("-" * 29)
        for i in range(9):
            row = ""
            for j in range(9):
                if self.board[i][j] == 0:
                    row += " . "                                        # Use '.' for empty cells
                else:
                    row += f" {self.board[i][j]} "

                if (j + 1) % 3 == 0 and j != 8:
                    row += "|"                                          # Add vertical separator every 3 columns
            print(row)

            if (i + 1) % 3 == 0:
                print("-" * 29)                                         # Add horizontal separator every 3 rows


    def is_valid(self, row, col, num):
        """
        Check the validity of position for number in Sudoku board.

        Args:
            row (int): Row index (0-8).
            col (int): Column index (0-8).
            num (int): Number to check (1-9).
        """
        for i in range(9):
            if self.board[i, col] == num:                               # Check the row
                return False
            
        for j in range(9):
            if self.board[row, j] == num:                               # Check the column
                return False
            
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)

        for i in range(start_row, start_row + 3):                       # Check the 3x3 subgrid
            for j in range(start_col, start_col + 3):
                if self.board[i, j] == num:
                    return False
        return True
    

    def find_empty(self):
        """
        Find an empty cell in the Sudoku board.

        Returns:
            tuple: (row, col) of the empty cell, or None if no empty cell is found.
        """
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return (i, j)
        return None



class SudokuSolver:
    """
    Class to solve the Sudoku puzzle using backtracking.
    """



def main():
    """
    Main function to run the code.
    This function provides a menu for the user to load Sudoku from manual input or image.
    """

    board = SudokuBoard()  # Create a SudokuBoard object

    while True:
        print("\nSudoku Solver")
        print("1. Load Sudoku from manual input")
        # print("2. Load Sudoku from image")
        # print("3. Solve Sudoku")
        print("4. Quit")

        choice = input("\nEnter your choice: ")

        if choice == '1':
            print("=" * 35)
            board.load_user_input()  # Load Sudoku from user input
            print("=" * 35)

        # elif choice == '2':

        # elif choice == '3':
            
        elif choice == '4':
            print("=" * 35)
            print("\nExiting the program.")
            print("")
            print("=" * 35)
            break

        else:
            print("Error: Invalid choice. Please try again.")
            continue


if __name__ == "__main__":
    main()  # Run the main function