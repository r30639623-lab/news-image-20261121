#!/usr/bin/env python3
"""Entry point: copy the rendered front page to $MAKEFUN_OUTPUT_DIR/entry.png.

Standard library only. Never writes into the repo (read-only on the grader).
Deterministic by construction: a byte copy of news.png.
"""
import os
import shutil
from pathlib import Path


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    root = Path(__file__).resolve().parent
    src = root / "news.png"
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, out_dir / "entry.png")
    print("wrote " + str(out_dir / "entry.png"))


if __name__ == "__main__":
    main()
