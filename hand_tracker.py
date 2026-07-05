"""
hand_tracker.py
===============
This file is a thin "wrapper" around MediaPipe's hand model.

Its ONLY job: take a picture (a single webcam frame) and answer two questions:
    1. Is there a hand in this frame?
    2. If so, where are its 21 landmarks (dots on the joints/fingertips)?

We keep all the MediaPipe-specific details in here so the rest of the game
(main.py, gesture_classifier.py) never has to think about MediaPipe directly.
That separation is a normal way to organise real projects: each file has one job.
"""

import cv2            # OpenCV: image/colour handling. We need it for a colour conversion below.
import mediapipe as mp  # MediaPipe: the actual hand-detection AI model.


class HandTracker:
    """Wraps MediaPipe Hands so the rest of the code just calls find_hand()/draw()."""

    def __init__(self, detection_confidence=0.7, tracking_confidence=0.5):
        # mp.solutions.hands is the "Hands" solution inside MediaPipe.
        self.mp_hands = mp.solutions.hands

        # This is the model itself. A few settings worth understanding:
        #   max_num_hands=1        -> we only care about one hand (yours). Faster + simpler.
        #   min_detection_confidence -> how sure the model must be to say "that's a hand".
        #                               Higher = fewer false hands, but needs a clearer view.
        #   min_tracking_confidence  -> how sure it must be to keep following a hand it already found.
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,          # False = video mode (it "remembers" between frames -> smoother/faster)
            max_num_hands=1,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

        # drawing_utils is a helper that draws the dots + the lines connecting them.
        self.mp_draw = mp.solutions.drawing_utils

    def find_hand(self, frame):
        """
        Run hand detection on one frame.

        Returns the landmarks object for the first hand (has 21 points), or None
        if no hand was found. We hand this object straight to gesture_classifier.py.

        GOTCHA worth knowing: OpenCV gives us images in BGR order (Blue-Green-Red),
        but MediaPipe expects RGB (Red-Green-Blue). If you forget to convert, the
        model still runs but sees "wrong" colours and detects poorly. So we convert.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # .process() is where the AI actually looks at the image.
        results = self.hands.process(rgb_frame)

        # results.multi_hand_landmarks is None when no hand is seen,
        # otherwise it's a list (one entry per hand). We asked for max 1 hand,
        # so we just return the first entry.
        if results.multi_hand_landmarks:
            return results.multi_hand_landmarks[0]
        return None

    def draw(self, frame, hand_landmarks):
        """
        Draw the 21 dots + the connecting lines onto the frame, IN PLACE.

        This is purely so YOU can see what the model sees while playing/debugging.
        It doesn't affect the game logic at all.
        """
        if hand_landmarks is not None:
            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,  # tells it which dots to join with lines
            )
        return frame
