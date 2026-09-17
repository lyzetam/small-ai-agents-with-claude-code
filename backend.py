"""backend.py — one function that runs a prompt through Claude, and one switch that says how.

AGENT_BACKEND=cli|api|auto   (default auto: "cli" if the claude binary exists, else "api")

Every call runs in a fresh temporary directory with --setting-sources "" and a one-line
system prompt, so nothing on the machine (other CLAUDE.md files, memory, rules) leaks in.
Report-writing calls pass tools="" — the model can only answer, never write a file.
"""
import json, os, shutil, subprocess, tempfile

CLAUDE = os.environ.get("CLAUDE_BIN") or shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")


def backend() -> str:
    mode = os.environ.get("AGENT_BACKEND", "auto")
    if mode == "auto":
        return "cli" if os.path.exists(CLAUDE) else "api"
    return mode


def ask(prompt: str, system: str = "You are one stage of a script. Do only what the prompt says.",
        tools: str = "", schema: dict | None = None, timeout: int = 300):
    """Return the model's text, or the parsed structured_output when a schema is given."""
    if backend() != "cli":
        raise RuntimeError("api backend is not configured on this machine "
                           "(set AGENT_BACKEND=cli, or add an API client before running here)")
    cmd = [CLAUDE, "-p", "--setting-sources", "", "--system-prompt", system,
           "--allowedTools", tools, "--output-format", "json"]
    if tools:
        cmd += ["--tools", tools]
    if schema:
        cmd += ["--json-schema", json.dumps(schema)]
    with tempfile.TemporaryDirectory(prefix="agent-") as tmp:
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, cwd=tmp)
    if r.returncode != 0:
        raise RuntimeError(f"claude failed ({r.returncode}): {r.stderr.strip()[:300]}")
    data = json.loads(r.stdout)
    return data["structured_output"] if schema else data["result"]
