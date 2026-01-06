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
from helper import (
    is_white,
    is_black,
    is_legal_move,
    king_in_check,
    is_checkmate,
    make_move
)
from game import Game
from clock import start_clock, stop_clock, switch_clock


# -----------------------------
# CONSTANTS
# -----------------------------
BOARD_SIZE = 8
SQUARE_SIZE = 80
MARGIN = 40

# -----------------------------
# CREATE GAME OBJECT
# -----------------------------
game = Game()  # Everything is stored inside game

# Ensure required attributes exist
game.selected_square = None
game.dragging_piece = None
game.drag_start = None
game.drag_image = None
game.is_dragging = False

# -----------------------------
# CREATE UI
# -----------------------------
root, canvas, turn_label, move_log = create_ui(BOARD_SIZE, SQUARE_SIZE, MARGIN, game)

game.root = root
game.canvas = canvas
game.turn_label = turn_label
game.move_log = move_log

# -----------------------------
# LOAD PIECES
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

    text = f"{game.move_number}. {start} → {end}\n"

    game.move_log.config(state="normal")
    game.move_log.insert(tk.END, text)
    game.move_log.see(tk.END)
    game.move_log.config(state="disabled")

    if game.current_turn == "black":
        game.move_number += 1

# -----------------------------
# PAWN PROMOTION
# -----------------------------
def promote_pawn(tr, tc):
    piece = game.board[tr][tc]
    if not ((piece == "P" and tr == 0) or (piece == "p" and tr == 7)):
        return

    popup = tk.Toplevel(game.root)
    popup.title("Pawn Promotion")
    popup.resizable(False, False)

    tk.Label(popup, text="Promote to:", font=("Segoe UI", 12)).pack(pady=5)

    def choose(new_piece):
        game.board[tr][tc] = new_piece
        play_sound("promote")
        popup.destroy()
        redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, pieces)

    options = ["Q", "R", "B", "N"] if piece.isupper() else ["q", "r", "b", "n"]
    for p in options:
        tk.Button(
            popup,
            text=p,
            font=("Segoe UI", 20, "bold"),
            width=2,
            command=lambda p=p: choose(p)
        ).pack(side="left", padx=5, pady=10)

# -----------------------------
# GAME OVER
# -----------------------------
def show_game_over(winner):
    play_sound("game_end")
    stop_clock(game)
    game.move_log.config(state="normal")
    game.move_log.insert(tk.END, f"\nCHECKMATE — {winner.upper()} WINS\n")
    game.move_log.see(tk.END)
    game.move_log.config(state="disabled")

# -----------------------------
# DRAG & DROP
# -----------------------------
def on_drag_start(event):
    col = (event.x - MARGIN) // SQUARE_SIZE
    row = (event.y - MARGIN) // SQUARE_SIZE

    if not (0 <= row < 8 and 0 <= col < 8):
        return

    piece = game.board[row][col]
    if piece == ".":
        return
    if game.current_turn == "white" and is_black(piece):
        return
    if game.current_turn == "black" and is_white(piece):
        return

    game.dragging_piece = piece
    game.drag_start = (row, col)
    game.is_dragging = True
    game.drag_image = game.canvas.create_image(event.x, event.y, image=pieces[piece])

def on_drag_motion(event):
    if game.drag_image:
        game.canvas.coords(game.drag_image, event.x, event.y)

def reset_drag():
    if game.drag_image:
        game.canvas.delete(game.drag_image)
    game.dragging_piece = None
    game.drag_start = None
    game.drag_image = None
    game.is_dragging = False

def on_drag_release(event):
    if not game.dragging_piece or not game.drag_start:
        reset_drag()
        return

    sr, sc = game.drag_start
    tr = (event.y - MARGIN) // SQUARE_SIZE
    tc = (event.x - MARGIN) // SQUARE_SIZE

    if 0 <= tr < 8 and 0 <= tc < 8 and is_legal_move(game, game.dragging_piece, sr, sc, tr, tc):
        make_move(game, sr, sc, tr, tc)
        promote_pawn(tr, tc)
        log_move(sr, sc, tr, tc, game.dragging_piece)

        # PvP Clock
        if game.mode == "PVP":
            switch_clock(game)

        game.current_turn = "black" if game.current_turn == "white" else "white"
        game.turn_label.config(text=f"{game.current_turn.capitalize()}'s turn")

        if is_checkmate(game, game.current_turn):
            winner = "white" if game.current_turn == "black" else "black"
            show_game_over(winner)

        elif game.mode == "PVC" and game.current_turn != game.player_color:
            game.root.after(300, lambda: computer_move(game))

    else:
        play_sound("illegal")

    reset_drag()
    redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, pieces)

# -----------------------------
# BIND EVENTS
# -----------------------------
canvas.bind("<ButtonPress-1>", on_drag_start)
canvas.bind("<B1-Motion>", on_drag_motion)
canvas.bind("<ButtonRelease-1>", on_drag_release)
root.bind("z", lambda e: undo_move())
root.bind("Z", lambda e: undo_move())
root.bind("r", lambda e: restart_game())
root.bind("R", lambda e: restart_game())
root.bind("q", lambda e: root.destroy())
root.bind("Q", lambda e: root.destroy())

# -----------------------------
# START GAME DIALOG
# -----------------------------
def start_game_dialog():
    popup = tk.Toplevel(game.root)
    popup.title("Game Settings")
    popup.resizable(False, False)
    popup.grab_set()

    mode_var = tk.StringVar(value="PVC")
    color_var = tk.StringVar(value="white")
    time_var = tk.IntVar(value=10)

    tk.Label(popup, text="Game Mode").pack()
    tk.Radiobutton(popup, text="Player vs Computer", variable=mode_var, value="PVC").pack(anchor="w")
    tk.Radiobutton(popup, text="Player vs Player", variable=mode_var, value="PVP").pack(anchor="w")

    tk.Label(popup, text="Choose Color").pack()
    tk.Radiobutton(popup, text="White", variable=color_var, value="white").pack(anchor="w")
    tk.Radiobutton(popup, text="Black", variable=color_var, value="black").pack(anchor="w")

    tk.Label(popup, text="Time (PVP only)").pack()
    for t in (5, 10, 15):
        tk.Radiobutton(popup, text=f"{t} minutes", variable=time_var, value=t).pack(anchor="w")

    def start():
        game.mode = mode_var.get()
        game.player_color = color_var.get()

        if game.mode == "PVP":
            game.white_time = time_var.get() * 60
            game.black_time = time_var.get() * 60
            game.clock_running = False
            # Update clock labels
            game.white_clock_label.config(text=f"White: {game.white_time//60:02d}:00")
            game.black_clock_label.config(text=f"Black: {game.black_time//60:02d}:00")

        popup.destroy()

        if game.mode == "PVC" and game.player_color == "black":
            game.current_turn = "white"
            game.turn_label.config(text="White's turn")
            game.root.after(300, lambda: computer_move(game))

    tk.Button(popup, text="Start Game", command=start).pack(pady=10)

# -----------------------------
# START GAME
# -----------------------------
redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, pieces)
play_sound("game_start")
start_game_dialog()
root.mainloop()
