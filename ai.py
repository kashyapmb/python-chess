# ai.py
# ===============================
# COMPUTER PLAYER LOGIC
# ===============================

import random
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

        make_move(game, sr, sc, tr, tc)

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
    """
    Executes the AI move for the current player
    """
    color = game.current_turn

    if is_checkmate(game, color):
        return

    move = choose_best_move(game, color)
    if move is None:
        return

    sr, sc, tr, tc = move

    # Save board for history
    game.board_history.append([row.copy() for row in game.board])

    make_move(game, sr, sc, tr, tc)

    # Switch turn
    game.current_turn = "black" if color == "white" else "white"
