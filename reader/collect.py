#!/usr/bin/env python3
"""collect.py — the agent that reads. Fetches items, skips the ones in the ledger, files the rest.

    python3 collect.py                 # dry run: print what would be written, touch nothing
    python3 collect.py --apply         # write reading/YYYY/MM/YYYY-MM-DD-<slug>.md and the ledger
    python3 collect.py --feed URL      # read an RSS/Atom feed instead of inbox/*.txt

The ledger (ledger.txt) is a SET of ids already handled, one per line — not a "last seen" mark.
Subtracting it from today's candidates is what makes a run after a missed day self-healing.
"""
import argparse, datetime, html, pathlib, re, sys, urllib.request, xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent
LEDGER = HERE / "ledger.txt"
OUT = HERE / "reading"


def fetch_inbox():
    """Default source: one .txt per item in inbox/. Replace with your own source; keep the shape."""
    return [(p.stem, p.stem.replace("-", " "), "", p.read_text()) for p in sorted((HERE / "inbox").glob("*.txt"))]


def fetch_feed(url):
    """RSS or Atom, standard library only. Returns (id, title, link, text)."""
    with urllib.request.urlopen(url, timeout=30) as r:
        root = ET.fromstring(r.read())
    ns = {"a": "http://www.w3.org/2005/Atom"}
    items = []
    for it in root.iter("item"):                                   # RSS
        get = lambda tag: (it.findtext(tag) or "").strip()
        items.append((get("guid") or get("link"), get("title"), get("link"), strip_tags(get("description"))))
    for it in root.findall(".//a:entry", ns):                      # Atom
        link = it.find("a:link", ns)
        items.append(((it.findtext("a:id", "", ns) or "").strip(), (it.findtext("a:title", "", ns) or "").strip(),
                      link.get("href") if link is not None else "", strip_tags(it.findtext("a:summary", "", ns) or "")))
    return items


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", " ", s)).strip()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "item"


def load_ledger():
    return set(LEDGER.read_text().split()) if LEDGER.exists() else set()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write to disk; default is a dry run")
    ap.add_argument("--feed", help="RSS/Atom URL; default reads inbox/*.txt")
    args = ap.parse_args()
    today = datetime.date.today()
    done = load_ledger()
    items = fetch_feed(args.feed) if args.feed else fetch_inbox()
    new = [it for it in items if it[0] and it[0] not in done]
    mode = "APPLY" if args.apply else "DRY"
    for item_id, title, link, text in new:
        path = OUT / f"{today:%Y/%m}" / f"{today:%Y-%m-%d}-{slug(title)}.md"
        print(f"[{mode}] {title[:60]!r} -> {path.relative_to(HERE)}")
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"---\nid: {item_id}\ntitle: \"{title}\"\nurl: {link}\ndate: {today}\n---\n# {title}\n\n{text}\n")
            with LEDGER.open("a") as f:
                f.write(item_id + "\n")
    print(f"{len(items)} fetched, {len(items)-len(new)} already in ledger, {len(new)} {'written' if args.apply else 'would be written'}")


if __name__ == "__main__":
    main()
