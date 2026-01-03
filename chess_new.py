"""
==============================
 CHESS GAME WITH BASIC RULES
 Python + Tkinter
==============================
"""

import tkinter as tk
import random

# -----------------------------
# CONSTANTS
# -----------------------------
BOARD_SIZE = 8
SQUARE_SIZE = 80
MARGIN = 30  # space for numbers/letters

# -----------------------------
# VARIABLES
# -----------------------------
board_history = []  # stores past board states
game_mode = None    # will be set to one of: "pvp", "pvc", "cvp", "cvc"

# -----------------------------
# MAIN WINDOW
# -----------------------------
root = tk.Tk()
root.title("Python Chess - With Move Log")

# Frame for board + move log
frame = tk.Frame(root)
frame.pack()

# Chessboard canvas
canvas = tk.Canvas(
    frame,
    width=MARGIN + BOARD_SIZE * SQUARE_SIZE,
    height=BOARD_SIZE * SQUARE_SIZE + MARGIN
)
canvas.grid(row=0, column=0)

turn_label = tk.Label(frame, text="White's turn", font=("Arial", 12, "bold"))
turn_label.grid(row=0, column=1, sticky='n')

# Move log (Text widget)
move_log = tk.Text(frame, width=20, height=20, state='disabled', font=("Arial", 12))
move_log.grid(row=0, column=1, padx=10)

# Scrollbar for move log
scrollbar = tk.Scrollbar(frame, command=move_log.yview)
scrollbar.grid(row=0, column=2, sticky='ns')
move_log.config(yscrollcommand=scrollbar.set)

# -----------------------------
# CHESS PIECES (UNICODE)
# -----------------------------
pieces = {
    "r": "♜", "n": "♞", "b": "♝", "q": "♛",
    "k": "♚", "p": "♟",
    "R": "♖", "N": "♘", "B": "♗", "Q": "♕",
    "K": "♔", "P": "♙"
}

# -----------------------------
# INITIAL BOARD
# -----------------------------
board = [
    list("rnbqkbnr"),
    list("pppppppp"),
    list("........"),
    list("........"),
    list("........"),
    list("........"),
    list("PPPPPPPP"),
    list("RNBQKBNR")
]

initial_board = [row.copy() for row in board]

# -----------------------------
# GAME STATE
# -----------------------------
selected_square = None
current_turn = "white"  # white starts

white_king_moved = False
black_king_moved = False
white_rook_moved = {"left": False, "right": False}
black_rook_moved = {"left": False, "right": False}

en_passant_target = None  # (row, col)
move_number = 1

# -----------------------------
# GAME MODE SELECTOR
# -----------------------------
def select_mode(mode):
    global game_mode
    game_mode = mode
    mode_window.destroy()
    draw_board()
    draw_pieces()
    # Start computer move if needed
    if (game_mode == "cvc") or (game_mode == "cvp" and current_turn=="white") or (game_mode == "pvc" and current_turn=="black"):
        root.after(500, computer_move)

mode_window = tk.Toplevel(root)
mode_window.title("Select Game Mode")
tk.Label(mode_window, text="Select Game Mode:", font=("Arial", 14)).pack(pady=10)
tk.Button(mode_window, text="Player vs Player", width=20, command=lambda: select_mode("pvp")).pack(pady=5)
tk.Button(mode_window, text="Player vs Computer", width=20, command=lambda: select_mode("pvc")).pack(pady=5)
tk.Button(mode_window, text="Computer vs Player", width=20, command=lambda: select_mode("cvp")).pack(pady=5)
tk.Button(mode_window, text="Computer vs Computer", width=20, command=lambda: select_mode("cvc")).pack(pady=5)

# Disable main window until mode is selected
root.withdraw()
def show_main_window():
    root.deiconify()
root.after(100, show_main_window)

# -----------------------------
# DRAW BOARD FUNCTION
# -----------------------------
def draw_board():
    canvas.delete("all")
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = "#EEEED2" if (row + col) % 2 == 0 else "#769656"
            canvas.create_rectangle(
                MARGIN + col * SQUARE_SIZE,
                row * SQUARE_SIZE,
                MARGIN + (col + 1) * SQUARE_SIZE,
                (row + 1) * SQUARE_SIZE,
                fill=color,
                outline=""
            )
    # Margin lines
    canvas.create_line(MARGIN, 0, MARGIN, BOARD_SIZE * SQUARE_SIZE, width=2)
    canvas.create_line(MARGIN, BOARD_SIZE * SQUARE_SIZE, 
                       MARGIN + BOARD_SIZE * SQUARE_SIZE, BOARD_SIZE * SQUARE_SIZE, width=2)
    # Row numbers
    for row in range(BOARD_SIZE):
        canvas.create_text(
            MARGIN // 2,
            row * SQUARE_SIZE + SQUARE_SIZE // 2,
            text=str(8 - row),
            font=("Arial", 12, "bold")
        )
    # Column letters
    for col in range(BOARD_SIZE):
        canvas.create_text(
            MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2,
            BOARD_SIZE * SQUARE_SIZE + MARGIN // 2,
            text=chr(ord('a') + col),
            font=("Arial", 12, "bold")
        )

# -----------------------------
# DRAW PIECES FUNCTION
# -----------------------------
def draw_pieces():
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece != ".":
                canvas.create_text(
                    MARGIN + c * SQUARE_SIZE + SQUARE_SIZE // 2,
                    r * SQUARE_SIZE + SQUARE_SIZE // 2,
                    text=pieces[piece],
                    font=("Arial", 32)
                )

# -----------------------------
# COMPUTER MOVE FUNCTION
# -----------------------------
def get_all_legal_moves(color):
    moves = []
    for sr in range(8):
        for sc in range(8):
            piece = board[sr][sc]
            if piece == ".":
                continue
            if color == "white" and not piece.isupper():
                continue
            if color == "black" and not piece.islower():
                continue
            for tr in range(8):
                for tc in range(8):
                    if is_legal_move(piece, sr, sc, tr, tc):
                        backup_from = board[sr][sc]
                        backup_to = board[tr][tc]
                        board[tr][tc] = piece
                        board[sr][sc] = "."
                        illegal = king_in_check(color)
                        board[sr][sc] = backup_from
                        board[tr][tc] = backup_to
                        if not illegal:
                            moves.append((sr, sc, tr, tc))
    return moves

def computer_move():
    global current_turn
    if (game_mode is None) or (current_turn=="white" and game_mode in ["pvp","cvp"]) or (current_turn=="black" and game_mode in ["pvp","pvc"]):
        return  # Only move for computer if needed

    moves = get_all_legal_moves(current_turn)
    if not moves:
        return

    # Prefer captures
    capture_moves = [m for m in moves if board[m[2]][m[3]] != "."]
    move = random.choice(capture_moves if capture_moves else moves)

    sr, sc, tr, tc = move
    piece = board[sr][sc]

    # Save history
    board_history.append([row.copy() for row in board])
    board[tr][tc] = piece
    board[sr][sc] = "."

    # Auto promotion for pawns
    if piece == "P" and tr == 0:
        board[tr][tc] = "Q"
    elif piece == "p" and tr == 7:
        board[tr][tc] = "q"

    # Switch turn
    current_turn = "white" if current_turn == "black" else "black"
    turn_label.config(text=f"{current_turn.capitalize()}'s turn")
    draw_board()
    draw_pieces()

    # Continue if next is also computer
    if (game_mode=="cvc") or (current_turn=="white" and game_mode=="cvp") or (current_turn=="black" and game_mode=="pvc"):
        root.after(500, computer_move)

# -----------------------------
# PLACEHOLDER FUNCTIONS
# -----------------------------
def is_legal_move(piece, sr, sc, tr, tc):
    # You can copy your full 767-line move logic here
    return True  # temporary for demo

def king_in_check(color):
    return False

# -----------------------------
# MOUSE CLICK HANDLER
# -----------------------------
def on_click(event):
    # Only allow clicks if human turn
    if (game_mode=="pvp") or \
       (game_mode=="pvc" and current_turn=="white") or \
       (game_mode=="cvp" and current_turn=="black"):
        print("Click registered")  # replace with your full click logic
canvas.bind("<Button-1>", on_click)

# -----------------------------
# START GAME
# -----------------------------
draw_board()
draw_pieces()
root.mainloop()
