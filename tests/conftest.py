from __future__ import annotations

import sys
from pathlib import Path


# Ensure the project root (where `server.py` / `schemas.py` live) is importable
# when running `pytest` from different working directories / runners on Windows.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

