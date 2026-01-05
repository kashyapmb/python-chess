import tkinter as tk

def create_ui(BOARD_SIZE, SQUARE_SIZE, MARGIN):
    # -----------------------
    # ROOT WINDOW
    # -----------------------
    root = tk.Tk()
    root.title("Python Chess")
    root.configure(bg="#f0f0f0")

    # Center the window
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = MARGIN + BOARD_SIZE * SQUARE_SIZE + 250  # extra for move log
    window_height = BOARD_SIZE * SQUARE_SIZE + MARGIN + 20
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.resizable(True, True)

    # -----------------------
    # MAIN FRAME
    # -----------------------
    main_frame = tk.Frame(root, bg="#f0f0f0", padx=10, pady=10)
    main_frame.pack(expand=True, fill="both")

    # -----------------------
    # CANVAS (BOARD)
    # -----------------------
    canvas = tk.Canvas(
        main_frame,
        width=MARGIN + BOARD_SIZE * SQUARE_SIZE,
        height=BOARD_SIZE * SQUARE_SIZE + MARGIN,
        bg="#ffffff",
        highlightthickness=0
    )
    canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    # -----------------------
    # SIDE PANEL
    # -----------------------
    side_frame = tk.Frame(main_frame, bg="#f0f0f0")
    side_frame.grid(row=0, column=1, sticky="ns")

    # Turn label
    turn_label = tk.Label(
        side_frame, text="White's turn",
        font=("Arial", 14, "bold"),
        bg="#f0f0f0", fg="#333333"
    )
    turn_label.pack(pady=(0, 10))

    # Move log
    move_log_frame = tk.Frame(side_frame, bg="#f0f0f0")
    move_log_frame.pack()

    move_log = tk.Text(
        move_log_frame,
        width=20,
        height=20,
        state="disabled",
        font=("Courier", 12),
        bg="#e8e8e8",
        fg="#000000",
        wrap="none",
        borderwidth=2,
        relief="sunken"
    )
    move_log.pack(side="left", fill="y")

    # Scrollbar
    scrollbar = tk.Scrollbar(move_log_frame, command=move_log.yview)
    scrollbar.pack(side="right", fill="y")
    move_log.config(yscrollcommand=scrollbar.set)

    # -----------------------
    # GRID CONFIG
    # -----------------------
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(0, weight=1)

    return root, canvas, turn_label, move_log
