# Gesture Rock Paper Scissors ✊✋✌️

Play Rock Paper Scissors against the computer using nothing but your webcam and your hand.
No controller, no mouse clicks — just throw a real gesture at the camera and the game reads it.

**[Watch the demo on YouTube](https://youtu.be/OE_sed2kIhk)**

## How it works

Every frame, [MediaPipe](https://developers.google.com/mediapipe) locates your hand and returns
21 landmark points (finger joints and tips). The game checks whether each fingertip sits above
or below its knuckle to decide if that finger is extended, then matches the pattern of
up/down fingers to a move:

| Move | Fingers up | Looks like |
|------|-----------|-----------|
| Rock | 0 | a fist |
| Paper | 4 | an open palm |
| Scissors | index + middle only | a peace sign ✌️ |

No machine learning was trained for this project — MediaPipe handles hand detection, and the
gesture logic itself is plain geometry. See [EXPLAINER.md](EXPLAINER.md) for a full, beginner-friendly
walkthrough of how everything fits together.

## Getting started

### Requirements

- Python 3
- A webcam

### Install

```bash
pip3 install -r requirements.txt
```

### Run

```bash
python3 main.py
```

A window opens showing your webcam feed with your hand tracked live.

### Controls

| Key | Action |
|-----|--------|
| `SPACE` | Throw a round (starts the Rock/Paper/Scissors countdown) |
| `R` | Start a new match once one is over |
| `Q` / `ESC` | Quit |

Matches are best-of-5 — first to 3 round wins takes it.

> **Note:** the first time you run the game, your OS may ask for camera permission for your
> terminal — allow it. If the window is black, another app (Zoom, FaceTime, Photo Booth, etc.)
> is probably holding the camera; close it and try again.

## Project structure

```
GestureRPS/
├── hand_tracker.py        # talks to MediaPipe: frame in -> 21 hand landmarks out
├── gesture_classifier.py  # geometry: landmarks in -> "rock"/"paper"/"scissors" out
├── game_logic.py          # rules: AI's move, who wins, scoring, best-of-5
├── main.py                # the conductor: camera loop, state machine, drawing
├── requirements.txt       # dependencies
└── EXPLAINER.md           # deep-dive write-up of how the whole game works
```

## Tech stack

- **Python** — glue that runs everything
- **[OpenCV](https://opencv.org/)** — webcam capture, drawing, and the game window
- **[MediaPipe](https://developers.google.com/mediapipe)** — pre-trained hand-tracking model
- **NumPy** — numerical backbone used under the hood by the other two

## License

No license specified.
