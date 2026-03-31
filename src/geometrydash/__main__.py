#!/usr/bin/env python3
"""
Run the Geometry Dash game:

    python -m geometrydash      ← run directly in terminal
    briefcase run macOS         ← run as bundled .app
"""
# Fix iOS locale crash (toga calls locale.setlocale which fails on iOS)
import os
os.environ.setdefault("LANG", "C")
os.environ.setdefault("LC_ALL", "C")

from geometrydash.game import main  # returns GeometryDashApp instance


if __name__ == "__main__":
    main().main_loop()
