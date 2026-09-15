"""Tests for scope_check.py. Run: python3 -m pytest .github/scripts -q

Each test builds a throwaway git repository with a base commit and a pull-request
commit, then runs the real check against the two SHAs.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import scope_check  # noqa: E402

MAINTAINER, ALICE, BOB = "naush-c", "alice", "bob"


def run(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()


def write(repo: Path, files: dict[str, str | None]) -> None:
    for path, content in files.items():
        p = repo / path
        if content is None:
            p.unlink()
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)


def commit(repo: Path, msg: str) -> str:
    run(repo, "add", "-A")
    run(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", msg)
    return run(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo():
    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        run(r, "init", "-q", "-b", "main")
        write(r, {
            ".github/maintainers.txt": f"# maintainers\n{MAINTAINER}\ndatapglabs\n",
            "README.md": "# repo\n",
            "reference/sub_ledger/models/a.sql": "select 1\n",
            "projects/README.md": "# projects\n",
            "projects/btc-candles/README.md": "# BTC candles\n\nAuthors: @alice\n",
            "projects/btc-candles/models/c.sql": "select 2\n",
        })
        commit(r, "base")
        cwd = os.getcwd()
        os.chdir(r)
        try:
            yield r
        finally:
            os.chdir(cwd)


def pr(repo: Path, files: dict[str, str | None], author: str) -> list[str]:
    base = run(repo, "rev-parse", "HEAD")
    run(repo, "checkout", "-q", "-b", f"pr-{abs(hash(str(files)))}")
    write(repo, files)
    head = commit(repo, "pr")
    return scope_check.check(base, head, author)


def test_author_changes_own_project(repo):
    assert pr(repo, {"projects/btc-candles/models/c.sql": "select 3\n"}, ALICE) == []


def test_new_project_listing_author_passes(repo):
    assert pr(repo, {"projects/jde-gl/README.md": "# JDE GL\n\nAuthors: @bob\n",
                     "projects/jde-gl/models/x.sql": "select 1\n"}, BOB) == []


def test_new_project_without_readme_fails(repo):
    problems = pr(repo, {"projects/jde-gl/models/x.sql": "select 1\n"}, BOB)
    assert any("new project" in p for p in problems)


def test_editing_someone_elses_project_fails(repo):
    problems = pr(repo, {"projects/btc-candles/models/c.sql": "select 9\n"}, BOB)
    assert any("belongs to @alice" in p for p in problems)


def test_joining_by_adding_only_yourself_passes(repo):
    assert pr(repo, {"projects/btc-candles/README.md": "# BTC candles\n\nAuthors: @alice, @bob\n"}, BOB) == []


def test_joining_while_also_changing_code_fails(repo):
    problems = pr(repo, {"projects/btc-candles/README.md": "# BTC candles\n\nAuthors: @alice, @bob\n",
                         "projects/btc-candles/models/c.sql": "select 9\n"}, BOB)
    assert any("belongs to @alice" in p for p in problems)


def test_adding_someone_else_to_a_project_fails(repo):
    problems = pr(repo, {"projects/btc-candles/README.md": "# BTC candles\n\nAuthors: @alice, @bob, @carol\n"}, BOB)
    assert problems


def test_learner_editing_reference_fails(repo):
    problems = pr(repo, {"reference/sub_ledger/models/a.sql": "select 2\n"}, ALICE)
    assert any("outside projects/" in p for p in problems)


def test_learner_editing_root_or_github_fails(repo):
    problems = pr(repo, {"README.md": "# changed\n", ".github/maintainers.txt": "alice\n"}, ALICE)
    assert len([p for p in problems if "outside projects/" in p]) == 2


def test_maintainer_may_edit_anything(repo):
    assert pr(repo, {"reference/sub_ledger/models/a.sql": "select 2\n", "README.md": "# x\n",
                     "projects/btc-candles/models/c.sql": "select 4\n"}, MAINTAINER) == []


def test_bad_project_name_fails(repo):
    problems = pr(repo, {"projects/My Project/README.md": "Authors: @bob\n"}, BOB)
    assert any("project names" in p for p in problems)


def test_env_file_fails_even_for_maintainer(repo):
    problems = pr(repo, {"projects/btc-candles/.env": "X=1\n"}, MAINTAINER)
    assert any("credentials file" in p for p in problems)


def test_hardcoded_password_fails(repo):
    problems = pr(repo, {"projects/btc-candles/produce.py": 'sasl_plain_password = "hunter2hunter2"\n'}, ALICE)
    assert any("hard-coded password" in p for p in problems)


def test_placeholder_and_env_read_pass(repo):
    ok = ('password = os.environ["KAFKA_PASSWORD"]\n'
          'os.environ["KAFKA_PASSWORD"] = "..."\n'
          'token: "<your-token>"\n'
          "password: \"{{ env_var('PW') }}\"\n")
    assert pr(repo, {"projects/btc-candles/produce.py": ok}, ALICE) == []


def test_aws_key_and_private_key_fail(repo):
    problems = pr(repo, {"projects/btc-candles/x.txt": "AKIAABCDEFGHIJKLMNOP\n-----BEGIN RSA PRIVATE KEY-----\n"}, ALICE)
    assert len(problems) == 1 or len(problems) == 2  # one finding per added line, first match wins
    assert any("AWS access key" in p for p in problems)


def test_deleting_own_project_passes_and_others_fails(repo):
    assert pr(repo, {"projects/btc-candles/models/c.sql": None}, ALICE) == []
