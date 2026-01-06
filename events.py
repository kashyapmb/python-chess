# events.py
from draw import redraw
from helper import is_white, is_black, is_legal_move, make_move, is_checkmate
from clock import stop_clock, switch_clock
from main_helpers import log_move, promote_pawn, show_game_over
from sound import play_sound
from ai import computer_move
import tkinter as tk

BOARD_SIZE = 8
SQUARE_SIZE = 80
MARGIN = 40


def bind_events(game, canvas, root):
    canvas.bind("<ButtonPress-1>", lambda e: on_drag_start(game, e))
    canvas.bind("<B1-Motion>", lambda e: on_drag_motion(game, e))
    canvas.bind("<ButtonRelease-1>", lambda e: on_drag_release(game, e))
    root.bind("z", lambda e: undo_move(game))
    root.bind("Z", lambda e: undo_move(game))
    root.bind("r", lambda e: restart_game(game))
    root.bind("R", lambda e: restart_game(game))
    root.bind("q", lambda e: root.destroy())
    root.bind("Q", lambda e: root.destroy())

def on_drag_start(game, event):
    col = (event.x - MARGIN) // SQUARE_SIZE
    row = event.y // SQUARE_SIZE   # ← NO margin on Y

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

    game.drag_image = game.canvas.create_image(
        event.x,
        event.y,
        image=game.pieces[piece],
        tags="drag"
    )

def on_drag_motion(game, event):
    if game.drag_image:
        game.canvas.coords(game.drag_image, event.x, event.y)

def reset_drag(game):
    if game.drag_image:
        game.canvas.delete(game.drag_image)
    game.dragging_piece = None
    game.drag_start = None
    game.drag_image = None
    game.is_dragging = False

def on_drag_release(game, event):
    if not game.dragging_piece or not game.drag_start:
        reset_drag(game)
        return

    sr, sc = game.drag_start
    tr = event.y // SQUARE_SIZE
    tc = (event.x - MARGIN) // SQUARE_SIZE

    if not (0 <= tr < 8 and 0 <= tc < 8):
        reset_drag(game)
        return

    piece = game.dragging_piece

    if is_legal_move(game, piece, sr, sc, tr, tc):
        # move piece in board
        game.board[tr][tc] = piece
        game.board[sr][sc] = "."          # remove from old square
        game.board_history.append([row.copy() for row in game.board])

        promote_pawn(game, tr, tc)
        log_move(game, sr, sc, tr, tc, piece)

        if game.mode == "PVP":
            switch_clock(game)

        game.current_turn = "black" if game.current_turn == "white" else "white"
        game.turn_label.config(text=f"{game.current_turn.capitalize()}'s turn")

        if is_checkmate(game, game.current_turn):
            winner = "white" if game.current_turn == "black" else "black"
            show_game_over(game, winner)

        elif game.mode == "PVC":
            game.root.after(300, lambda: computer_move(game))

    else:
        play_sound("illegal")

    reset_drag(game)
    redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, game.pieces)


def undo_move(game):
    if not game.board_history:
        play_sound("illegal")
        return

    # Restore last board state
    game.board = game.board_history.pop()

    # Switch turn back
    game.current_turn = "black" if game.current_turn == "white" else "white"

    # Fix move number if needed
    if game.current_turn == "white":
        game.move_number = max(1, game.move_number - 1)

    # Remove last move from log
    game.move_log.config(state="normal")
    game.move_log.delete("end-2l", "end-1l")
    game.move_log.config(state="disabled")

    # Stop clocks in PVP
    if game.mode == "PVP":
        stop_clock(game)

    # Redraw UI
    redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, game.pieces)
    play_sound("move")



def restart_game(game):
    # Reset board to initial state
    game.board = [row.copy() for row in game.initial_board]

    # Reset turns and counters
    game.current_turn = "white"
    game.move_number = 1

    # Clear history
    game.board_history = []

    # Reset clocks if PVP
    if game.mode == "PVP":
        stop_clock(game)
        game.white_time = 10 * 60
        game.black_time = 10 * 60
        game.white_clock_label.config(text="White: 10:00")
        game.black_clock_label.config(text="Black: 10:00")

    # Clear move log
    game.move_log.config(state="normal")
    game.move_log.delete(1.0, tk.END)
    game.move_log.config(state="disabled")

    # Reset drag state
    reset_drag(game)

    # Redraw everything
    redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, game.pieces)

    play_sound("game_start")


