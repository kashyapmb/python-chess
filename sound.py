# sound.py
 
import pygame
import os

pygame.mixer.init()
pygame.mixer.music.set_volume(0.6)

# Map sound names to files
SOUNDS = {
    "capture": "sounds/capture.mp3",
    "castle": "sounds/castle.mp3",
    "game_end": "sounds/game-end.mp3",
    "game_start": "sounds/game-start.mp3",
    "illegal": "sounds/illegal.mp3",
    "check": "sounds/move-check.mp3",
    "move_self": "sounds/move-self.mp3",
    "move_opponent": "sounds/move-opponent.mp3",
    "premove": "sounds/premove.mp3",
    "promote": "sounds/promote.mp3",
}

def play_sound(sound_type):
    """
    Plays a chess sound based on the sound_type string.
    Example:
        play_sound("piece_move")
        play_sound("check")
    """
    file = SOUNDS.get(sound_type)
    if not file:
        return  # invalid sound key

    if not os.path.exists(file):
        print(f"[Sound] Missing file: {file}")
        return

    pygame.mixer.music.load(file)
    pygame.mixer.music.play()