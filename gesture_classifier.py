r"""
gesture_classifier.py
======================
This is the "brain" that turns 21 dots into a word: "rock", "paper", or "scissors".

The important idea for a beginner:
    MediaPipe already did the hard AI part (finding your hand). Everything in this
    file is just plain geometry — comparing where dots are. No machine learning from us.

--- The 21 landmarks ---
MediaPipe numbers the dots 0 to 20. A few we care about:

        8   12  16  20     <- FINGERTIPS (index, middle, ring, pinky)
        |   |   |   |
        6   10  14  18     <- the knuckle just below each tip (called the "PIP" joint)
         \  |   |  /
          \ |   | /
            0  (wrist)

So for the INDEX finger: dot 8 is the tip, dot 6 is the knuckle below it.

--- Coordinate gotcha ---
Each dot has an x and a y. In image coordinates, y = 0 is the TOP of the frame and
y grows as you go DOWN. So "higher on screen" means a SMALLER y.

Therefore a finger is EXTENDED (pointing up) when:
        tip.y  <  knuckle.y      (tip is higher on screen than its knuckle)

If the finger is curled, the tip flops down and its y becomes larger than the knuckle's.

We deliberately IGNORE the thumb: it moves sideways, not up/down, so this simple
up/down test is unreliable for it. Checking the other 4 fingers is enough to tell
rock/paper/scissors apart.
"""

# --- Landmark index constants (names are clearer than magic numbers) ---
# Fingertips:
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20

# The knuckle (PIP joint) just below each fingertip:
INDEX_PIP = 6
MIDDLE_PIP = 10
RING_PIP = 14
PINKY_PIP = 18

# Pair each fingertip with its knuckle so we can loop over them cleanly.
# Order is [index, middle, ring, pinky] and we keep that order everywhere.
FINGERS = [
    (INDEX_TIP, INDEX_PIP),
    (MIDDLE_TIP, MIDDLE_PIP),
    (RING_TIP, RING_PIP),
    (PINKY_TIP, PINKY_PIP),
]


def fingers_up(hand_landmarks):
    """
    Return a list of 4 booleans: [index_up, middle_up, ring_up, pinky_up].

    True  = that finger is extended (up)
    False = that finger is curled (down)

    hand_landmarks is the object MediaPipe gave us. hand_landmarks.landmark[i]
    is dot number i, and it has .x and .y (each a number from 0.0 to 1.0 across the frame).
    """
    lm = hand_landmarks.landmark  # shorthand
    result = []
    for tip_id, pip_id in FINGERS:
        # "tip is higher on screen than knuckle" -> finger is up.
        # Remember: smaller y = higher on screen.
        is_up = lm[tip_id].y < lm[pip_id].y
        result.append(is_up)
    return result


def classify(hand_landmarks):
    """
    Turn the finger pattern into a move.

    Returns one of: "rock", "paper", "scissors", or None.
    None means "the hand shape didn't clearly match any move" — the game uses that
    to nudge you to show your hand more clearly instead of guessing wrong.
    """
    if hand_landmarks is None:
        return None

    up = fingers_up(hand_landmarks)
    count = sum(up)  # how many of the 4 fingers are up (True counts as 1)

    index_up, middle_up, ring_up, pinky_up = up

    # ROCK = a fist = no fingers up.
    if count == 0:
        return "rock"

    # PAPER = open palm = all 4 fingers up.
    if count == 4:
        return "paper"

    # SCISSORS = index + middle up, ring + pinky down (the classic "peace sign").
    if index_up and middle_up and not ring_up and not pinky_up:
        return "scissors"

    # Anything else (e.g. only 1 or 3 fingers up) is ambiguous -> None.
    #
    # TUNING NOTE (read this if detection feels off for YOUR hand):
    #   - If scissors is hard to trigger, your ring/pinky might be reading as "up".
    #     Try curling them more, or loosen the rule to just: index_up and middle_up.
    #   - If rock/paper flicker, move your hand closer/steadier so MediaPipe sees it clearly.
    return None
