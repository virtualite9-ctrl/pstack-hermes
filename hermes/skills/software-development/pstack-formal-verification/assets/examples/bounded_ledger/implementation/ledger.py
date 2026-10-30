"""Synthetic bounded ledger only; not a production or unbounded proof."""
from __future__ import annotations

class Ledger:
    def __init__(self):
        self.balance = 0

    def apply(self, amount):
        candidate = self.balance + amount
        if 0 <= candidate <= 3:
            self.balance = candidate
        return self.balance
