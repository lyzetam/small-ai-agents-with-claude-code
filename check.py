#!/usr/bin/env python3
"""check.py — the weekly health check. Asks three questions of every agent and writes the answers where
the morning report will show them: state/check.json. Did any run write errors? Has a ledger stopped
growing? Is a dated output missing? Run it Sunday night; read it Monday morning."""
import datetime, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
today = datetime.date.today()
week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
problems = []

# 1. failures: any error log written to this week
for log in (ROOT / "logs").glob("*.err.log"):
    if log.stat().st_size and datetime.datetime.fromtimestamp(log.stat().st_mtime) > week_ago:
        last = log.read_text().strip().splitlines()[-1][:80]
        problems.append(f"{log.name}: {last}")

# 2. stale ledgers: nothing appended in seven days
for ledger in [ROOT / "reader" / "ledger.txt", ROOT / "state" / "used-topics.txt"]:
    if not ledger.exists():
        problems.append(f"{ledger.relative_to(ROOT)}: never written"); continue
    age = (datetime.datetime.now() - datetime.datetime.fromtimestamp(ledger.stat().st_mtime)).days
    if age > 7:
        problems.append(f"{ledger.relative_to(ROOT)}: last entry {age} days ago")

# 3. missing dated reports, weekdays only
for i in range(1, 8):
    d = today - datetime.timedelta(days=i)
    if d.weekday() < 5 and not (ROOT / "reports" / f"{d:%Y/%m/%Y-%m-%d}.md").exists():
        problems.append(f"report missing for {d}")

(ROOT / "state").mkdir(exist_ok=True)
(ROOT / "state" / "check.json").write_text(json.dumps(problems, indent=1))
print("\n".join(problems) if problems else "all clear")
