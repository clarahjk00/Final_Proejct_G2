# Sudoku Solver

Sudoku is fun until it’s not. Ever got stuck with a tricky board, erasing so many times that the paper nearly tore? We've been there. 

Whether you’re a casual player or an obsessive puzzler, this tool is here to help. If you’re stuck, don’t worry. We’ve got you!
<br>
<br>
## 🐍Required installation
Make sure you have the following Python libraries installed:
+ numpy
+ opencv-python (cv2)
+ pytesseract
+ Pillow
+ You may also need to install **Tesseract**

```
pip install numpy opencv-python pytesseract pillow
```

## ⚙️How to use:
### Step 0. Prepare Your Input
If you have a picture of your Sudoku board, add a photo or get ready to input it manually.
Ensure the image file is saved on your computer (preferably in the same folder as the code), and note down the file path.

The following picture format is supported:
+ JPEG (.jpg, .jpeg)
+ PNG (.png)
+ WebP (.webp)


### Step 1. Run the code
Once you run the code, you get to pick an option. Type the number of your desired option and hit enter.

1️⃣ **Option 1. Manual input**

Enter 9 rows, each containing 9 digits.\
Use `0` or `.` for empty cells.

Example input using `board1.png`:
<br>
*Input example*
<br>
![Input example](https://github.com/clarahjk00/Final_Proejct_G2/blob/d77d341bbad04d8f05f562185e520c6ed854eb59/Example%201.png)
<br>
*Result example*
<br>
![Result example](https://github.com/clarahjk00/Final_Proejct_G2/blob/d77d341bbad04d8f05f562185e520c6ed854eb59/Example%201-2.png)

2️⃣ **Option 2. Image input**

Paste the full file path of your Sudoku board image.

Example:
+ For windows user: `C:\Users\YourUsername\Pictures\sudoku_puzzle.jpg`
+ For Mac/Linux user:` /home/username/Pictures/sudoku_puzzle.jpg` or `~/Pictures/sudoku_puzzle.jpg`

3️⃣ **Option 3. Solver**

This solves the puzzle based on your input via Option 1 or 2.
Example using `board1.png`:
<br>
![Solution example](https://github.com/clarahjk00/Final_Proejct_G2/blob/d77d341bbad04d8f05f562185e520c6ed854eb59/Example%203.png)

4️⃣ **Option 4. Quit**

Exits the program.
<br>
<br>
## 🎉What you will get:
A fully solved Sudoku puzzle is printed to your terminal—no more guesswork or erasing holes in your paper.
<br>
<br>
## 📧Still confused? Contact us!
Nithya Parthasarathi (nparthasarathi17 | npartha2@jh.edu)
+ Initial logic
+ Code solver and image processing
+ Unittest
 
Clara Hyeonji Kim (clarahjk00 | hkim348@jh.edu)
+ Updating README
+ Code the Sudoku board class
+ Additional edits in image processing
