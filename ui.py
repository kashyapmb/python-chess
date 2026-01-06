import tkinter as tk

def create_ui(BOARD_SIZE, SQUARE_SIZE, MARGIN, game):
    # -----------------------
    # ROOT WINDOW
    # -----------------------
    root = tk.Tk()
    root.title("♟ Python Chess")
    root.configure(bg="#2b2b2b")

    # Window size
    board_width = BOARD_SIZE * SQUARE_SIZE
    board_height = BOARD_SIZE * SQUARE_SIZE
    side_width = 260
    window_width = MARGIN + board_width + side_width + 40
    window_height = board_height + 40

    # Center window
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.minsize(window_width, window_height)

    # -----------------------
    # MAIN FRAME
    # -----------------------
    main_frame = tk.Frame(root, bg="#2b2b2b", padx=20, pady=20)
    main_frame.pack(expand=True, fill="both")

    # -----------------------
    # BOARD CANVAS
    # -----------------------
    canvas = tk.Canvas(
        main_frame,
        width=board_width,
        height=board_height,
        bg="#1e1e1e",
        highlightthickness=2,
        highlightbackground="#555555"
    )
    canvas.grid(row=0, column=0, sticky="n")

    # -----------------------
    # SIDE PANEL
    # -----------------------
    side_frame = tk.Frame(
        main_frame,
        bg="#1f1f1f",
        width=side_width,
        padx=15,
        pady=15
    )
    side_frame.grid(row=0, column=1, sticky="ns", padx=(20, 0))
    side_frame.grid_propagate(False)

    # -----------------------
    # TURN LABEL
    # -----------------------
    turn_label = tk.Label(
        side_frame,
        text="White to Move",
        font=("Segoe UI", 16, "bold"),
        bg="#1f1f1f",
        fg="#f5f5f5"
    )
    turn_label.pack(pady=(0, 20))

    # -----------------------
    # MOVE LOG TITLE
    # -----------------------
    log_title = tk.Label(
        side_frame,
        text="Move History",
        font=("Segoe UI", 13, "bold"),
        bg="#1f1f1f",
        fg="#cccccc"
    )
    log_title.pack(anchor="w")

    # -----------------------
    # MOVE LOG FRAME
    # -----------------------
    move_log_frame = tk.Frame(side_frame, bg="#1f1f1f")
    move_log_frame.pack(fill="both", expand=True, pady=(10, 0))

    move_log = tk.Text(
        move_log_frame,
        state="disabled",
        font=("Consolas", 12),
        bg="#111111",
        fg="#ffffff",
        insertbackground="white",
        wrap="none",
        borderwidth=0,
        relief="flat"
    )
    move_log.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(
        move_log_frame,
        command=move_log.yview,
        bg="#1f1f1f",
        troughcolor="#111111",
        activebackground="#444444"
    )
    scrollbar.pack(side="right", fill="y")
    move_log.config(yscrollcommand=scrollbar.set)

    # -----------------------
    # CLOCK LABELS (PvP)
    # -----------------------
    # Black → top-right of board
    black_clock_label = tk.Label(
        root,
        text="Black: 00:00",
        font=("Segoe UI", 14, "bold"),
        bg="#1f1f1f",
        fg="white"
    )
    black_clock_label.place(
        x=MARGIN + 8 * SQUARE_SIZE + 10,
        y=10
    )

    # White → bottom-right of board
    white_clock_label = tk.Label(
        root,
        text="White: 00:00",
        font=("Segoe UI", 14, "bold"),
        bg="#1f1f1f",
        fg="white"
    )
    white_clock_label.place(
        x=MARGIN + 8 * SQUARE_SIZE + 10,
        y=8 * SQUARE_SIZE - 30
    )

    # -----------------------
    # GRID CONFIG
    # -----------------------
    main_frame.grid_columnconfigure(0, weight=0)
    main_frame.grid_columnconfigure(1, weight=1)
    main_frame.grid_rowconfigure(0, weight=1)

    # Attach clocks to game object
    game.black_clock_label = black_clock_label
    game.white_clock_label = white_clock_label

    # -----------------------
    # RETURN REFERENCES
    # -----------------------
    return root, canvas, turn_label, move_log
