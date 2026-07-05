# Gesture Rock Paper Scissors — How It Works

A play-by-webcam Rock Paper Scissors game. You throw a real hand gesture at your camera,
the computer reads it, picks its own move, and keeps score (best of 5). This document
explains **what each piece is, why it's there, and how it all fits** — written for someone
new to code.

---

## 1. How to run it

Everything is already installed on your machine, so from inside this folder just run:

```bash
python3 main.py
```

A window opens showing your webcam.

**Controls**
- `SPACE` — throw a round (starts the Rock/Paper/Scissors countdown)
- `R` — start a new match once one is over
- `Q` or `ESC` — quit

The first time, macOS will ask permission for your **terminal to use the camera** — say yes.
If the window is black, another app (Zoom, FaceTime, Photo Booth) is probably holding the camera; close it.

---

## 2. The tech stack (what the tools do)

| Tool | What it is | What it does for us |
|------|-----------|---------------------|
| **Python** | the programming language | glue that runs everything |
| **OpenCV** (`cv2`) | a computer-vision library | grabs webcam frames, draws text/shapes, shows the window. "Eyes + a pen + a window." |
| **MediaPipe** | Google's ready-made AI models | finds your hand and returns **21 dots** on its joints/fingertips |
| **NumPy** | a maths library | the number-crunching engine the other two lean on (you never call it directly) |

**The single most important idea:** the *hard* part — recognising a hand in a photo — is done
for us by MediaPipe. It's a pre-trained neural network. Everything *we* wrote is simple
arithmetic on the dots it gives back. We did **not** train any AI.

---

## 3. The 21 hand landmarks

Every frame, MediaPipe hands us 21 numbered points (0–20) on your hand. Each point has an
`x` and a `y` telling us where it sits in the frame.

```
        8   12  16  20      <- fingertips: index, middle, ring, pinky
        |   |   |   |
        6   10  14  18      <- the knuckle just below each tip (the "PIP" joint)
         \  |   |  /
          \ |   | /
            0   (wrist)      (the thumb is dots 1-4, off to the side)
```

For each finger we only need two dots: the **tip** and the **knuckle below it**.

---

## 4. The clever trick: turning dots into a gesture

This is the heart of the game, and it's just a comparison.

**The y-axis is upside-down.** In images, `y = 0` is the **top** of the frame, and `y` gets
bigger as you go **down**. So "higher on the screen" means a **smaller** `y`.

That gives us a one-line test for whether a finger is sticking up:

> A finger is **extended (up)** when its tip is higher on screen than its knuckle —
> that is, `tip.y < knuckle.y`.

When you curl a finger, the tip flops downward and its `y` becomes *larger* than the knuckle's,
so the test flips to "down". We run this test on 4 fingers (index, middle, ring, pinky) and
**skip the thumb** — the thumb moves sideways, so an up/down test doesn't work well for it.

Then we map the pattern of up/down fingers to a move:

| Move | Fingers up | Looks like |
|------|-----------|-----------|
| **Rock** | 0 (all curled) | a fist |
| **Paper** | 4 (all extended) | an open palm |
| **Scissors** | index + middle only | a peace sign ✌️ |

Anything that doesn't cleanly match (e.g. just one finger up) returns `None`, and the game
asks you to show your hand more clearly instead of guessing.

---

## 5. The files and why they're split up

Each file has exactly **one job**. Splitting them this way is how real projects stay
readable — you always know where to look, and you can change one part without breaking others.

```
GestureRPS/
├── hand_tracker.py        # talks to MediaPipe: frame in  ->  21 dots out (and draws them)
├── gesture_classifier.py  # the geometry: 21 dots in  ->  "rock"/"paper"/"scissors"
├── game_logic.py          # the rules: AI's move, who wins, the score, best-of-5
├── main.py                # the conductor: camera loop + countdown + drawing on screen
├── requirements.txt       # the shopping list of libraries (already installed)
└── EXPLAINER.md           # this file
```

- **`hand_tracker.py`** hides all the MediaPipe details. One gotcha it handles: OpenCV stores
  colours as **BGR** (Blue-Green-Red) but MediaPipe wants **RGB**, so it converts before
  detecting. If you forgot this, detection would be poor.
- **`gesture_classifier.py`** is pure geometry (Section 4). It's the file you'd tweak first if
  a gesture reads wrong for your hand — the tuning notes are in the comments.
- **`game_logic.py`** has no camera and no drawing at all — just the rules. The entire
  win logic is one dictionary: `{"rock": "scissors", "paper": "rock", "scissors": "paper"}`
  ("rock beats scissors", and so on).
- **`main.py`** ties them together and handles the screen + keyboard.

---

## 6. The game loop and its "states"

`main.py` runs a loop: grab a frame → figure out what to draw → show it → check for a keypress
→ repeat, many times a second. To keep that organised, the game is always in one of **four
states** (held in a variable called `state`):

```
   live  ──SPACE──▶  countdown  ──"SHOOT!"──▶  result  ──SPACE──▶  live
    ▲                                             │
    │                                        (if someone hit
    │                                         best-of-5)
    │                                             ▼
    └──────────────── R ──────────────────  match_over
```

- **`live`** — normal webcam view; shows the gesture you're making *right now*. Waiting for SPACE.
- **`countdown`** — plays "ROCK… PAPER… SCISSORS… SHOOT!" (each word ~0.6s). On **SHOOT!** it
  freezes your hand, reads your move, and rolls the AI's move.
- **`result`** — shows both moves and who won the round, updates the score. SPACE for the next round.
- **`match_over`** — someone reached 3 wins; shows the final banner. R starts a fresh match.

Thinking in states like this is the standard way to build *any* game, not just this one.

---

## 7. Want to tinker? Good first changes

- **Make it endless instead of best-of-5:** in `main.py`, change `game_logic.Score(best_of=5)`
  to a bigger odd number like `best_of=9`.
- **Scissors won't trigger for you?** In `gesture_classifier.py`, loosen the scissors rule to
  just `index_up and middle_up` (ignore the ring/pinky check).
- **Change the countdown speed:** in `main.py`, edit `COUNTDOWN_STEP = 0.6` (seconds per word).
- **Different colours:** the `MOVE_COLOURS` dictionary near the top of `main.py`. Remember OpenCV
  colours are `(Blue, Green, Red)`, each 0–255.

Each of these is a one- or two-line edit — a safe way to learn by poking at working code.
