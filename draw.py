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

# -------------------------------
# COLORS (UI THEME)
# -------------------------------
LIGHT_SQUARE = "#f0d9b5"
DARK_SQUARE = "#b58863"
LAST_MOVE_COLOR = "#653b18"
CHECK_COLOR = "#ff4d4d"
LEGAL_MOVE_COLOR = "#4CAF50"
COORD_COLOR = "white"


def draw_board(game, BOARD_SIZE, SQUARE_SIZE, MARGIN):
    canvas = game.canvas
    canvas.delete("board")

    # -------------------------------
    # DRAW SQUARES
    # -------------------------------
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            canvas.create_rectangle(
                MARGIN + col * SQUARE_SIZE,
                row * SQUARE_SIZE,
                MARGIN + (col + 1) * SQUARE_SIZE,
                (row + 1) * SQUARE_SIZE,
                fill=color,
                outline="",
                tags="board"
            )

    # -------------------------------
    # BORDER LINES
    # -------------------------------
    canvas.create_rectangle(
        MARGIN,
        0,
        MARGIN + BOARD_SIZE * SQUARE_SIZE,
        BOARD_SIZE * SQUARE_SIZE,
        outline="#222222",
        width=2,
        tags="board"
    )

    # -------------------------------
    # ROW NUMBERS (8–1) → WHITE
    # -------------------------------
    for row in range(BOARD_SIZE):
        canvas.create_text(
            MARGIN // 2,
            row * SQUARE_SIZE + SQUARE_SIZE // 2,
            text=str(BOARD_SIZE - row),
            font=("Segoe UI", 12, "bold"),
            fill=COORD_COLOR,
            tags="board"
        )

    # -------------------------------
    # COLUMN LETTERS (a–h) → WHITE
    # -------------------------------
    for col in range(BOARD_SIZE):
        canvas.create_text(
            MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2,
            BOARD_SIZE * SQUARE_SIZE + MARGIN // 2,
            text=chr(ord("a") + col),
            font=("Segoe UI", 12, "bold"),
            fill=COORD_COLOR,
            tags="board"
        )


def draw_pieces(game, pieces, SQUARE_SIZE, MARGIN):
    canvas = game.canvas
    board = game.board

    # -------------------------------
    # LAST MOVE HIGHLIGHT (DRAW FIRST)
    # -------------------------------
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
                        fill=LAST_MOVE_COLOR,
                        outline=""
                    )

    # -------------------------------
    # DRAW PIECES (ON TOP)
    # -------------------------------
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == ".":
                continue

            # King in check highlight
            if (piece == "K" and king_in_check(game, "white")) or \
               (piece == "k" and king_in_check(game, "black")):
                canvas.create_rectangle(
                    MARGIN + c * SQUARE_SIZE,
                    r * SQUARE_SIZE,
                    MARGIN + (c + 1) * SQUARE_SIZE,
                    (r + 1) * SQUARE_SIZE,
                    outline=CHECK_COLOR,
                    width=4
                )

            canvas.create_image(
                MARGIN + c * SQUARE_SIZE + SQUARE_SIZE // 2,
                r * SQUARE_SIZE + SQUARE_SIZE // 2,
                image=pieces[piece]
            )


def highlight_square(game, row, col, SQUARE_SIZE, MARGIN, color="#a6dcef"):
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
                    MARGIN + c * SQUARE_SIZE + 26,
                    r * SQUARE_SIZE + 26,
                    MARGIN + c * SQUARE_SIZE + SQUARE_SIZE - 26,
                    r * SQUARE_SIZE + SQUARE_SIZE - 26,
                    fill=LEGAL_MOVE_COLOR,
                    outline=""
                )


def redraw(game, BOARD_SIZE, SQUARE_SIZE, MARGIN, pieces):
    game.canvas.delete("all")
    draw_board(game, BOARD_SIZE, SQUARE_SIZE, MARGIN)
    draw_pieces(game, pieces, SQUARE_SIZE, MARGIN)
