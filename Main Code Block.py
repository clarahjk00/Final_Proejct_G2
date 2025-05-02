# Main Code Block
import time
import copy
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import pytesseract


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

    def load_from_image(self, image_path):
        """
        Load a Sudoku puzzle from an image file.
        Applies preprocessing, perspective correction, splits grid, and uses OCR to detect digits.
        """
        print(f"Loading puzzle from image: {image_path}")

        #load the image from disk
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not open or find the image at {image_path}")
            return False

        #convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        #apply Gaussian blur to reduce noise and improve thresholding
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)

        #apply adaptive thresholding to get a binary image with inverted colors
        thresh = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  #use a weighted sum of neighborhood values
            cv2.THRESH_BINARY_INV,           #invert the colors: digits become white
            11, 2                            #block size and constant for adaptive threshold
        )

        #detect contours in the binary image
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            print("Error: No contours found in the image.")
            return False

        #select the largest contour, assuming it is the Sudoku grid
        largest_contour = max(contours, key=cv2.contourArea)

        #approximate the contour to a 4-point polygon
        peri = cv2.arcLength(largest_contour, True)
        approx = cv2.approxPolyDP(largest_contour, 0.02 * peri, True)

        #check if the polygon has exactly 4 corners
        if len(approx) != 4:
            print(f"Error: Could not find a proper grid (found {len(approx)} points instead of 4).")
            return False

        #try to apply a perspective transform to get a top-down view of the grid
        try:
            grid_image = self._apply_perspective_transform(gray, approx)
        except Exception as e:
            print(f"Error during perspective transform: {e}")
            return False

        #try to split the corrected grid image into 81 cell images
        try:
            cell_images = self._split_grid(grid_image)
        except Exception as e:
            print(f"Error splitting grid into cells: {e}")
            return False

        # Initialize the board and marker for original (pre-filled) cells
        self.board = np.zeros((9, 9), dtype=int)
        self.original_cells = np.zeros((9, 9), dtype=bool)

        #loop through each of the 81 cells to detect digits
        for i in range(9):
            for j in range(9):
                cell_idx = i * 9 + j
                try:
                    #recognize digit in the current cell image
                    digit = self._recognize_digit(cell_images[cell_idx])
                    self.board[i, j] = digit
                    if digit != 0:
                        # Mark original clues (pre-filled digits)
                        self.original_cells[i, j] = True
                except Exception as e:
                    print(f"Warning: Failed to recognize digit at cell ({i}, {j}): {e}")
                    self.board[i, j] = 0  # Default to empty if recognition fails

        #display the final loaded board
        print("\nLoaded Sudoku puzzle from image:")
        self.display()
        return True
    
     def _apply_perspective_transform(self, image, contour):
        """Apply perspective transform to get a top-down view of the grid"""
        # Find the corners of the grid
        rect = self._order_points(contour.reshape(len(contour), 2))
        
        # Define the destination points for the transform (a square)
        side_length = 900  # The target size of our grid
        dst = np.array([
            [0, 0],
            [side_length - 1, 0],
            [side_length - 1, side_length - 1],
            [0, side_length - 1]
        ], dtype="float32")
        
        # Calculate the perspective transform matrix and apply it
        transform_matrix = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, transform_matrix, (side_length, side_length))
        
        return warped
    
    def _order_points(self, pts):
        """Order points in top-left, top-right, bottom-right, bottom-left order"""
        # Sort by sum of coordinates to get top-left and bottom-right
        s = pts.sum(axis=1)
        top_left = pts[np.argmin(s)].astype("float32")
        bottom_right = pts[np.argmax(s)].astype("float32")
        
        # Sort by difference of coordinates to get top-right and bottom-left
        diff = np.diff(pts, axis=1)
        top_right = pts[np.argmin(diff)].astype("float32")
        bottom_left = pts[np.argmax(diff)].astype("float32")
        
        return np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.float32)
    
    def _split_grid(self, grid_image):
        """Split the Sudoku grid into 81 individual cells"""
        cell_images = []
        cell_size = grid_image.shape[0] // 9
        
        for i in range(9):
            for j in range(9):
                # Extract cell with some margin to avoid grid lines
                margin = int(cell_size * 0.1)
                x = j * cell_size + margin
                y = i * cell_size + margin
                width = cell_size - 2 * margin
                height = cell_size - 2 * margin
                
                cell = grid_image[y:y+height, x:x+width]
                cell_images.append(cell)
        
        return cell_images
    
    def _recognize_digit(self, cell_image):
        """Recognize digit in a Sudoku cell using OCR"""
        try:
            # Thresholding to make the digit clearer
            _, thresh = cv2.threshold(cell_image, 128, 255, cv2.THRESH_BINARY_INV)
            
            # Check if cell is mostly empty (no digit)
            if np.sum(thresh) / 255 < cell_image.size * 0.1:
                return 0
            
            # Add padding around the digit
            padded = cv2.copyMakeBorder(thresh, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=0)
            
            # Use pytesseract to recognize the digit
            config = '--psm 10 --oem 3 -c tessedit_char_whitelist=123456789'
            digit_text = pytesseract.image_to_string(padded, config=config).strip()
            
            # Try to parse the digit
            try:
                digit = int(digit_text)
                if 1 <= digit <= 9:
                    return digit
            except (ValueError, IndexError):
                pass
            
            return 0  # Return 0 if no valid digit was recognized
        except Exception as e:
            print(f"OCR failed: {e}")
            print("Returning 0 for this cell. Consider using manual input instead.")
            return 0

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

    def __init__(self, sudoku_board):
        """Initialize with a SodokuBoard object."""
        self.board = sudoku_board
        self.solved_board = None
        self.solving_time = 0

    def solve(self):
        """Solve the Sudoku puzzle using backtracking."""

        self.solved_board = copy.deepcopy(self.board) #creates a copy of the board to solve
        start_time = time.time() #start timing
        success = self._solve_backtracking() #call the recursive backtracking solver
        self.solving_time = time.time() - start_time #end timing

        return success  
    
    def _solve_backtracking(self):
        """Recursive backtracking algo to solve the puzzle."""

        empty_cell = self.solved_board.find_empty() #find an empty cell

        #if no empty cell is found, the puzzle is solved!
        if empty_cell is None:
            return True
        
        row, col = empty_cell

        #try digits 1-9 for this empty cell
        for num in range(1,10):

            #check if the digit is valid in this position
            if self.solved_board.is_valid(row, col, num):
                self.solved_board.board[row, col] = num #place the digit

                #recursively solve the rest of the puzzle
                if self._solve_backtracking():
                    return True 
                
                self.solved_board.board[row,col] = 0 #backtrack by setting the cell to 0

        #no digits worked, so this puzzle is unsolvable 
        return False

    def display_solution(self):
        """Displays the soln."""

        if self.solved_board is None:
            print("The puzzle hasn't been solved yet.")
            return
        
        print("\nSolution:")
        self.solved_board.display()
        print(f"Solving time: {self.solving_time:.3f} seconds")



def main():
    """
    Main function to run the code.
    This function provides a menu for the user to load Sudoku from manual input or image.
    """

    board = SudokuBoard()  # Create a SudokuBoard object

    while True:
        print("\nSudoku Solver")
        print("1. Load Sudoku from manual input")
        print("2. Load Sudoku from image")
        print("3. Solve Sudoku")
        print("4. Quit")

        choice = input("\nEnter your choice: ")

        if choice == '1':
            print("=" * 35)
            board.load_user_input()  # Load Sudoku from user input
            print("=" * 35)

        elif choice == '2':
            image_path = input("Enter the path to the Sudoku image: ")
            success = board.load_from_image(image_path)
            if not success:
                print("Failed to load puzzle from image. Try again or use manual input.")
        
        elif choice == '3':
            # Check if board is empty
            if np.sum(board.board) == 0:
                print("Board is empty. Please load a puzzle first.")
                continue

            print("\nSolving puzzle...")
            solver = SudokuSolver(board)
            if solver.solve():
                solver.display_solution()
            else:
                print("No solution :(")
            
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