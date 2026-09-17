#!/usr/bin/env python3
"""decide.py — the agent that decides. Candidates minus the used-topics ledger → pick one (schema) →
research it (web search, its own clean room) → write it in a voice defined by files → a DRAFT in
queue/pending/ for a human to approve. It never publishes anything.

    python3 decide.py             # dry run: show candidates, run the pipeline, print the draft, write nothing
    python3 decide.py --apply     # write queue/pending/<date>-<slug>.md and append the used-topics ledger
    python3 decide.py --list      # just show today's candidates minus the ledger
"""
import argparse, datetime, json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from backend import ask
import memory

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
READING = ROOT / "reader" / "reading"
LEDGER = ROOT / "state" / "used-topics.txt"      # a set of ids, one per line
QUEUE = ROOT / "queue" / "pending"
LOOKBACK_DAYS = 2


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    fm = dict(re.findall(r"^(\w+):\s*\"?(.*?)\"?$", m.group(1), re.M)) if m else {}
    return fm, (m.group(2) if m else text)


def candidates(days):
    rows = []
    for day in days:
        for note in sorted((READING / f"{day:%Y/%m}").glob(f"{day:%Y-%m-%d}-*.md")):
            fm, body = frontmatter(note.read_text())
            summ = body.split("## Summary", 1)[1].strip()[:300] if "## Summary" in body else body.strip()[:300]
            rows.append({"id": fm.get("id", note.stem), "title": fm.get("title", note.stem), "url": fm.get("url", ""), "summary": summ})
    return rows


def stage(name, prompt_file, payload, tools="", schema=None):
    """One headless call per stage, prompt from a markdown file, input on stdin, own temp dir (see backend.ask)."""
    prompt = (HERE / "prompts" / prompt_file).read_text() + "\n\n" + payload
    schema = json.loads((HERE / "schemas" / schema).read_text()) if schema else None
    return ask(prompt, tools=tools, schema=schema)


def voice_pack():
    return "".join(f"\n\n## {n}\n\n{(HERE / 'voice' / n).read_text()}" for n in ["voice.md", "claims.md", "positions.md", "guardrails.md"])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true"); ap.add_argument("--list", action="store_true", help="show candidates and stop"); args = ap.parse_args()
    today = datetime.date.today()
    days = [today - datetime.timedelta(days=i) for i in range(LOOKBACK_DAYS)]
    used = set(memory.load(LEDGER))
    rows = [r for r in candidates(days) if r["id"] not in used]
    print(f"{len(rows)} candidates over {[d.isoformat() for d in days]} ({len(used)} already used)")
    if not rows:
        sys.exit("nothing to pick from")
    if args.list:
        for r in rows: print(f"  {r['id'][-12:]}  {r['title'][:70]}")
        return
    listing = "\n".join(f"{i+1}. id={r['id']}\n   title: {r['title']}\n   url: {r['url']}\n   summary: {r['summary']}" for i, r in enumerate(rows))
    pick = stage("pick", "pick.md", listing, tools="", schema="pick.json")
    chosen = next((r for r in rows if r["id"] == pick["id"]), None)
    if not chosen:
        sys.exit(f"REJECTED: pick returned an id not in the list: {pick['id']!r}")
    print(f"picked: {chosen['title']!r} — {pick['reason']}")
    research = stage("research", "research.md", json.dumps(chosen, indent=1), tools="WebSearch", schema="research.json")
    print(f"research: {len(research['facts'])} facts")
    script = stage("write", "write.md", json.dumps(research, indent=1) + voice_pack(), tools="", schema="script.json")
    slug = re.sub(r"[^a-z0-9]+", "-", script["title"].lower()).strip("-")[:50]
    draft = (f"---\ntitle: \"{script['title']}\"\nsource_id: {chosen['id']}\nsource_url: {chosen['url']}\ndate: {today}\nstatus: pending\n---\n"
             f"# {script['title']}\n\n{script['script'].strip()}\n\n## Facts used\n\n" +
             "\n".join(f"- {f['fact']} — {f['source']}" for f in research["facts"]) + "\n")
    if args.apply:
        out = QUEUE / f"{today}-{slug}.md"; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(draft)
        memory.append(LEDGER, chosen["id"])
        print(f"wrote {out.relative_to(ROOT)}; ledger +1")
    else:
        print("\n" + draft + "\n[DRY] nothing written; ledger unchanged")


if __name__ == "__main__":
    main()
