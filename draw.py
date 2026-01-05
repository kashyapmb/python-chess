# draw.py
# ===============================
# BOARD DRAWING & HIGHLIGHTS
# ===============================

from helper import (
    is_white,
    is_black,
    is_legal_move,
    king_in_check
)


def draw_board(game, BOARD_SIZE, SQUARE_SIZE, MARGIN):
    canvas = game.canvas
    canvas.delete("all")

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

    # Vertical margin line
    canvas.create_line(
        MARGIN, 0,
        MARGIN, BOARD_SIZE * SQUARE_SIZE,
        width=2
    )

    # Horizontal margin line
    canvas.create_line(
        MARGIN,
        BOARD_SIZE * SQUARE_SIZE,
        MARGIN + BOARD_SIZE * SQUARE_SIZE,
        BOARD_SIZE * SQUARE_SIZE,
        width=2
    )

    # Row numbers (8–1)
    for row in range(BOARD_SIZE):
        canvas.create_text(
            MARGIN // 2,
            row * SQUARE_SIZE + SQUARE_SIZE // 2,
            text=str(8 - row),
            font=("Arial", 12, "bold")
        )

    # Column letters (a–h)
    for col in range(BOARD_SIZE):
        canvas.create_text(
            MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2,
            BOARD_SIZE * SQUARE_SIZE + MARGIN // 2,
            text=chr(ord("a") + col),
            font=("Arial", 12, "bold")
        )


def draw_pieces(game, pieces, SQUARE_SIZE, MARGIN):
    canvas = game.canvas
    board = game.board

    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == ".":
                continue

            # Highlight king in check
            if (piece == "K" and king_in_check(game, "white")) or \
               (piece == "k" and king_in_check(game, "black")):
                canvas.create_rectangle(
                    MARGIN + c * SQUARE_SIZE,
                    r * SQUARE_SIZE,
                    MARGIN + (c + 1) * SQUARE_SIZE,
                    (r + 1) * SQUARE_SIZE,
                    outline="red",
                    width=3
                )

            canvas.create_image(
                MARGIN + c * SQUARE_SIZE + SQUARE_SIZE // 2,
                r * SQUARE_SIZE + SQUARE_SIZE // 2,
                image=pieces[piece]
            )

    # Highlight last move
    if game.board_history:
        last_board = game.board_history[-1]
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


def highlight_square(game, row, col, SQUARE_SIZE, MARGIN, color="#ADD8E6"):
    game.canvas.create_rectangle(
        MARGIN + col * SQUARE_SIZE,
        row * SQUARE_SIZE,
        MARGIN + (col + 1) * SQUARE_SIZE,
        (row + 1) * SQUARE_SIZE,
        fill=color,
        outline=""
    )


def show_legal_moves(game, sr, sc, SQUARE_SIZE, MARGIN):
    piece = game.board[sr][sc]

    for r in range(8):
        for c in range(8):
            if is_legal_move(game, piece, sr, sc, r, c):
                game.canvas.create_oval(
                    MARGIN + c * SQUARE_SIZE + 30,
                    r * SQUARE_SIZE + 30,
                    MARGIN + c * SQUARE_SIZE + 50,
                    r * SQUARE_SIZE + 50,
                    fill="green",
                    outline=""
                )


def redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, pieces):
    game.canvas.delete("all")
    draw_board(game, BOARD_SIZE, SQUARE_SIZE, MARGIN)
    draw_pieces(game, pieces, SQUARE_SIZE, MARGIN)
