# start_game_dialog.py

import tkinter as tk
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

def start_game_dialog(game):
    popup = tk.Toplevel(game.root)
    popup.title("Game Settings")
    popup.resizable(True, True)
    popup.grab_set()

    mode_var = tk.StringVar(value="PVC")
    color_var = tk.StringVar(value="white")

    # ---------------- FIRST STEP: CHOOSE MODE ----------------
    tk.Label(popup, text="Select Game Mode").pack(anchor="w", pady=5)

    tk.Radiobutton(popup, text="Player vs Computer",
                   variable=mode_var, value="PVC").pack(anchor="w")

    tk.Radiobutton(popup, text="Player vs Player",
                   variable=mode_var, value="PVP").pack(anchor="w")

    # ------------- Frames for second step options -------------
    pvc_frame = tk.Frame(popup)
    pvp_frame = tk.Frame(popup)

    # ---------------- PVC OPTIONS ----------------
    tk.Label(pvc_frame, text="Choose Your Color").pack(anchor="w", pady=5)
    tk.Radiobutton(pvc_frame, text="White",
                   variable=color_var, value="white").pack(anchor="w")
    tk.Radiobutton(pvc_frame, text="Black",
                   variable=color_var, value="black").pack(anchor="w")

    # ---------------- PVP OPTIONS ----------------
    tk.Label(pvp_frame, text="Choose Your Color").pack(anchor="w", pady=5)
    tk.Radiobutton(pvp_frame, text="White",
                   variable=color_var, value="white").pack(anchor="w")
    tk.Radiobutton(pvp_frame, text="Black",
                   variable=color_var, value="black").pack(anchor="w")

    # Player Names
    tk.Label(pvp_frame, text="Player 1 Name:").pack(anchor="w", pady=2)
    p1_entry = tk.Entry(pvp_frame)
    p1_entry.pack(anchor="w")

    tk.Label(pvp_frame, text="Player 2 Name:").pack(anchor="w", pady=2)
    p2_entry = tk.Entry(pvp_frame)
    p2_entry.pack(anchor="w")

    # Different timestamps for each player
    tk.Label(pvp_frame, text="Player 1 Time").pack(anchor="w", pady=2)
    p1_time = tk.IntVar(value=5)
    for t in (5, 10, 15):
        tk.Radiobutton(pvp_frame, text=f"{t} minutes",
                       variable=p1_time, value=t).pack(anchor="w")

    tk.Label(pvp_frame, text="Player 2 Time").pack(anchor="w", pady=2)
    p2_time = tk.IntVar(value=10)
    for t in (5, 10, 15):
        tk.Radiobutton(pvp_frame, text=f"{t} minutes",
                       variable=p2_time, value=t).pack(anchor="w")

    # ------------- Toggle visibility based on mode -------------
    def toggle_frames(*args):
        pvc_frame.pack_forget()
        pvp_frame.pack_forget()

        if mode_var.get() == "PVC":
            pvc_frame.pack(anchor="w", pady=10)

        elif mode_var.get() == "PVP":
            pvp_frame.pack(anchor="w", pady=10)

    mode_var.trace_add("write", toggle_frames)

    # ---------------- START BUTTON LOGIC ----------------
    def start():
        selected_mode = mode_var.get()

        if not selected_mode:
            return  # no mode chosen

        game.mode = selected_mode
        game.player_color = color_var.get()

        if game.mode == "PVC":
            popup.destroy()

            # Remove clocks if PVC
            game.white_clock_label.config(text="")
            game.black_clock_label.config(text="")

            if game.player_color == "black":
                game.current_turn = "white"
                game.turn_label.config(text="White's turn")
                game.root.after(300, lambda: computer_move(game))
            else:
                game.current_turn = "white"

        else:
            # PVP MODE
            game.player1_name = p1_entry.get().strip() or "Player 1"
            game.player2_name = p2_entry.get().strip() or "Player 2"

            game.white_time = p1_time.get() * 60
            game.black_time = p2_time.get() * 60
            game.clock_running = False

            # Update clock labels with different times
            game.white_clock_label.config(
                text=f"{game.player1_name}: {p1_time.get()} min"
            )
            game.black_clock_label.config(
                text=f"{game.player2_name}: {p2_time.get()} min"
            )

            popup.destroy()

        
        redraw(game, 8, 80, 40, game.pieces)
        play_sound("game_start")

    tk.Button(popup, text="Start Game",
              command=start).pack(anchor="center", pady=10)
