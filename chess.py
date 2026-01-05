# chess.py
"""
==============================
 CHESS GAME WITH BASIC RULES
 Python + Tkinter
==============================
"""

import tkinter as tk
from PIL import Image, ImageTk
from sound import play_sound
from ui import create_ui
from draw import draw_board, draw_pieces, highlight_square, show_legal_moves, redraw
from ai import computer_move
from helper import is_white, is_black, is_legal_move, king_in_check, is_checkmate
from game import Game

# -----------------------------
# CONSTANTS
# -----------------------------
BOARD_SIZE = 8
SQUARE_SIZE = 80
MARGIN = 40  # space for numbers/letters

# -----------------------------
# CREATE GAME OBJECT
# -----------------------------
game = Game()

# -----------------------------
# CREATE UI
# -----------------------------
root, canvas, turn_label, move_log = create_ui(BOARD_SIZE, SQUARE_SIZE, MARGIN)
game.root = root
game.canvas = canvas
game.turn_label = turn_label
game.move_log = move_log

# -----------------------------
# LOAD PIECES IMAGES
# -----------------------------
pieces_files = {
    "r": "images/black-rook.png",
    "n": "images/black-knight.png",
    "b": "images/black-bishop.png",
    "q": "images/black-queen.png",
    "k": "images/black-king.png",
    "p": "images/black-pawn.png",
    "R": "images/white-rook.png",
    "N": "images/white-knight.png",
    "B": "images/white-bishop.png",
    "Q": "images/white-queen.png",
    "K": "images/white-king.png",
    "P": "images/white-pawn.png",
}

pieces = {}
for key, file in pieces_files.items():
    img = Image.open(file).convert("RGBA")
    img = img.resize((SQUARE_SIZE - 10, SQUARE_SIZE - 10), Image.Resampling.LANCZOS)
    pieces[key] = ImageTk.PhotoImage(img)

# -----------------------------
# MOVE LOGGING
# -----------------------------
def log_move(sr, sc, tr, tc, piece):
    start = chr(ord('a') + sc) + str(8 - sr)
    end = chr(ord('a') + tc) + str(8 - tr)
    move_text = f"{game.move_number}. {start} → {end} ({piece})\n"

    game.move_log.config(state='normal')
    game.move_log.insert(tk.END, move_text)
    game.move_log.see(tk.END)
    game.move_log.config(state='disabled')

    if game.current_turn == "black":
        game.move_number += 1

# -----------------------------
# PAWN PROMOTION
# -----------------------------
def promote_pawn(tr, tc):
    piece = game.board[tr][tc]
    if (piece == "P" and tr == 0) or (piece == "p" and tr == 7):
        popup = tk.Toplevel(game.root)
        popup.title("Promote Pawn")
        tk.Label(popup, text="Choose promotion:", font=("Arial", 12)).pack(pady=5)

        def choose(new_piece):
            game.board[tr][tc] = new_piece
            play_sound("promote")
            popup.destroy()
            redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, pieces)

        options = ["Q", "R", "B", "N"] if piece.isupper() else ["q", "r", "b", "n"]
        for p in options:
            tk.Button(popup, text=p, font=("Arial", 24), command=lambda p=p: choose(p)).pack(side="left", padx=5, pady=5)

# -----------------------------
# GAME OVER
# -----------------------------
def show_game_over(winner):
    play_sound("game_end")
    game.move_log.config(state='normal')
    game.move_log.insert(tk.END, f"\nCHECKMATE! {winner.upper()} WINS\n")
    game.move_log.see(tk.END)
    game.move_log.config(state='disabled')

# -----------------------------
# UNDO
# -----------------------------
def undo_move(event=None):
    if game.board_history:
        game.board = game.board_history.pop()
        game.current_turn = "black" if game.current_turn == "white" else "white"
        if game.current_turn == "white":
            game.move_number = max(1, game.move_number-1)
        game.move_log.config(state='normal')
        game.move_log.delete("end-2l", "end-1l")
        game.move_log.config(state='disabled')
        redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, pieces)

# -----------------------------
# RESTART
# -----------------------------
def restart_game(event=None):
    game.board = [row.copy() for row in game.initial_board]
    game.current_turn = "white"
    game.move_number = 1
    game.board_history = []
    game.move_log.config(state='normal')
    game.move_log.delete(1.0, tk.END)
    game.move_log.config(state='disabled')
    redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, pieces)

# -----------------------------
# DRAG & DROP HANDLERS
# -----------------------------
def on_drag_start(event):
    col = (event.x - MARGIN) // SQUARE_SIZE
    row = event.y // SQUARE_SIZE
    if not (0 <= row < 8 and 0 <= col < 8):
        return
    piece = game.board[row][col]
    if piece == ".":
        return
    if game.current_turn == "white" and is_black(piece): return
    if game.current_turn == "black" and is_white(piece): return

    game.dragging_piece = piece
    game.drag_start = (row, col)
    game.is_dragging = True
    game.drag_image = game.canvas.create_image(event.x, event.y, image=pieces[piece])

def on_drag_motion(event):
    if game.drag_image:
        game.canvas.coords(game.drag_image, event.x, event.y)

def reset_drag():
    game.dragging_piece = None
    game.drag_start = None
    game.is_dragging = False
    game.drag_image = None

def on_drag_release(event):
    if not game.dragging_piece or not game.drag_start:
        return

    sr, sc = game.drag_start
    tr = event.y // SQUARE_SIZE
    tc = (event.x - MARGIN) // SQUARE_SIZE
    piece = game.dragging_piece
    backup_board = [row.copy() for row in game.board]

    if 0 <= tr < 8 and 0 <= tc < 8 and is_legal_move(game, piece, sr, sc, tr, tc):
        # MOVE
        from helper import make_move
        make_move(game, sr, sc, tr, tc)
        promote_pawn(tr, tc)
        log_move(sr, sc, tr, tc, piece)
        game.current_turn = "black" if game.current_turn == "white" else "white"
        game.turn_label.config(text=f"{game.current_turn.capitalize()}'s turn")
        # COMPUTER MOVE
        if game.current_turn == "black":
            root.after(300, lambda: computer_move(game))
    else:
        game.board = backup_board
        play_sound("illegal")

    reset_drag()
    redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, pieces)

# -----------------------------
# MOUSE CLICK
# -----------------------------
def on_click(event):
    if game.is_dragging:
        return
    col = (event.x - MARGIN) // SQUARE_SIZE
    row = event.y // SQUARE_SIZE
    if not (0 <= row < 8 and 0 <= col < 8): return
    piece = game.board[row][col]

    if game.selected_square is None:
        if piece == ".": return
        if game.current_turn == "white" and is_black(piece): return
        if game.current_turn == "black" and is_white(piece): return
        game.selected_square = (row, col)
        redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, pieces)
        highlight_square(game, row, col, SQUARE_SIZE, MARGIN)
        show_legal_moves(game, row, col, SQUARE_SIZE, MARGIN)
        return

    # Move selected piece
    sr, sc = game.selected_square
    selected_piece = game.board[sr][sc]
    if piece != "." and is_white(piece) == is_white(selected_piece):
        game.selected_square = (row, col)
        redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, pieces)
        highlight_square(game, row, col, SQUARE_SIZE, MARGIN)
        show_legal_moves(game, row, col, SQUARE_SIZE, MARGIN)
        return

    from helper import make_move
    if is_legal_move(game, selected_piece, sr, sc, row, col):
        make_move(game, sr, sc, row, col)
        log_move(sr, sc, row, col, selected_piece)
        promote_pawn(row, col)
        game.current_turn = "black" if game.current_turn == "white" else "white"
        game.turn_label.config(text=f"{game.current_turn.capitalize()}'s turn")
        if game.current_turn == "black":
            root.after(300, lambda: computer_move(game))

        if is_checkmate(game, game.current_turn):
            winner = "white" if game.current_turn == "black" else "black"
            show_game_over(winner)

    game.selected_square = None
    redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, pieces)

# -----------------------------
# BIND EVENTS
# -----------------------------
canvas.bind("<Button-1>", on_click)
canvas.bind("<ButtonPress-1>", on_drag_start)
canvas.bind("<B1-Motion>", on_drag_motion)
canvas.bind("<ButtonRelease-1>", on_drag_release)

root.bind("q", lambda e: root.destroy())
root.bind("Q", lambda e: root.destroy())
root.bind("z", undo_move)
root.bind("Z", undo_move)
root.bind("r", restart_game)
root.bind("R", restart_game)

# -----------------------------
# START GAME
# -----------------------------
redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, pieces)
play_sound("game_start")
root.mainloop()
