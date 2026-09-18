#!/usr/bin/env python3
"""Pull-request checks for datapg-labs/ingestion (GitHub-hosted runner, no secrets).

Quality checks, not the security boundary: the platform validates connectors again
before deploying them, and merged producers run in a sandbox. These exist so a
problem shows up on the pull request instead of after merge.

  producer-scripts/<project>/   README.md present, pipeline.py compiles, no
                                hard-coded credentials, PG_ID not hard-coded
  source-connectors/<project>/  README.md present, connector.json passes the same
                                rules the learner_connectors DAG applies
Every problem is printed as a GitHub annotation on the file it concerns.
"""

from __future__ import annotations

import json
import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT_NAME = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")

CLASS = "com.github.castorm.kafka.connect.http.HttpSourceConnector"
ALLOWED_HOSTS = re.compile(
    r"^(?:[a-z0-9-]+\.)*(?:binance\.com|binance\.vision)$"
    r"|^(?:query1|query2)\.finance\.yahoo\.com$")
DENIED_KEYS = re.compile(r"^http\.(auth|client\.proxy)")
MIN_INTERVAL_MS = 60_000

SECRET_PATTERNS = [
    (re.compile(r"""(?i)\b(pass(word|wd)?|secret|token|api[_-]?key|sasl_plain_password)\b\s*[:=]\s*["']([^"']{6,})["']"""),
     "a hard-coded password or secret"),
    (re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"), "an AWS access key"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "a private key"),
    (re.compile(r"\b(ghp|gho|ghs)_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{30,}"), "a GitHub token"),
]
PLACEHOLDER = re.compile(r"(\.\.\.|<[^>]*>|\$\{|os\.environ|getenv|x{4,}|your[_-]|change[_-]?me|example)", re.I)

problems = 0


def error(path: Path, message: str, line: int | None = None) -> None:
    global problems
    problems += 1
    rel = path.relative_to(ROOT).as_posix()
    loc = f",line={line}" if line else ""
    print(f"::error file={rel}{loc}::{message}")


def warn(path: Path, message: str) -> None:
    print(f"::warning file={path.relative_to(ROOT).as_posix()}::{message}")


def project_dirs(folder: str) -> list[Path]:
    base = ROOT / folder
    return sorted(d for d in base.iterdir() if d.is_dir()) if base.is_dir() else []


def scan_secrets(path: Path) -> None:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return
    for n, line in enumerate(lines, 1):
        for pattern, label in SECRET_PATTERNS:
            m = pattern.search(line)
            if m and not PLACEHOLDER.search(m.group(0)):
                error(path, f"looks like {label} - read credentials from the environment instead", n)


def check_producers() -> None:
    for d in project_dirs("producer-scripts"):
        if not PROJECT_NAME.match(d.name):
            error(d, "folder names are lowercase letters, digits, - and _")
            continue
        if not (d / "README.md").is_file():
            error(d, "add a README.md: what it does, where the data comes from, who built it")
        pipeline = d / "pipeline.py"
        if not pipeline.is_file():
            error(d, "a producer needs pipeline.py - that is the file the platform runs")
        else:
            try:
                py_compile.compile(str(pipeline), doraise=True)
            except py_compile.PyCompileError as e:
                error(pipeline, f"does not compile: {e.msg.strip().splitlines()[-1]}")
            text = pipeline.read_text(encoding="utf-8", errors="replace")
            if re.search(r"""^\s*PG_ID\s*=\s*["']pg\d{4}["']""", text, re.M):
                warn(pipeline, "PG_ID is hard-coded - use os.environ.get('PG_ID', ...) so it runs as 'pipelines' after merge")
        for f in d.rglob("*"):
            if f.is_file() and f.suffix in {".py", ".json", ".yml", ".yaml", ".txt", ".md", ".cfg", ".ini", ".env"}:
                if f.name == ".env" or f.suffix == ".env":
                    error(f, "never commit .env files")
                scan_secrets(f)


def validate_connector(project: str, raw: object) -> list[str]:
    """Same rules as the learner_connectors DAG (which stays authoritative)."""
    cfg = raw.get("config", raw) if isinstance(raw, dict) else None
    if not isinstance(cfg, dict):
        return ["connector.json must be a JSON object (optionally with a 'config' object)"]
    out, errs = {}, []
    if cfg.get("connector.class", CLASS) != CLASS:
        errs.append(f"only {CLASS} is available")
    for key, value in cfg.items():
        if key in ("connector.class", "name", "tasks.max"):
            continue
        value = str(value)
        if "${" in value:
            errs.append(f"'{key}' uses a config provider (${{...}}), which is not allowed")
        if key == "kafka.topic" or (key.startswith("http.") and not DENIED_KEYS.match(key)):
            out[key] = value
        else:
            errs.append(f"'{key}' is not allowed (only http.* settings and kafka.topic; no auth or proxy)")
    url = out.get("http.request.url", "")
    m = re.match(r"^https://([^/:?#]+)(?:[/?#]|$)", url)
    if not m or not ALLOWED_HOSTS.match(m.group(1).lower()):
        errs.append("http.request.url must be https:// on api.binance.com, data-api.binance.vision "
                    "or query1/query2.finance.yahoo.com")
    topic, want = out.get("kafka.topic", ""), f"pipelines.{project}."
    if not topic.startswith(want) or topic == want:
        errs.append(f"kafka.topic must start with '{want}'")
    for key in ("http.timer.interval.millis", "http.timer.catchup.interval.millis"):
        if key in out:
            try:
                if int(out[key]) < MIN_INTERVAL_MS:
                    errs.append(f"'{key}' is below {MIN_INTERVAL_MS} ms - it will be raised to one minute")
            except ValueError:
                errs.append(f"'{key}' must be a number of milliseconds")
    return errs


def check_connectors() -> None:
    for d in project_dirs("source-connectors"):
        if not PROJECT_NAME.match(d.name):
            error(d, "folder names are lowercase letters, digits, - and _")
            continue
        if not (d / "README.md").is_file():
            error(d, "add a README.md: what it pulls, how often, into which topic, and why")
        f = d / "connector.json"
        if not f.is_file():
            error(d, "a connector project needs connector.json")
            continue
        try:
            raw = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            error(f, f"not valid JSON: {e.msg}", e.lineno)
            continue
        for msg in validate_connector(d.name, raw):
            error(f, msg)
        scan_secrets(f)


def main() -> int:
    check_producers()
    check_connectors()
    print(f"\n{problems} problem(s) found" if problems else "\nAll checks passed")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
