#!/usr/bin/env python3
"""catchup.py — run on login/wake (launchd RunAtLoad, or a cron @reboot). For each agent, if today's
output does not exist, run it now. Otherwise do nothing. The 06:00 job only fires if the machine is awake;
this is what covers the mornings it wasn't."""
import datetime, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent
today = datetime.date.today()
JOBS = {
    "writer": (ROOT / "reports" / f"{today:%Y/%m/%Y-%m-%d}.md", ["writer/writer.py", "--apply"]),
}
for name, (expected, cmd) in JOBS.items():
    if expected.exists():
        print(f"{name}: ok ({expected.relative_to(ROOT)})")
        continue
    print(f"{name}: missing {expected.relative_to(ROOT)} — running")
    r = subprocess.run([sys.executable, *cmd], cwd=ROOT)
    print(f"{name}: exit {r.returncode}")
