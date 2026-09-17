"""memory.py — read at start, append at end. An agent may add lines; it never rewrites the file."""
import pathlib


def load(path) -> list[str]:
    p = pathlib.Path(path)
    return p.read_text().splitlines() if p.exists() else []


def append(path, line: str) -> None:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        f.write(line.rstrip() + "\n")
