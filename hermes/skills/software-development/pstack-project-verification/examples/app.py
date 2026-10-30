"""Synthetic user-facing CLI, not production verification."""
from __future__ import annotations
import sys
if __name__ == '__main__':
    if sys.argv[1:] == ['deposit', '2']:
        print('balance=2; deposit accepted')
    else:
        sys.exit(1)
