# main_helpers.py
from draw import redraw
from sound import play_sound
from helper import is_checkmate
from clock import stop_clock
import tkinter as tk


BOARD_SIZE = 8
SQUARE_SIZE = 80
MARGIN = 40


# -----------------------------
# MOVE LOGGING
# -----------------------------
def log_move(game,sr, sc, tr, tc, piece):
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
def promote_pawn(game, tr, tc):
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
        redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, game.pieces)

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
def show_game_over(game, winner):
    play_sound("game_end")
    stop_clock(game)
    game.move_log.config(state="normal")
    game.move_log.insert(tk.END, f"\nCHECKMATE — {winner.upper()} WINS\n")
    game.move_log.see(tk.END)
    game.move_log.config(state="disabled")
