# ai.py
# ===============================
# COMPUTER PLAYER LOGIC
# ===============================

import random
from draw import redraw
from helper import (
    is_white,
    is_black,
    is_legal_move,
    make_move,
    king_in_check,
    is_checkmate
)


def get_all_legal_moves(game, color):
    """
    Returns a list of all legal moves for the given color.
    Each move is (sr, sc, tr, tc)
    """
    moves = []

    for sr in range(8):
        for sc in range(8):
            piece = game.board[sr][sc]
            if piece == ".":
                continue

            if color == "white" and not is_white(piece):
                continue
            if color == "black" and not is_black(piece):
                continue

            for tr in range(8):
                for tc in range(8):
                    if is_legal_move(game, piece, sr, sc, tr, tc):
                        moves.append((sr, sc, tr, tc))

    return moves


def evaluate_board(game):
    """
    Simple material-based evaluation
    """
    values = {
        "P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0,
        "p": -1, "n": -3, "b": -3, "r": -5, "q": -9, "k": 0
    }

    score = 0
    for row in game.board:
        for piece in row:
            score += values.get(piece, 0)

    return score


def choose_best_move(game, color):
    """
    Very basic AI:
    - Try all legal moves
    - Pick the one with best evaluation
    """
    best_score = None
    best_moves = []

    moves = get_all_legal_moves(game, color)

    for move in moves:
        sr, sc, tr, tc = move

        # Save state
        board_copy = [row.copy() for row in game.board]
        ep_copy = game.en_passant_target
        castling_state = (
            game.white_king_moved,
            game.black_king_moved,
            game.white_rook_moved.copy(),
            game.black_rook_moved.copy()
        )

        """
        Executes a move from (sr, sc) to (tr, tc) on the game.board.
        Handles normal moves, en passant, and castling.
        """
        piece = game.board[sr][sc]
        target = game.board[tr][tc]

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

            

            

        score = evaluate_board(game)
        if color == "black":
            score = -score

        # Restore state
        game.board = [row.copy() for row in board_copy]
        game.en_passant_target = ep_copy
        (
            game.white_king_moved,
            game.black_king_moved,
            game.white_rook_moved,
            game.black_rook_moved
        ) = castling_state

        if best_score is None or score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)

    if not best_moves:
        return None

    return random.choice(best_moves)


def computer_move(game):
    color = game.current_turn

    if is_checkmate(game, color):
        return

    move = choose_best_move(game, color)
    if not move:
        return

    sr, sc, tr, tc = move
    make_move(game, sr, sc, tr, tc)

    game.current_turn = "black" if color == "white" else "white"
    game.turn_label.config(text=f"{game.current_turn.capitalize()}'s turn")

    redraw(game, 8, 80, 40, game.pieces)
