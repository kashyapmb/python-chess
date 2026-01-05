# helper.py
# ===============================
# CHESS RULES & VALIDATION
# ===============================

def is_white(piece):
    return piece.isupper()


def is_black(piece):
    return piece.islower()


def find_king(game, color):
    """Find king position for given color"""
    king = "K" if color == "white" else "k"
    for r in range(8):
        for c in range(8):
            if game.board[r][c] == king:
                return r, c
    return None


def path_clear(game, sr, sc, tr, tc):
    """Check if path is clear (rook, bishop, queen)"""
    dr = (tr - sr) and ((tr - sr) // abs(tr - sr))
    dc = (tc - sc) and ((tc - sc) // abs(tc - sc))

    r, c = sr + dr, sc + dc
    while (r, c) != (tr, tc):
        if game.board[r][c] != ".":
            return False
        r += dr
        c += dc
    return True


def is_legal_move(game, piece, sr, sc, tr, tc):
    board = game.board
    target = board[tr][tc]

    # Cannot capture own piece
    if target != "." and is_white(piece) == is_white(target):
        return False

    dr = tr - sr
    dc = tc - sc

    # -----------------------------
    # PAWN
    # -----------------------------
    if piece.lower() == "p":
        direction = -1 if is_white(piece) else 1
        start_row = 6 if is_white(piece) else 1

        # Forward move
        if dc == 0 and target == ".":
            if dr == direction:
                return True
            if sr == start_row and dr == 2 * direction and board[sr + direction][sc] == ".":
                return True

        # Diagonal capture
        if abs(dc) == 1 and dr == direction:
            if target != "." and is_white(piece) != is_white(target):
                return True

            # En passant
            if target == "." and game.en_passant_target == (tr, tc):
                return True

    # -----------------------------
    # ROOK
    # -----------------------------
    elif piece.lower() == "r":
        if sr == tr or sc == tc:
            return path_clear(game, sr, sc, tr, tc)

    # -----------------------------
    # BISHOP
    # -----------------------------
    elif piece.lower() == "b":
        if abs(dr) == abs(dc):
            return path_clear(game, sr, sc, tr, tc)

    # -----------------------------
    # QUEEN
    # -----------------------------
    elif piece.lower() == "q":
        if sr == tr or sc == tc or abs(dr) == abs(dc):
            return path_clear(game, sr, sc, tr, tc)

    # -----------------------------
    # KNIGHT
    # -----------------------------
    elif piece.lower() == "n":
        return (abs(dr), abs(dc)) in [(2, 1), (1, 2)]

    # -----------------------------
    # KING
    # -----------------------------
    elif piece.lower() == "k":
        # Normal move
        if abs(dr) <= 1 and abs(dc) <= 1:
            return True

        # ---------------- CASTLING ----------------
        if is_white(piece):
            if game.white_king_moved:
                return False
            row = 7
            enemy = "black"
        else:
            if game.black_king_moved:
                return False
            row = 0
            enemy = "white"

        # King-side castling
        if dr == 0 and dc == 2:
            if board[row][5] == "." and board[row][6] == ".":
                if not is_square_attacked(game, row, 4, enemy) and \
                   not is_square_attacked(game, row, 5, enemy) and \
                   not is_square_attacked(game, row, 6, enemy):
                    return True

        # Queen-side castling
        if dr == 0 and dc == -2:
            if board[row][1] == "." and board[row][2] == "." and board[row][3] == ".":
                if not is_square_attacked(game, row, 4, enemy) and \
                   not is_square_attacked(game, row, 3, enemy) and \
                   not is_square_attacked(game, row, 2, enemy):
                    return True

    return False


def is_square_attacked(game, row, col, by_color):
    board = game.board

    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == ".":
                continue

            if by_color == "white" and is_white(piece):
                if piece.lower() == "p":
                    if r - 1 == row and abs(c - col) == 1:
                        return True
                elif piece.lower() == "k":
                    if max(abs(r - row), abs(c - col)) == 1:
                        return True
                else:
                    if is_legal_move(game, piece, r, c, row, col):
                        return True

            if by_color == "black" and is_black(piece):
                if piece.lower() == "p":
                    if r + 1 == row and abs(c - col) == 1:
                        return True
                elif piece.lower() == "k":
                    if max(abs(r - row), abs(c - col)) == 1:
                        return True
                else:
                    if is_legal_move(game, piece, r, c, row, col):
                        return True

    return False


def king_in_check(game, color):
    king_pos = find_king(game, color)
    if not king_pos:
        return False

    kr, kc = king_pos
    opponent = "black" if color == "white" else "white"
    return is_square_attacked(game, kr, kc, opponent)


def has_legal_moves(game, color):
    board = game.board

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
                    if is_legal_move(game, piece, sr, sc, tr, tc):

                        backup_from = board[sr][sc]
                        backup_to = board[tr][tc]

                        board[tr][tc] = piece
                        board[sr][sc] = "."

                        illegal = king_in_check(game, color)

                        board[sr][sc] = backup_from
                        board[tr][tc] = backup_to

                        if not illegal:
                            return True
    return False


def is_checkmate(game, color):
    return king_in_check(game, color) and not has_legal_moves(game, color)

def make_move(game, sr, sc, tr, tc):
    """
    Executes a move from (sr, sc) to (tr, tc) on the game.board.
    Handles normal moves, en passant, and castling.
    """
    piece = game.board[sr][sc]
    target = game.board[tr][tc]

    # Save board for undo if needed
    game.board_history.append([row.copy() for row in game.board])

    # Normal move
    game.board[tr][tc] = piece
    game.board[sr][sc] = "."

    # Castling
    if piece.lower() == "k" and abs(tc - sc) == 2:
        row = sr
        if tc == 6:  # King-side
            game.board[row][5] = game.board[row][7]
            game.board[row][7] = "."
        elif tc == 2:  # Queen-side
            game.board[row][3] = game.board[row][0]
            game.board[row][0] = "."

    # En passant
    if piece.lower() == "p" and game.en_passant_target == (tr, tc) and target == ".":
        if piece.isupper():
            game.board[tr + 1][tc] = "."
        else:
            game.board[tr - 1][tc] = "."

    # Update castling flags
    if piece == "K":
        game.white_king_moved = True
    elif piece == "k":
        game.black_king_moved = True

    if piece == "R" and sr == 7 and sc == 0:
        game.white_rook_moved["left"] = True
    elif piece == "R" and sr == 7 and sc == 7:
        game.white_rook_moved["right"] = True
    elif piece == "r" and sr == 0 and sc == 0:
        game.black_rook_moved["left"] = True
    elif piece == "r" and sr == 0 and sc == 7:
        game.black_rook_moved["right"] = True

    # Update en passant target
    game.en_passant_target = None
    if piece.lower() == "p" and abs(tr - sr) == 2:
        game.en_passant_target = ((tr + sr) // 2, tc)

