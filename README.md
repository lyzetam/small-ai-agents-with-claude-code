# Small AI Agents With Claude Code — the kit

The scripts, prompt files, schemas, voice files and schedule from the book **_Small AI Agents With Claude Code: Scheduled, Headless Agents That Read, Write and Decide While You Sleep_** by Landry Zetam (Kindle, 2026). Standard-library Python, `claude -p`, and the scheduler your OS already has. No framework.

Every file was run in a clean folder on the day the book was finished — 20 tests, in [TESTS.md](TESTS.md). Real outputs from that run are in [`examples/`](examples/).

**Book:** Amazon link coming as soon as the listing is live. Book one, about the vault these agents live in: [obsidian-claude-code-setup](https://github.com/lyzetam/obsidian-claude-code-setup).

## The three agents

| Agent | Files | What it does | Guardrails it carries |
|---|---|---|---|
| **Reads** | `reader/collect.py`, `reader/enrich.py` | Fetches items (`inbox/*.txt` or any RSS/Atom feed), files them as dated notes, then adds a summary to each once | dry by default; `ledger.txt` is a **set**, not a watermark; enrich is idempotent by marker; no tools |
| **Writes** | `writer/writer.py`, `writer/prompts/` | One headless call turns the day's sources into a report | **no tools**; rejects a "Saved to…" stub; writes the parts it has and names the missing ones; surfaces `check.py`'s problems on line one; never overwrites |
| **Decides** | `decider/decide.py`, `decider/prompts/`, `decider/schemas/`, `decider/voice/` | Candidates minus the used ledger → pick (schema) → research (web search, own clean room) → write in a voice defined by files → a **draft** in `queue/pending/` | rejects a pick outside the list; the rules are files; it never publishes |

Around them: `backend.py` (one `ask()`, every call in a fresh temp dir with `--setting-sources ""`; `AGENT_BACKEND=cli|api|auto` — api mode refuses to spend on a machine without a client), `memory.py` (append-only), `approve.py` (the human's side of the line: `pending | approve | reject` — there is no send code in this repo), `check.py` (Sunday: errors this week, stale ledgers, missing reports → `state/check.json`), `catchup.py` (run on wake: anything missing today gets run), `launchd/` and `crontab.txt`.

## Quick start

Requirements: macOS or Linux, Python 3.10+, [Claude Code](https://code.claude.com/docs/en/setup) signed in (Pro/Max/Team).

```bash
git clone https://github.com/lyzetam/small-ai-agents-with-claude-code.git ~/agents && cd ~/agents
python3 -m unittest -v                       # 7 offline tests, zero tokens

echo "Plumber booked Thursday 9am." > reader/inbox/plumber.txt
python3 reader/collect.py                    # dry: shows what it would file
python3 reader/collect.py --apply            # files it; ledger.txt grows by one
python3 reader/enrich.py --apply             # one headless call per note, no tools

python3 writer/writer.py                     # dry: prints today's report
python3 writer/writer.py --apply             # writes reports/YYYY/MM/YYYY-MM-DD.md

python3 reader/collect.py --feed https://hnrss.org/frontpage --apply   # real candidates
python3 decider/decide.py                    # dry: pick → research → write, nothing written
python3 decider/decide.py --apply            # a draft lands in queue/pending/
python3 approve.py pending                   # you read it; approve or reject

python3 check.py                             # what needs you this week
```

Schedule: edit the `/Users/me` paths in `launchd/local.agents.writer.plist`, `plutil -lint` it, then `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/local.agents.writer.plist`. Linux: `crontab.txt`.

## The rules the kit enforces

1. **Dry by default.** Nothing is written without `--apply`.
2. **A ledger is a set.** Subtract what was done; a missed day heals itself.
3. **Report-writing runs get no tools**, and an answer that reads like a confirmation is rejected, not saved.
4. **Write the parts you have; name the part you don't.** A missing source is a line in the report, not a crash and not an invented number.
5. **Each stage in its own clean room.** No `CLAUDE.md`, no settings, no memory leaks into an agent.
6. **The line it may not cross is a file.** Voice, claims, positions, guardrails — readable, editable, versioned.
7. **Budget is a switch.** `cli` on a subscription, `api` on a server, and never by accident.
8. **You draft; the human sends.** Drafts go to a queue. Nothing here can send.

## License

MIT. If the book helped, an honest review on Amazon helps the next reader find it.
