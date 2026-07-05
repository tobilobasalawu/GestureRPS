"""
main.py
=======
The conductor. This file opens the webcam, runs the loop, draws everything on
screen, and calls the other three files at the right moments:

    hand_tracker.py       -> find + draw the hand
    gesture_classifier.py -> turn the hand into "rock"/"paper"/"scissors"
    game_logic.py         -> AI move, who won, score, best-of-5

Run it with:   python3 main.py
Controls:      SPACE = play a round     R = restart match     Q or ESC = quit

--- How the loop is organised (a "state machine") ---
At any moment the game is in ONE of four states, held in the variable `state`:

    "live"      -> live webcam, showing your current gesture. Press SPACE to start a round.
    "countdown" -> the "Rock... Paper... Scissors... SHOOT!" animation is playing.
    "result"    -> a round finished; showing both moves + who won. SPACE = next round.
    "match_over"-> someone reached best-of-5. Showing the final banner. R = new match.

Each frame we look at `state` and decide what to draw / what keys to react to.
Thinking in states is the standard way to build any game loop.
"""

import time
import cv2

from hand_tracker import HandTracker
from gesture_classifier import classify
import game_logic


# --- Colours (OpenCV uses BGR order, not RGB!) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (80, 220, 80)
RED = (60, 60, 235)
YELLOW = (60, 220, 235)
GREY = (200, 200, 200)

# A colour for each move, just for a bit of polish.
MOVE_COLOURS = {
    "rock": GREY,
    "paper": GREEN,
    "scissors": RED,
}

# How long each word of the countdown stays on screen, in seconds.
COUNTDOWN_STEP = 0.6
COUNTDOWN_WORDS = ["ROCK", "PAPER", "SCISSORS", "SHOOT!"]


def draw_text(frame, text, position, scale=1.0, colour=WHITE, thickness=2):
    """
    Helper: draw text with a black outline so it stays readable over any background.
    We draw the text twice — a thick black copy first, then the coloured copy on top.
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    x, y = position
    cv2.putText(frame, text, (x, y), font, scale, BLACK, thickness + 3, cv2.LINE_AA)
    cv2.putText(frame, text, (x, y), font, scale, colour, thickness, cv2.LINE_AA)


def draw_scoreboard(frame, score):
    """Top-left running tally: Player vs AI, plus the best-of target."""
    draw_text(frame, f"YOU {score.player}", (20, 45), 1.1, GREEN, 2)
    draw_text(frame, f"AI {score.ai}", (20, 90), 1.1, RED, 2)
    draw_text(frame, f"(first to {score.wins_needed})", (20, 125), 0.6, GREY, 1)


def main():
    # cv2.VideoCapture(0) opens the DEFAULT webcam. If you had multiple cameras
    # you'd try 1, 2, ... The 0 is the most common.
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open the webcam. Is another app using it? Try closing Zoom/FaceTime.")
        return

    tracker = HandTracker()
    score = game_logic.Score(best_of=5)

    # --- Game state variables ---
    state = "live"
    countdown_start = 0.0     # the time.time() when the countdown began
    player_move = None        # the move captured on SHOOT!
    ai_move = None
    round_result = None       # "player" / "ai" / "tie"
    current_gesture = None    # what your hand looks like RIGHT NOW (updated every frame in "live")

    print("Game window opened. Click it, then: SPACE = play, R = restart, Q = quit.")

    while True:
        # Grab one frame from the webcam. `ok` is False if the grab failed.
        ok, frame = cap.read()
        if not ok:
            print("Lost the camera feed.")
            break

        # Mirror the image left-to-right so it feels like a mirror (move right hand -> it goes right).
        frame = cv2.flip(frame, 1)

        # Always find the hand — we need it live in "live" state, and MediaPipe
        # stays "warm" if we keep feeding it frames.
        hand = tracker.find_hand(frame)
        frame = tracker.draw(frame, hand)

        # ---------------- STATE: LIVE ----------------
        # Show the webcam and the gesture you're currently making. Wait for SPACE.
        if state == "live":
            current_gesture = classify(hand)
            label = current_gesture.upper() if current_gesture else "SHOW HAND CLEARLY"
            colour = MOVE_COLOURS.get(current_gesture, YELLOW)
            draw_text(frame, f"Detected: {label}", (20, frame.shape[0] - 60), 0.9, colour, 2)
            draw_text(frame, "Press SPACE to throw", (20, frame.shape[0] - 20), 0.8, WHITE, 2)

        # ---------------- STATE: COUNTDOWN ----------------
        # Play "ROCK / PAPER / SCISSORS / SHOOT!" then capture the hand on SHOOT!.
        elif state == "countdown":
            elapsed = time.time() - countdown_start
            # Which word are we on? 0,1,2,3 based on how much time has passed.
            step = int(elapsed / COUNTDOWN_STEP)

            if step < len(COUNTDOWN_WORDS):
                word = COUNTDOWN_WORDS[step]
                # Big centred word.
                draw_text(frame, word, (frame.shape[1] // 2 - 140, frame.shape[0] // 2),
                          2.2, YELLOW, 4)
            else:
                # Time's up -> this is the SHOOT! moment. Freeze the player's move NOW.
                player_move = classify(hand)
                ai_move = game_logic.random_ai_move()

                if player_move is None:
                    # Couldn't read the hand at the crucial moment — replay the round.
                    draw_text(frame, "Didn't catch that — try again",
                              (frame.shape[1] // 2 - 260, frame.shape[0] // 2), 1.0, RED, 2)
                    cv2.imshow("Gesture Rock Paper Scissors", frame)
                    cv2.waitKey(900)  # brief pause so the message is readable
                    state = "live"
                else:
                    round_result = game_logic.decide_winner(player_move, ai_move)
                    score.record(round_result)
                    state = "match_over" if score.match_over() else "result"

        # ---------------- STATE: RESULT ----------------
        # Show what each side threw and who won this round. Wait for SPACE.
        elif state == "result":
            draw_text(frame, f"You: {player_move.upper()}", (20, frame.shape[0] - 120),
                      1.1, MOVE_COLOURS[player_move], 2)
            draw_text(frame, f"AI:  {ai_move.upper()}", (20, frame.shape[0] - 75),
                      1.1, MOVE_COLOURS[ai_move], 2)

            if round_result == "player":
                draw_text(frame, "YOU WIN THE ROUND!", (20, frame.shape[0] - 30), 1.0, GREEN, 2)
            elif round_result == "ai":
                draw_text(frame, "AI WINS THE ROUND", (20, frame.shape[0] - 30), 1.0, RED, 2)
            else:
                draw_text(frame, "TIE", (20, frame.shape[0] - 30), 1.0, YELLOW, 2)

            draw_text(frame, "SPACE = next round", (frame.shape[1] - 340, 45), 0.7, WHITE, 2)

        # ---------------- STATE: MATCH OVER ----------------
        # Someone reached best-of-5. Show the big banner. Wait for R (restart) or Q (quit).
        elif state == "match_over":
            winner = score.match_winner()
            banner = "YOU WON THE MATCH!" if winner == "player" else "AI WON THE MATCH"
            banner_colour = GREEN if winner == "player" else RED
            draw_text(frame, banner, (frame.shape[1] // 2 - 300, frame.shape[0] // 2),
                      1.6, banner_colour, 3)
            draw_text(frame, "R = play again    Q = quit",
                      (frame.shape[1] // 2 - 260, frame.shape[0] // 2 + 60), 0.9, WHITE, 2)

        # The scoreboard is always visible.
        draw_scoreboard(frame, score)

        # Show the finished frame in a window.
        cv2.imshow("Gesture Rock Paper Scissors", frame)

        # --- Handle keyboard input ---
        # waitKey(1) waits 1ms for a key and returns its code (or -1 if none).
        # & 0xFF is a standard trick to read the key reliably across systems.
        key = cv2.waitKey(1) & 0xFF

        if key in (ord("q"), 27):        # 'q' or ESC
            break
        elif key == ord(" "):            # SPACE
            if state == "live":
                state = "countdown"
                countdown_start = time.time()
            elif state == "result":
                state = "live"           # go back to live feed for the next throw
        elif key == ord("r"):            # R
            if state == "match_over":
                score.reset()
                state = "live"

    # Clean up: release the camera and close the window.
    cap.release()
    cv2.destroyAllWindows()


# This line means: only run main() if you launched THIS file directly
# (i.e. `python3 main.py`), not if some other file imported it.
if __name__ == "__main__":
    main()
