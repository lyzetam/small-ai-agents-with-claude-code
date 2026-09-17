#!/usr/bin/env python3
"""approve.py — the human's side of the line. Drafts wait in queue/pending/. You read, then move them.
Nothing in this folder can send, post or publish; 'approved' is where a human takes over.

    python3 approve.py pending
    python3 approve.py approve 2026-09-16-some-title.md
    python3 approve.py reject  2026-09-16-some-title.md
"""
import pathlib, shutil, sys
Q = pathlib.Path(__file__).resolve().parent / "queue"


def pending():
    for f in sorted((Q / "pending").glob("*.md")):
        print(f.name, "—", next((l[2:] for l in f.read_text().splitlines() if l.startswith("# ")), "")[:70])


def move(name, to):
    src = Q / "pending" / name
    if not src.exists():
        sys.exit(f"no such draft: {name}")
    (Q / to).mkdir(parents=True, exist_ok=True)
    shutil.move(src, Q / to / name)
    print(f"{name} -> {to}/")


if __name__ == "__main__":
    cmd, *args = sys.argv[1:] or ["pending"]
    {"pending": lambda: pending(), "approve": lambda: move(args[0], "approved"), "reject": lambda: move(args[0], "rejected")}[cmd]()
