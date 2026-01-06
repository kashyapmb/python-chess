def format_time(seconds):
    minutes = max(0, seconds) // 60
    secs = max(0, seconds) % 60
    return f"{minutes:02d}:{secs:02d}"


def tick(game):
    if not getattr(game, "clock_running", False):
        return

    if game.current_turn == "white":
        game.white_time -= 1
        if game.white_time <= 0:
            timeout(game, "black")
            return
    else:
        game.black_time -= 1
        if game.black_time <= 0:
            timeout(game, "white")
            return

    # Update clocks
    game.white_clock_label.config(text=f"White: {format_time(game.white_time)}")
    game.black_clock_label.config(text=f"Black: {format_time(game.black_time)}")

    game.root.after(1000, lambda: tick(game))


def start_clock(game):
    if game.mode != "PVP":
        # Remove clocks completely in PVC
        game.white_clock_label.place_forget()
        game.black_clock_label.place_forget()
        return

    if not game.clock_running:
        game.clock_running = True
        tick(game)



def stop_clock(game):
    game.clock_running = False


def switch_clock(game):
    if game.mode == "PVP":
        start_clock(game)


def timeout(game, winner):
    stop_clock(game)
    game.move_log.config(state="normal")
    game.move_log.insert("end", f"\nTIME OUT — {winner.upper()} WINS\n")
    game.move_log.see("end")
    game.move_log.config(state="disabled")
