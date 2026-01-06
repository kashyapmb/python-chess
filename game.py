# game.py
class Game:
    def __init__(self):
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

        self.current_turn = "white"
        self.selected_square = None

        self.en_passant_target = None

        self.white_king_moved = False
        self.black_king_moved = False

        self.white_rook_moved = {"left": False, "right": False}
        self.black_rook_moved = {"left": False, "right": False}

        self.move_number = 1

        self.dragging_piece = None
        self.drag_start = None
        self.drag_image = None
        self.is_dragging = False

        self.root = None
        self.canvas = None
        self.turn_label = None
        self.move_log = None

        # -----------------------------
        # CLOCK (PVP ONLY)
        # -----------------------------
        self.clock_running = False
        self.white_time = 0
        self.black_time = 0
        self.mode = None   # "PVC" or "PVP"

