"""Command-line entry point:  python -m adamas.fit KIND data.csv [--json]   (see adamas.fitting)."""
from .fitting import main

if __name__ == "__main__":
    raise SystemExit(main())
