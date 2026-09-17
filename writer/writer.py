#!/usr/bin/env python3
"""writer.py — the agent that writes. Gathers the day's sources, makes ONE headless call with NO tools,
checks the answer looks like a report, and writes the parts it has — naming the parts it doesn't.

    python3 writer.py                  # dry run: print the report, write nothing
    python3 writer.py --apply          # write reports/YYYY/MM/YYYY-MM-DD.md
    python3 writer.py --date 2026-09-15
"""
import argparse, datetime, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from backend import ask

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
PROMPT = (HERE / "prompts/nightly.md").read_text()
SCHEMA = json.loads((HERE / "prompts/nightly.schema.json").read_text())
MIN_CHARS = 400


def sources(day):
    stem = f"{day:%Y/%m/%Y-%m-%d}"
    return {
        "terminal log": ROOT / "logs" / f"{stem}.md",
        "reading notes": ROOT / "reader" / "reading" / f"{day:%Y/%m}",   # a folder: all notes of the day
    }


def gather(day):
    found, missing = {}, []
    for name, path in sources(day).items():
        if path.is_dir():
            texts = [p.read_text() for p in sorted(path.glob(f"{day:%Y-%m-%d}-*.md"))]
            if texts: found[name] = "\n\n".join(texts)
            else: missing.append(name)
        elif path.is_file():
            found[name] = path.read_text()
        else:
            missing.append(name)
    return found, missing


def looks_like_report(text):
    lines = text.strip().splitlines()
    if not lines or not lines[0].startswith("# "):
        return False, "no level-one heading"
    first = lines[0].lower()
    for word in ("saved", "written", "created", "i have", "i've", "done"):
        if word in first:
            return False, f"confirmation, not a report: {lines[0]!r}"
    if len(text) < MIN_CHARS:
        return False, f"too short ({len(text)} chars)"
    return True, "ok"


def build(day, found, missing):
    """Write the parts you have; name the part you don't. Never invent, never crash."""
    if found:
        prompt = PROMPT + "".join(f"\n\n## {k}\n\n{v}" for k, v in found.items())
        try:
            body = ask(prompt, tools="", schema=SCHEMA)["report"]
            ok, why = looks_like_report(body)
            if not ok:
                print(f"REJECTED: {why}", file=sys.stderr)
                body = f"_No analysis was generated this run: {why}._"
        except Exception as e:
            print(f"no analysis: {e}", file=sys.stderr)
            body = "_No analysis was generated this run: the model call failed._"
    else:
        body = "_No analysis was generated this run: no sources found._"
    lines = [body.strip(), "", "---", f"sources: {', '.join(found) or 'none'}"]
    check = ROOT / "state" / "check.json"
    if check.exists() and (problems := json.loads(check.read_text())):
        lines.insert(0, f"**{len(problems)} things need you:** " + "; ".join(problems) + "\n")
    if missing:
        lines.append(f"missing: {', '.join(missing)}")
    lines.append(f"built: {datetime.datetime.now():%Y-%m-%dT%H:%M}")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true"); ap.add_argument("--date")
    args = ap.parse_args()
    day = datetime.date.fromisoformat(args.date) if args.date else datetime.date.today()
    out = ROOT / "reports" / f"{day:%Y/%m/%Y-%m-%d}.md"
    if out.exists() and args.apply:
        sys.exit(f"exists: {out.relative_to(ROOT)} — delete it to rebuild")
    report = build(day, *gather(day))
    if args.apply:
        out.parent.mkdir(parents=True, exist_ok=True); out.write_text(report); print(f"wrote {out.relative_to(ROOT)}")
    else:
        print(report)


if __name__ == "__main__":
    main()
