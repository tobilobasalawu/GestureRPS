"""
game_logic.py
=============
The pure "rules of the game" — no camera, no MediaPipe, no drawing.

Keeping this separate means you could unit-test it, or reuse it in a totally
different version of the game (a phone app, a text version...) without changing
a single line. That's the payoff of splitting files by responsibility.
"""

import random

# The three possible moves. Using a list keeps things tidy and lets the AI pick randomly.
MOVES = ["rock", "paper", "scissors"]

# What each move BEATS. Read it as: "rock beats scissors", etc.
# This one dictionary encodes the whole win logic.
BEATS = {
    "rock": "scissors",
    "paper": "rock",
    "scissors": "paper",
}


def random_ai_move():
    """Pick a move for the computer, completely at random."""
    return random.choice(MOVES)


def decide_winner(player_move, ai_move):
    """
    Compare two moves and say who won this round.

    Returns "player", "ai", or "tie".
    """
    if player_move == ai_move:
        return "tie"
    # If the player's move beats the AI's move, player wins.
    if BEATS[player_move] == ai_move:
        return "player"
    # Otherwise the AI wins.
    return "ai"


class Score:
    """
    Tracks the running score and decides when the MATCH (best-of-N) is over.

    best_of=5 means: first player to 3 round-wins takes the match
    (because you need more than half of 5). That gives the game a nice arc.
    """

    def __init__(self, best_of=5):
        self.player = 0          # player's round wins
        self.ai = 0              # ai's round wins
        self.best_of = best_of
        self.wins_needed = best_of // 2 + 1   # 5 -> 3, 3 -> 2, 7 -> 4

    def record(self, winner):
        """Update the score after a round. winner is 'player', 'ai', or 'tie'."""
        if winner == "player":
            self.player += 1
        elif winner == "ai":
            self.ai += 1
        # a tie changes nothing

    def match_over(self):
        """True once someone has reached the wins needed to take the match."""
        return self.player >= self.wins_needed or self.ai >= self.wins_needed

    def match_winner(self):
        """Who won the whole match? Only meaningful once match_over() is True."""
        if self.player >= self.wins_needed:
            return "player"
        if self.ai >= self.wins_needed:
            return "ai"
        return None

    def reset(self):
        """Start a fresh match (used when you press R after a match ends)."""
        self.player = 0
        self.ai = 0
