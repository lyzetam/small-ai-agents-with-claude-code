# Tests run 2026-09-16 — every file in `tested/agents/` was executed in a throwaway folder

The kit: standard-library Python + `claude -p` (Max plan, no API key) + launchd/cron. Layout in `tested/agents/`.

| # | What | How | Result |
|---|---|---|---|
| T1 | `reader/collect.py` dry run | two `.txt` items in `inbox/` | printed `[DRY] … -> reading/2026/09/2026-09-16-<slug>.md` for both; wrote nothing |
| T2 | `collect.py --apply` | same | wrote two notes with frontmatter (`id/title/url/date`) and appended both ids to `ledger.txt` |
| T3 | run `--apply` again | same | "2 fetched, 2 already in ledger, 0 written" — the ledger is a set |
| T4 | `collect.py --feed <RSS url>` (dry) | a real public RSS feed, standard-library XML parsing | 20 items listed, none written; later applied to give the decider real candidates |
| T5–T7 | `reader/enrich.py` | dry → apply (one headless call per note, no tools) → apply again | dry listed 2; apply appended a one-sentence summary + three bullets + `<!-- enriched -->` to each; second apply: "2 already enriched, 0 enriched" |
| T8 | `writer/writer.py` dry | a day's terminal log + the day's two reading notes, one `claude -p` with `--allowedTools ""` and a JSON schema | a real report with the three sections; it noted the full test suite was never re-run and the sweep was dry-run only |
| T9 | `writer.py --apply` twice | | first wrote `reports/2026/09/2026-09-16.md`; second exited "exists … delete it to rebuild" |
| T10 | `writer.py --date 2026-09-10 --apply` (a day with no sources) | | wrote the file with `_No analysis was generated this run: no sources found._`, `sources: none`, `missing: terminal log, reading notes`, a `built:` stamp; exit 0 |
| T11 | `looks_like_report` | four inputs | rejected "I have saved the report…" (no heading), "# Done / Saved." (confirmation), a 31-char report (too short); accepted a real one |
| T12 | `decider/decide.py` dry | 22 candidates from the feed; three stages: pick (schema) → research (`--allowedTools WebSearch`, own temp dir) → write (schema, voice files appended) | picked one story with a reason; research returned 6 facts each with a source URL; the script obeyed `claims.md` (used only the allowed first-person line); nothing written, ledger unchanged |
| T13 | `decide.py --apply` | | wrote `queue/pending/2026-09-16-<slug>.md` and appended the source id to `state/used-topics.txt` |
| T14 | `decide.py --list` after T13 | | "21 candidates … (1 already used)" — the used story is excluded |
| T15 | `approve.py` | `pending`, `approve <file>`, `reject nope.md` | listed the draft by title; moved it to `queue/approved/`; unknown name exits 1 |
| T16 | `launchd/local.agents.writer.plist` | `plutil -lint` | OK |
| T17 | `catchup.py` | today's report exists | "writer: ok" — no-op |
| T18 | `check.py` | planted: a `RuntimeError` line in `logs/decider.err.log`, `used-topics.txt` touched 15 days old | reported both, plus four missing weekday reports; skipped the weekend and the day that had its honest stub; wrote `state/check.json` |
| T19 | `python3 -m unittest -v` (offline, `backend.ask` patched) | 7 tests | all pass in 0.06 s, zero tokens, no network |
| T20 | the budget switch, end to end | `AGENT_BACKEND=api python3 writer/writer.py --apply` on a machine with no API client | the call refused to spend ("api backend is not configured"), the report was still written with `_No analysis was generated this run: the model call failed._`, and the six `check.json` problems appeared as its first line |

Live model calls made during testing: enrich ×2, writer ×1, decider ×3 (one with web search) = 6 headless calls on the Max plan.
