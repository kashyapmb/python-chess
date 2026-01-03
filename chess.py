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
dragging_piece = None      # piece char e.g. "P"
drag_start = None          # (row, col)
drag_image = None          # canvas text ID
is_dragging = False




# -----------------------------
# MAIN WINDOW
# -----------------------------
# Main window
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
# Track king & rook movement (for castling)
white_king_moved = False
black_king_moved = False
white_rook_moved = {"left": False, "right": False}
black_rook_moved = {"left": False, "right": False}

# Track en passant target square
en_passant_target = None  # (row, col)

# -----------------------------
# DRAW BOARD
# -----------------------------

def draw_board():
    canvas.delete("all")  # clear canvas

    # Draw squares
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

    # Draw vertical margin line (left)
    canvas.create_line(MARGIN, 0, MARGIN, BOARD_SIZE * SQUARE_SIZE, width=2)

    # Draw horizontal margin line (bottom)
    canvas.create_line(MARGIN, BOARD_SIZE * SQUARE_SIZE, 
                       MARGIN + BOARD_SIZE * SQUARE_SIZE, BOARD_SIZE * SQUARE_SIZE, width=2)

    # Draw row numbers (1-8) on left margin
    for row in range(BOARD_SIZE):
        canvas.create_text(
            MARGIN // 2,
            row * SQUARE_SIZE + SQUARE_SIZE // 2,
            text=str(8 - row),
            font=("Arial", 12, "bold")
        )

    # Draw column letters (a-h) on bottom margin
    for col in range(BOARD_SIZE):
        canvas.create_text(
            MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2,
            BOARD_SIZE * SQUARE_SIZE + MARGIN // 2,
            text=chr(ord('a') + col),
            font=("Arial", 12, "bold")
        )




move_number = 1
def log_move(sr, sc, tr, tc, piece):
    global move_number

    # Convert to chess notation
    start = chr(ord('a') + sc) + str(8 - sr)
    end = chr(ord('a') + tc) + str(8 - tr)
    move_text = f"{move_number}. {start} → {end} ({piece})\n"

    move_log.config(state='normal')
    move_log.insert(tk.END, move_text)
    move_log.see(tk.END)
    move_log.config(state='disabled')

    # Increase number every 2 moves (one full turn)
    if current_turn == "black":
        move_number += 1


# -----------------------------
# HIGHLIGHT SQUARE
# -----------------------------
def highlight_square(row, col, color="#ADD8E6"):
    canvas.create_rectangle(
        MARGIN + col * SQUARE_SIZE,  # Add margin here
        row * SQUARE_SIZE,
        MARGIN + (col + 1) * SQUARE_SIZE,
        (row + 1) * SQUARE_SIZE,
        fill=color,
        outline=""
    )


# -----------------------------
# SHOW LEGAL MOVES
# -----------------------------
def show_legal_moves(sr, sc):
    piece = board[sr][sc]
    for r in range(8):
        for c in range(8):
            if is_legal_move(piece, sr, sc, r, c):
                canvas.create_oval(
                    MARGIN + c * SQUARE_SIZE + 30,  # Add margin here
                    r * SQUARE_SIZE + 30,
                    MARGIN + c * SQUARE_SIZE + 50,
                    r * SQUARE_SIZE + 50,
                    fill="green",
                    outline=""
                )





def get_all_legal_moves(color):
    moves = []
    for sr in range(8):
        for sc in range(8):
            piece = board[sr][sc]
            if piece == ".":
                continue
            if color == "white" and not is_white(piece):
                continue
            if color == "black" and not is_black(piece):
                continue

            for tr in range(8):
                for tc in range(8):
                    if is_legal_move(piece, sr, sc, tr, tc):
                        # test move
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
    global current_turn, en_passant_target

    moves = get_all_legal_moves("black")
    if not moves:
        return

    # Prefer captures
    capture_moves = [m for m in moves if board[m[2]][m[3]] != "."]
    move = random.choice(capture_moves if capture_moves else moves)

    sr, sc, tr, tc = move
    piece = board[sr][sc]

    # Save current board state for undo
    board_history.append([row.copy() for row in board])

    # Move the piece
    board[tr][tc] = piece
    board[sr][sc] = "."

    # -------- CASTLING ROOK MOVE --------
    if piece.lower() == "k" and abs(tc - sc) == 2:
        if tc == 6:          # king-side
            board[tr][5] = board[tr][7]
            board[tr][7] = "."
        elif tc == 2:        # queen-side
            board[tr][3] = board[tr][0]
            board[tr][0] = "."

    # -------- EN PASSANT CAPTURE --------
    if piece.lower() == "p" and en_passant_target == (tr, tc) and board[tr][tc] == ".":
        if is_white(piece):
            board[tr + 1][tc] = "."  # remove captured black pawn
        else:
            board[tr - 1][tc] = "."  # remove captured white pawn

    # -------- RESET / SET EN PASSANT TARGET --------
    en_passant_target = None
    if piece.lower() == "p" and abs(tr - sr) == 2:
        en_passant_target = ((tr + sr) // 2, tc)

    # -------- AUTO-PROMOTION FOR COMPUTER --------
    if piece == "p" and tr == 7:
        board[tr][tc] = "q"  # automatically promote to Queen

    # Log the move
    log_move(sr, sc, tr, tc, piece)

    # Switch turn
    current_turn = "white"
    turn_label.config(text=f"{current_turn.capitalize()}'s turn")

    # Check for checkmate
    if is_checkmate("white"):
        show_game_over("black")

    # Redraw board
    canvas.delete("all")
    draw_board()
    draw_pieces()






# -----------------------------
# DRAW PIECES
# -----------------------------
def draw_pieces():
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece != ".":

                # If king is in check → highlight with red border
                if (piece == "K" and king_in_check("white")) or (piece == "k" and king_in_check("black")):
                    canvas.create_rectangle(
                        MARGIN + c * SQUARE_SIZE,
                        r * SQUARE_SIZE,
                        MARGIN + (c + 1) * SQUARE_SIZE,
                        (r + 1) * SQUARE_SIZE,
                        outline="red",
                        width=3
                    )

                # Draw piece centered
                canvas.create_text(
                    MARGIN + c * SQUARE_SIZE + SQUARE_SIZE // 2,
                    r * SQUARE_SIZE + SQUARE_SIZE // 2,
                    text=pieces[piece],
                    font=("Arial", 32)
                )

    # Optional: highlight last move (if any)
    if board_history:
        last_board = board_history[-1]
        for r in range(8):
            for c in range(8):
                if last_board[r][c] != board[r][c]:
                    canvas.create_rectangle(
                        MARGIN + c * SQUARE_SIZE,
                        r * SQUARE_SIZE,
                        MARGIN + (c + 1) * SQUARE_SIZE,
                        (r + 1) * SQUARE_SIZE,
                        outline="blue",
                        width=2
                    )



# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def is_white(piece):
    return piece.isupper()

def is_black(piece):
    return piece.islower()

def find_king(color):
    """Find king position for given color"""
    king = "K" if color == "white" else "k"
    for r in range(8):
        for c in range(8):
            if board[r][c] == king:
                return r, c
    return None

def path_clear(sr, sc, tr, tc):
    """Check if path is clear (for rook, bishop, queen)"""
    dr = (tr - sr) and ((tr - sr) // abs(tr - sr))
    dc = (tc - sc) and ((tc - sc) // abs(tc - sc))

    r, c = sr + dr, sc + dc
    while (r, c) != (tr, tc):
        if board[r][c] != ".":
            return False
        r += dr
        c += dc
    return True

# -----------------------------
# MOVE VALIDATION
# -----------------------------
def is_legal_move(piece, sr, sc, tr, tc):
    target = board[tr][tc]

    # Cannot capture own piece
    if target != "." and (is_white(piece) == is_white(target)):
        return False

    dr = tr - sr
    dc = tc - sc

    # PAWN
    if piece.lower() == "p":
        direction = -1 if is_white(piece) else 1
        start_row = 6 if is_white(piece) else 1

        # Move forward
        if dc == 0 and target == ".":
            if dr == direction:
                return True
            if sr == start_row and dr == 2 * direction and board[sr + direction][sc] == ".":
                return True

        # Diagonal capture
        if abs(dc) == 1 and dr == direction:
            # Normal capture
            if target != "." and is_white(piece) != is_white(target):
                return True
            # En passant capture
            if target == "." and en_passant_target == (tr, tc):
                return True

    # ROOK
    elif piece.lower() == "r":
        if sr == tr or sc == tc:
            return path_clear(sr, sc, tr, tc)

    # BISHOP
    elif piece.lower() == "b":
        if abs(dr) == abs(dc):
            return path_clear(sr, sc, tr, tc)

    # QUEEN
    elif piece.lower() == "q":
        if sr == tr or sc == tc or abs(dr) == abs(dc):
            return path_clear(sr, sc, tr, tc)

    # KNIGHT
    elif piece.lower() == "n":
        return (abs(dr), abs(dc)) in [(2, 1), (1, 2)]

    # KING
    elif piece.lower() == "k":
        # Normal king move
        if abs(dr) <= 1 and abs(dc) <= 1:
            return True

        # ---------------- CASTLING ----------------
        if is_white(piece):
            if white_king_moved:
                return False
            row = 7
        else:
            if black_king_moved:
                return False
            row = 0

        # King-side castling
        if dr == 0 and dc == 2:
            rook_col = 7
            if board[row][5] == "." and board[row][6] == ".":
                if not is_square_attacked(row, 4, "black" if is_white(piece) else "white") and \
                not is_square_attacked(row, 5, "black" if is_white(piece) else "white") and \
                not is_square_attacked(row, 6, "black" if is_white(piece) else "white"):
                    return True

        # Queen-side castling
        if dr == 0 and dc == -2:
            rook_col = 0
            if board[row][1] == "." and board[row][2] == "." and board[row][3] == ".":
                if not is_square_attacked(row, 4, "black" if is_white(piece) else "white") and \
                not is_square_attacked(row, 3, "black" if is_white(piece) else "white") and \
                not is_square_attacked(row, 2, "black" if is_white(piece) else "white"):
                    return True


    return False

def is_square_attacked(row, col, by_color):
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == ".":
                continue

            if by_color == "white" and is_white(piece):
                if piece.lower() == "p":
                    direction = -1
                    if (r + direction == row) and abs(c - col) == 1:
                        return True
                elif piece.lower() == "k":
                    if max(abs(r - row), abs(c - col)) == 1:
                        return True
                else:
                    if is_legal_move(piece, r, c, row, col):
                        return True

            if by_color == "black" and is_black(piece):
                if piece.lower() == "p":
                    direction = 1
                    if (r + direction == row) and abs(c - col) == 1:
                        return True
                elif piece.lower() == "k":
                    if max(abs(r - row), abs(c - col)) == 1:
                        return True
                else:
                    if is_legal_move(piece, r, c, row, col):
                        return True
    return False


def king_in_check(color):
    king_pos = find_king(color)
    if not king_pos:
        return False

    kr, kc = king_pos
    opponent = "black" if color == "white" else "white"
    return is_square_attacked(kr, kc, opponent)


def has_legal_moves(color):
    """Check if the given color has at least one legal move"""
    for sr in range(8):
        for sc in range(8):
            piece = board[sr][sc]
            if piece == ".":
                continue

            if color == "white" and not is_white(piece):
                continue
            if color == "black" and not is_black(piece):
                continue

            for tr in range(8):
                for tc in range(8):
                    if is_legal_move(piece, sr, sc, tr, tc):

                        # Try move temporarily
                        backup_from = board[sr][sc]
                        backup_to = board[tr][tc]

                        board[tr][tc] = piece
                        board[sr][sc] = "."

                        illegal = king_in_check(color)

                        # Undo move
                        board[sr][sc] = backup_from
                        board[tr][tc] = backup_to

                        if not illegal:
                            return True
    return False

def promote_pawn(tr, tc):
    piece = board[tr][tc]
    if (piece == "P" and tr == 0) or (piece == "p" and tr == 7):

        # Create a top-level popup
        popup = tk.Toplevel(root)
        popup.title("Promote Pawn")

        tk.Label(popup, text="Choose promotion:", font=("Arial", 12)).pack(pady=5)

        def choose(new_piece):
            board[tr][tc] = new_piece
            popup.destroy()
            # Redraw board after promotion
            canvas.delete("all")
            draw_board()
            draw_pieces()

        # Buttons for choices
        if piece.isupper():
            pieces_options = ["Q", "R", "B", "N"]
        else:
            pieces_options = ["q", "r", "b", "n"]

        for p in pieces_options:
            tk.Button(popup, text=pieces[p], font=("Arial", 24),
                      command=lambda p=p: choose(p)).pack(side="left", padx=5, pady=5)



def is_checkmate(color):
    return king_in_check(color) and not has_legal_moves(color)

def show_game_over(winner):
    move_log.config(state='normal')
    move_log.insert(tk.END, f"\nCHECKMATE! {winner.upper()} WINS\n")
    move_log.see(tk.END)
    move_log.config(state='disabled')

def undo_move(event=None):
    global board, current_turn, move_number
    if board_history:
        board = board_history.pop()
        current_turn = "black" if current_turn == "white" else "white"
        if current_turn == "white":
            move_number = max(1, move_number-1)
        # Remove last move from log
        move_log.config(state='normal')
        move_log.delete("end-2l", "end-1l")  # delete last line
        move_log.config(state='disabled')
        canvas.delete("all")
        draw_board()
        draw_pieces()


def restart_game(event=None):
    global board, current_turn, move_number, board_history
    board = [row.copy() for row in initial_board]  # initial_board = starting position
    current_turn = "white"
    move_number = 1
    board_history = []
    move_log.config(state='normal')
    move_log.delete(1.0, tk.END)
    move_log.config(state='disabled')
    canvas.delete("all")
    draw_board()
    draw_pieces()

def on_drag_start(event):
    global dragging_piece, drag_start, drag_image, is_dragging
    is_dragging = True

    col = (event.x - MARGIN) // SQUARE_SIZE
    row = event.y // SQUARE_SIZE

    if not (0 <= row < 8 and 0 <= col < 8):
        return

    piece = board[row][col]
    if piece == ".":
        return

    # Respect turn
    if current_turn == "white" and is_black(piece):
        return
    if current_turn == "black" and is_white(piece):
        return

    dragging_piece = piece
    drag_start = (row, col)

    # Create floating piece
    drag_image = canvas.create_text(
        event.x,
        event.y,
        text=pieces[piece],
        font=("Arial", 32),
        fill="black"
    )

def on_drag_motion(event):
    if drag_image:
        canvas.coords(drag_image, event.x, event.y)

def on_drag_release(event):
    global dragging_piece, drag_start, drag_image
    global current_turn, en_passant_target
    global white_king_moved, black_king_moved
    global white_rook_moved, black_rook_moved
    global is_dragging

    if not dragging_piece or not drag_start:
        return

    is_dragging = False

    sr, sc = drag_start
    tr = event.y // SQUARE_SIZE
    tc = (event.x - MARGIN) // SQUARE_SIZE

    # Remove floating piece
    if drag_image:
        canvas.delete(drag_image)

    drag_image = None

    # Out of board → cancel
    if not (0 <= tr < 8 and 0 <= tc < 8):
        reset_drag()
        redraw()
        return

    piece = dragging_piece
    backup_board = [row.copy() for row in board]

    if is_legal_move(piece, sr, sc, tr, tc):

        # --- MOVE PIECE ---
        board[tr][tc] = piece
        board[sr][sc] = "."

        # --- CASTLING ---
        if piece.lower() == "k" and abs(tc - sc) == 2:
            if tc == 6:  # king side
                board[tr][5] = board[tr][7]
                board[tr][7] = "."
            elif tc == 2:  # queen side
                board[tr][3] = board[tr][0]
                board[tr][0] = "."

        # --- EN PASSANT CAPTURE ---
        if piece.lower() == "p" and en_passant_target == (tr, tc):
            if piece.isupper():
                board[tr + 1][tc] = "."
            else:
                board[tr - 1][tc] = "."

        # --- KING SAFETY CHECK ---
        if king_in_check(current_turn):
            board[:] = backup_board
            reset_drag()
            redraw()
            return

        # --- UPDATE CASTLING FLAGS ---
        if piece == "K":
            white_king_moved = True
        elif piece == "k":
            black_king_moved = True

        if piece == "R" and sr == 7 and sc == 0:
            white_rook_moved["left"] = True
        elif piece == "R" and sr == 7 and sc == 7:
            white_rook_moved["right"] = True

        if piece == "r" and sr == 0 and sc == 0:
            black_rook_moved["left"] = True
        elif piece == "r" and sr == 0 and sc == 7:
            black_rook_moved["right"] = True

        # --- UPDATE EN PASSANT TARGET ---
        en_passant_target = None
        if piece.lower() == "p" and abs(tr - sr) == 2:
            en_passant_target = ((tr + sr) // 2, tc)

        # --- LOG + PROMOTION ---
        log_move(sr, sc, tr, tc, piece)
        promote_pawn(tr, tc)

        # --- SWITCH TURN ---
        current_turn = "black" if current_turn == "white" else "white"
        turn_label.config(text=f"{current_turn.capitalize()}'s turn")

        # --- COMPUTER MOVE ---
        if current_turn == "black":
            root.after(300, computer_move)

    reset_drag()
    redraw()

def reset_drag():
    global dragging_piece, drag_start
    dragging_piece = None
    drag_start = None

def redraw():
    canvas.delete("all")
    draw_board()
    draw_pieces()





















# -----------------------------
# MOUSE CLICK HANDLER
# -----------------------------
def on_click(event):

    if is_dragging:
        return
    
    global selected_square, current_turn, move_number
    global white_king_moved, black_king_moved
    global white_rook_moved, black_rook_moved
    global en_passant_target

    col = (event.x - MARGIN) // SQUARE_SIZE
    row = event.y // SQUARE_SIZE

    if not (0 <= row < 8 and 0 <= col < 8):
        return

    piece = board[row][col]

    # -----------------------------
    # NO PIECE SELECTED
    # -----------------------------
    if selected_square is None:

        if piece == ".":
            return

        if current_turn == "white" and is_black(piece):
            return
        if current_turn == "black" and is_white(piece):
            return

        selected_square = (row, col)

        canvas.delete("all")
        draw_board()
        highlight_square(row, col)
        draw_pieces()
        show_legal_moves(row, col)
        return

    # -----------------------------
    # PIECE ALREADY SELECTED
    # -----------------------------
    sr, sc = selected_square
    selected_piece = board[sr][sc]

    # Reselect same color
    if piece != "." and is_white(piece) == is_white(selected_piece):
        selected_square = (row, col)
        canvas.delete("all")
        draw_board()
        highlight_square(row, col)
        draw_pieces()
        show_legal_moves(row, col)
        return

    # -----------------------------
    # TRY MOVE
    # -----------------------------
    if is_legal_move(selected_piece, sr, sc, row, col):

        backup_board = [r.copy() for r in board]
        board_history.append(backup_board)

        board[row][col] = selected_piece
        board[sr][sc] = "."

        # -------- CASTLING ROOK MOVE --------
        if selected_piece.lower() == "k" and abs(col - sc) == 2:
            if col == 6:          # king-side
                board[row][5] = board[row][7]
                board[row][7] = "."
            elif col == 2:        # queen-side
                board[row][3] = board[row][0]
                board[row][0] = "."
        
        # -----------------------------
        # EN PASSANT CAPTURE
        # -----------------------------
        if selected_piece.lower() == "p" and en_passant_target == (row, col) and board[row][col] == ".":
            if is_white(selected_piece):
                board[row + 1][col] = "."  # remove captured black pawn
            else:
                board[row - 1][col] = "."  # remove captured white pawn

        # -----------------------------
        # RESET / SET EN PASSANT TARGET
        # -----------------------------
        en_passant_target = None
        if selected_piece.lower() == "p" and abs(row - sr) == 2:
            en_passant_target = ((row + sr) // 2, col)



        # -------- CHECK ILLEGAL --------
        if king_in_check(current_turn):
            board[:] = backup_board
        else:
            # -------- LOG MOVE --------
            log_move(sr, sc, row, col, selected_piece)

            # Check for pawn promotion
            promote_pawn(row, col)

            # -------- UPDATE CASTLING FLAGS --------
            if selected_piece == "K":
                white_king_moved = True
            elif selected_piece == "k":
                black_king_moved = True

            if selected_piece == "R" and sr == 7 and sc == 0:
                white_rook_moved["left"] = True
            elif selected_piece == "R" and sr == 7 and sc == 7:
                white_rook_moved["right"] = True

            if selected_piece == "r" and sr == 0 and sc == 0:
                black_rook_moved["left"] = True
            elif selected_piece == "r" and sr == 0 and sc == 7:
                black_rook_moved["right"] = True

            # -------- SWITCH TURN --------
            current_turn = "black" if current_turn == "white" else "white"
            turn_label.config(text=f"{current_turn.capitalize()}'s turn")

            # -------- COMPUTER MOVE --------
            if current_turn == "black":
                root.after(300, computer_move)

            # -------- CHECKMATE --------
            if is_checkmate(current_turn):
                winner = "white" if current_turn == "black" else "black"
                show_game_over(winner)
                canvas.unbind("<Button-1>")

    selected_square = None
    canvas.delete("all")
    draw_board()
    draw_pieces()




# -----------------------------
# BIND EVENTS
# -----------------------------
canvas.bind("<Button-1>", on_click)
root.bind("q", lambda e: root.destroy())
root.bind("Q", lambda e: root.destroy())
root.bind("z", undo_move)
root.bind("Z", undo_move)
root.bind("r", restart_game)
root.bind("R", restart_game)

canvas.bind("<ButtonPress-1>", on_drag_start)
canvas.bind("<B1-Motion>", on_drag_motion)
canvas.bind("<ButtonRelease-1>", on_drag_release)




# -----------------------------
# START GAME
# -----------------------------
draw_board()
draw_pieces()
root.mainloop()
