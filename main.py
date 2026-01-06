# main.py
import tkinter as tk
from game import Game
from ui import create_ui
from start_game_dialog import start_game_dialog
from events import bind_events  # separate drag, undo, restart bindings

BOARD_SIZE = 8
SQUARE_SIZE = 80
MARGIN = 40

def main():
    # 1. Create game state
    game = Game()

    # 2. Create UI
    root, canvas, turn_label, move_log = create_ui(BOARD_SIZE, SQUARE_SIZE, MARGIN, game)
    game.root = root
    game.canvas = canvas
    game.turn_label = turn_label
    game.move_log = move_log

    # 3. Load piece images AFTER root exists
    game.load_pieces()

    # 4. Bind all events (drag, undo, restart)
    bind_events(game, canvas, root)

    # 5. Start settings dialog
    start_game_dialog(game)

    # 6. Run Tkinter
    root.mainloop()

if __name__ == "__main__":
    main()