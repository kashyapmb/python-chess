# game.py
# ===============================
# GAME STATE CONTAINER
# ===============================

class Game:
    def __init__(self):
        # -----------------------------
        # BOARD STATE
        # -----------------------------
        self.board = [
            list("rnbqkbnr"),
            list("pppppppp"),
            list("........"),
            list("........"),
            list("........"),
            list("........"),
            list("PPPPPPPP"),
            list("RNBQKBNR")
        ]

        self.initial_board = [row.copy() for row in self.board]
        self.board_history = []

        # -----------------------------
        # TURN & SELECTION
        # -----------------------------
        self.current_turn = "white"
        self.selected_square = None  # (row,col)

        # -----------------------------
        # SPECIAL MOVE STATE
        # -----------------------------
        self.en_passant_target = None # (row,col)

        # -----------------------------
        # CASTLING FLAGS
        # -----------------------------
        self.white_king_moved = False
        self.black_king_moved = False

        self.white_rook_moved = {
            "left": False, # rook on h1
            "right": False # rook on h8
        }
        self.black_rook_moved = {
            "left": False, # rook on a1
            "right": False # rook on a8
        }

        # -----------------------------
        # MOVE LOG
        # -----------------------------
        self.move_number = 1

        # -----------------------------
        # DRAG STATE
        # -----------------------------
        self.dragging_piece = None
        self.drag_start = None
        self.drag_image = None
        self.is_dragging = False

        # -----------------------------
        # UI REFERENCES (ASSIGNED LATER)
        # -----------------------------
        self.root = None
        self.canvas = None
        self.turn_label = None
        self.move_log = None
