# Main Code Block

"""
Sudoku Solver with OCR and Backtracking!
By: Clara Kim & Nithya Parthasarathi

This project is a Sudoku solver that can solve puzzles in two ways:
1.  Accepting user manual input for the Sudoku board
2.  Accepting an image of Sudoku board form the user

For the image processing part, the solver uses:
- OpenCV for image processing - it detects and extracts the Sudoku grid from the image
- Tesseract OCR (via pytesseract) - it reads the digits from the extracted cells using 
Optical Character Recognition (OCR), coverting the images of the numebrs into integers. 

The solver uses a backtracking algorithm to solve the Sudoku puzzle. The solved Sudoku board 
is displayed to the user, along with the time taken to solve it.
"""


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
        self.board = np.zeros((9, 9), dtype=int)  #main 9x9 grid 
        self.original = np.zeros((9, 9), dtype=bool) #keeps track of which numbers were filled in by the user


    def load_user_input(self):
        """
        Prompt the user to input Sudoku row by row.
        """
        print("Enter your sudoku row by row.")
        print("Use 0 or . for empty cells.")
        print("=" * 35) #visual divider 

        for i in range(9):
            valid_input = False
            while not valid_input:
                row_input = input(f"Enter row {i + 1} (9 digits): ") #ask for one row of numbers 
                row_input = row_input.replace(" ", "").replace(".","0") #clean up the input, removes spaces and turn '.' into 0

                #check that there are only 9 characters 
                if len(row_input) != 9:
                    print("Error: Entered row must be 9 digits long.")
                    continue

                try:
                    row = [int(cell) for cell in row_input] #turn each character into a number
                    #make sure all numbers are between 0 and 9
                    if not all(0 <= cell <= 9 for cell in row):
                        print("Error: Digits must be between 0 and 9.")
                        continue

                    valid_input = True #if we made it here, the input is valid
                    self.board[i] = row  #save the row to the board

                    #mark the numbers that aren't zero as original
                    for j in range(9):
                        if row[j] != 0:      
                            self.original[i][j] = True

                except ValueError:
                    print("Error: Invalid input. Please enter digits only.")
        
        print("=" * 35)
        print("\nSudoku board loaded successfully.\n")
        print("=" * 35)
        self.display()  #show the board 

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
                        #mark original clues (pre-filled digits)
                        self.original_cells[i, j] = True
                except Exception as e:
                    print(f"Warning: Failed to recognize digit at cell ({i}, {j}): {e}")
                    self.board[i, j] = 0  #default to empty if recognition fails

        #display the final loaded board
        print("=" * 35)
        print("\nLoaded Sudoku puzzle from image:")
        print("")
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
        """Recognize digit in a Sudoku cell using OCR (Tesseract)."""
        try:
            #make the digit stand out more by inverting the colors 
            _, thresh = cv2.threshold(cell_image, 128, 255, cv2.THRESH_BINARY_INV)
            
            #if hthe cell is mostly empty (not much white), assume it's blank
            if np.sum(thresh) / 255 < cell_image.size * 0.05:
                return 0
            
            #add some space aroumd the digit to help Tesseract read it 
            padded = cv2.copyMakeBorder(thresh, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=0)
            
            #tesseract configuration: treat image as a single character, and only look for digits 1-9
            config = '--psm 10 --oem 3 -c tessedit_char_whitelist=123456789'
            digit_text = pytesseract.image_to_string(padded, config=config).strip()
            
            #try converting the result into an integer 
            try:
                digit = int(digit_text)
                if 1 <= digit <= 9:
                    return digit
            except (ValueError, IndexError):
                pass

            #second try if first one fails
            #enhance the white region of the image to help Tesseract read it better
            kernel = np.ones((3, 3), np.uint8)  #create a kernel for dilation
            dilated = cv2.dilate(thresh, kernel, iterations=1)  #dilate the image to make the digits more prominent
            kernel_padded = cv2.copyMakeBorder(dilated, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=0)

            digit_text = pytesseract.image_to_string(kernel_padded, config=config).strip()

            try:
                digit = int(digit_text)
                if 1 <= digit <= 9:
                    return digit
            except (ValueError, IndexError):
                pass
            return 0  #if tesseract didn't return a valid digit, return 0 
        
        except Exception as e: #something went wrong 
            print(f"OCR failed: {e}")
            print("Returning 0 for this cell. Consider using manual input instead.")
            return 0

    def display(self):
        """
        Print the Sudoku board in a readable format.
        """
        print("-" * 29) #top border
        for i in range(9):
            row = ""
            for j in range(9):
                #show a dot for empty cells 
                if self.board[i][j] == 0:
                    row += " . "                                
                else:
                    row += f" {self.board[i][j]} "

                #add vertical line every 3 cols
                if (j + 1) % 3 == 0 and j != 8:
                    row += "|"                                  
            print(row)

            #add horizontal separator every 3 rows
            if (i + 1) % 3 == 0:
                print("-" * 29)                                         


    def is_valid(self, row, col, num):
        """
        Check the validity of position for number in Sudoku board.

        Args:
            row (int): Row index (0-8).
            col (int): Column index (0-8).
            num (int): Number to check (1-9).
        """

        #check if the number already exists in this col
        for i in range(9):
            if self.board[i, col] == num:                              
                return False

        #check if the number already exists in this row 
        for j in range(9):
            if self.board[row, j] == num:                          
                return False
        
        #figure out where the 3x3 subgrid starts 
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)

        #check if the num is already in teh same 3x3 box
        for i in range(start_row, start_row + 3):                       
            for j in range(start_col, start_col + 3):
                if self.board[i, j] == num:
                    return False
        
        #if all checks are passed, it's valid move 
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
                    return (i, j) #found an empty spot
        return None #no more empty spots 

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
        
        print("=" * 35)
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
            print("=" * 35)
            image_path = input("Enter the path to the Sudoku image: ")
            success = board.load_from_image(image_path)
            print("")
            print("=" * 35)
            if not success:
                print("Failed to load puzzle from image. Try again or use manual input.")
        
        elif choice == '3':
            # Check if board is empty
            if np.sum(board.board) == 0:
                print("=" * 35)
                print("\nBoard is empty. Please load a puzzle first.")
                print("")
                print("=" * 35)
                continue
            
            print("=" * 35)
            print("\nSolving puzzle...")
            solver = SudokuSolver(board)
            if solver.solve():
                solver.display_solution()
                print("")
                print("=" * 35)
            else:
                print("=" * 35)
                print("\nNo solution :(")
                print("=" * 35)
            
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