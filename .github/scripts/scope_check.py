#!/usr/bin/env python3
"""Scope check for pull requests into a shared datapg-labs repository.

This runs under `pull_request_target`, from the BASE branch. It reads what the pull
request changes as data (git diff / git show) and never executes anything that came
from the pull request - otherwise a pull request could simply edit this file to pass.

Rules
  1. Outside projects/<name>/ only maintainers may change anything: reference/,
     README.md, CONTRIBUTING.md, .github/ and every other root file.
  2. Inside projects/<name>/ you must be listed on the project's `Authors:` line in
     its README.md on the base branch.
       - A NEW project must add projects/<name>/README.md listing you.
       - JOINING a project is a pull request whose only change in that project adds
         your handle to the Authors line. An existing author reviews it.
  3. No credentials, from anyone: credential-looking files and added lines fail.

Inputs (environment): BASE_SHA, HEAD_SHA, PR_AUTHOR. Exit 1 on any violation.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

PROJECT_NAME = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")
AUTHORS_LINE = re.compile(r"^\s*[*_]*authors?[*_]*\s*:\s*(.*)$", re.IGNORECASE | re.MULTILINE)
HANDLE = re.compile(r"@?([A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38})")

CREDENTIAL_FILES = re.compile(
    r"(^|/)(\.env(\..+)?|[^/]+\.(pem|key|p12|pfx|jks|keystore)|id_(rsa|dsa|ecdsa|ed25519)|credentials\.json)$",
    re.IGNORECASE,
)
CREDENTIAL_LINES = [
    ("an AWS access key id", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("a private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("a GitHub token", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{30,}")),
    ("a Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    (
        "a hard-coded password or secret",
        re.compile(
            r"""(?ix)\b(pass(word|wd)?|secret|token|api[_-]?key|access[_-]?key|secret[_-]?key|
                sasl_plain_password|client[_-]?secret)\b
                \s*[:=]\s*["']([^"']{6,})["']"""
        ),
    ),
    (
        "a hard-coded password or secret",
        re.compile(r"(?i)^\s*(password|passwd|secret|token|api_key|client_secret)\s*:\s*([^\s#'\"]{6,})\s*$"),
    ),
]
# Values that are clearly not a real secret.
PLACEHOLDER = re.compile(r"(\.\.\.|<[^>]*>|\$\{|\{\{|%\(|os\.environ|getenv|env_var|x{4,}|\*{4,}|your[_-]|change[_-]?me|example|placeholder|redacted)", re.IGNORECASE)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def show(sha: str, path: str) -> str | None:
    r = subprocess.run(["git", "show", f"{sha}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def authors(readme: str | None) -> set[str]:
    if not readme:
        return set()
    found: set[str] = set()
    for line in AUTHORS_LINE.findall(readme):
        found.update(h.lower() for h in HANDLE.findall(line))
    return found


def maintainers(base: str) -> set[str]:
    text = show(base, ".github/maintainers.txt") or ""
    return {l.strip().lstrip("@").lower() for l in text.splitlines() if l.strip() and not l.startswith("#")}


def added_lines(base: str, head: str) -> list[tuple[str, str]]:
    out, current = [], None
    for line in git("diff", "--no-renames", "-U0", f"{base}...{head}").splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("+") and not line.startswith("+++") and current:
            out.append((current, line[1:]))
    return out


def check(base: str, head: str, author: str) -> list[str]:
    author = author.lower()
    is_maintainer = author in maintainers(base)
    changed = [p for p in git("diff", "--no-renames", "--name-only", f"{base}...{head}").splitlines() if p]
    problems: list[str] = []

    by_project: dict[str, list[str]] = {}
    for path in changed:
        parts = path.split("/")
        if parts[0] == "projects" and len(parts) >= 3:
            by_project.setdefault(parts[1], []).append("/".join(parts[2:]))
        elif not is_maintainer:
            problems.append(f"`{path}` is outside projects/<name>/ - only maintainers change that.")

    if not is_maintainer:
        for name, files in sorted(by_project.items()):
            where = f"projects/{name}/"
            if not PROJECT_NAME.match(name):
                problems.append(f"`{where}`: project names are lowercase letters, digits, - and _ (2-64 chars).")
                continue
            base_readme = show(base, f"{where}README.md")
            head_readme = show(head, f"{where}README.md")
            base_authors, head_authors = authors(base_readme), authors(head_readme)

            if base_readme is None:  # a new project
                if author not in head_authors:
                    problems.append(f"`{where}` is a new project: add `{where}README.md` with `Authors: @{author}`.")
            elif author in base_authors:
                if head_readme is not None and not head_authors:
                    problems.append(f"`{where}README.md` must keep an `Authors:` line.")
            elif files == ["README.md"] and head_authors == base_authors | {author}:
                pass  # joining: only adds themselves; an existing author reviews it
            else:
                listed = ", ".join(f"@{a}" for a in sorted(base_authors)) or "nobody"
                problems.append(
                    f"`{where}` belongs to {listed}. To join, open a pull request that only adds "
                    f"`@{author}` to its Authors line."
                )

    for path in changed:
        if CREDENTIAL_FILES.search(path) and show(head, path) is not None:
            problems.append(f"`{path}` looks like a credentials file - never commit those.")
    for path, line in added_lines(base, head):
        for label, pattern in CREDENTIAL_LINES:
            m = pattern.search(line)
            if m and not PLACEHOLDER.search(m.group(0)):
                problems.append(f"`{path}` adds what looks like {label}. Read it from the environment instead.")
                break
    return problems


def main() -> int:
    base, head, author = os.environ["BASE_SHA"], os.environ["HEAD_SHA"], os.environ["PR_AUTHOR"]
    problems = check(base, head, author)
    report = (
        "### Scope check passed\n" if not problems
        else "### Scope check failed\n\n" + "\n".join(f"- {p}" for p in problems)
        + "\n\nSee CONTRIBUTING.md for how projects, authors and reviews work.\n"
    )
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write(report)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
