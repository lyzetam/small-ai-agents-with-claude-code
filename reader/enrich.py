#!/usr/bin/env python3
"""enrich.py — adds a summary to every reading note that doesn't have one. Idempotent: a note is
enriched once, marked, and skipped forever after, so a better prompt can be re-run over everything.
Never touches the network or the source; the model gets the stored text and no tools."""
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from backend import ask

HERE = pathlib.Path(__file__).resolve().parent
MARK = "<!-- enriched -->"
PROMPT = "Summarize the article below in one sentence, then give three key points as a bulleted list. Plain English. No preamble.\n\n"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true"); args = ap.parse_args()
    notes = sorted((HERE / "reading").glob("*/*/*.md"))
    todo = [n for n in notes if MARK not in n.read_text()]
    for n in todo:
        print(f"[{'APPLY' if args.apply else 'DRY'}] enrich {n.relative_to(HERE)}")
        if args.apply:
            body = n.read_text()
            summary = ask(PROMPT + body.split("---", 2)[-1], tools="")
            n.write_text(body.rstrip() + f"\n\n## Summary\n\n{summary.strip()}\n{MARK}\n")
    print(f"{len(notes)} notes, {len(notes)-len(todo)} already enriched, {len(todo)} {'enriched' if args.apply else 'to do'}")


if __name__ == "__main__":
    main()
