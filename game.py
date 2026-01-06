# game.py
from PIL import Image, ImageTk

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

        self.pieces = {}

    def load_pieces(self):
        pieces_files = {
            "r": "images/black-rook.png",
            "n": "images/black-knight.png",
            "b": "images/black-bishop.png",
            "q": "images/black-queen.png",
            "k": "images/black-king.png",
            "p": "images/black-pawn.png",
            "R": "images/white-rook.png",
            "N": "images/white-knight.png",
            "B": "images/white-bishop.png",
            "Q": "images/white-queen.png",
            "K": "images/white-king.png",
            "P": "images/white-pawn.png",
        }
        for key, file in pieces_files.items():
            img = Image.open(file).convert("RGBA")
            img = img.resize((70, 70), Image.Resampling.LANCZOS)
            self.pieces[key] = ImageTk.PhotoImage(img, master=self.root)

