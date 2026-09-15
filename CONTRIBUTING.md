# Contributing

This repository is a shared codebase, worked on the way a data team works on one:
projects live side by side, every change goes through a pull request, and teammates
review each other's work before it merges.

## How the repository is organised

```
reference/          maintained examples — read them, don't edit them
  _template/        the starting point: create a topic, produce, consume
projects/           learner projects, one directory each
  btc-price-alerts/
    README.md       Authors: @alice, @bob
    pipeline.py
```

- **`reference/`** is kept in shape for everyone. Only maintainers change it.
- **`projects/<name>/`** belongs to the people on its `Authors:` line. Name a project
  after what it does (`btc-price-alerts`), not after a person.

## Start a project

```bash
git clone https://github.com/datapg-labs/ingestion.git
cd ingestion
git checkout -b btc-price-alerts
cp -r reference/_template projects/btc-price-alerts
```

1. Put your GitHub handle on the `Authors:` line of `projects/btc-price-alerts/README.md`:
   `Authors: @your-github-user`
2. Build it and run it in JupyterHub (see *Where your code runs*), then copy it back
   into your clone.
3. Commit, push your branch, and open a pull request.

If you have not accepted your `datapg-labs` invitation yet, fork the repository and
open the pull request from your fork — everything else is the same.

## Work on someone else's project

Projects are meant to be shared. To join one, open a pull request whose **only**
change adds your handle to that project's `Authors:` line. One of its authors reviews
it; once it merges you work on the project like any other author.

To suggest a change without joining, open an issue or comment on a pull request.

## Reviews

A pull request merges when it has:

1. **A peer review.** Ask a teammate — an author of the project, or anyone who knows
   the area. Reviewing is half of what this repository teaches: read the code, run it
   if you can, ask questions, suggest changes.
2. **A maintainer's approval.** Maintainers merge; you don't need to chase them.
3. **A passing scope check** (next section).

What a good review looks for:

- Does it do what its README says, and would the README make sense to the next person?
- Does it respect the platform limits below?
- Is it easy to follow — clear names, no dead code, no notebook output committed?
- No credentials, tokens, keys, or `.env` files. Not even fake-looking ones.

Expect comments on your pull requests; they are meant to teach, not to reject.

## The scope check

An automated check runs on every pull request. It fails, and says exactly which file
and why, when a pull request:

- changes anything outside `projects/` — `reference/`, the docs, `.github/` — unless
  you are a maintainer
- changes a project you are not an author of (joining, as above, is the exception)
- adds a project without a `README.md` that lists you on its `Authors:` line
- adds a credentials file (`.env`, `*.pem`, a private key) or a line that looks like a
  hard-coded password, token or key

## Clone locally, with your own GitHub account

**Do not use the browser-based VS Code on the platform for git work.** It is a
shared workspace. Pushing from it would mean putting your GitHub credentials
somewhere other people can reach, and any commit you made would be attributed to
whoever set the workspace up. Clone to your own machine, with your own identity.

## Where your code runs

The platform's services — Kafka, Trino, the lakehouse — are only reachable from
inside the platform. Write and run your code in **JupyterHub** (or a platform VS
Code workspace if you have one), then copy it into your local clone to commit.
Your laptop and GitHub Actions cannot reach those services.

## Platform limits

These are enforced by the platform on your platform account. Hitting them produces a
real error, so it is worth knowing them before you are confused by one.

| Limit | Value |
|---|---|
| Kafka topics you may create | Must start with `<your-pg-id>.` — e.g. `pgXXXX.orders` |
| Kafka consumer groups | Same prefix rule |
| Produce rate | 1 MB/s |
| Consume rate | 2 MB/s |
| Kafka retention | 24 hours, 1 GB per partition |
| Topic auto-creation | **Off.** Create topics explicitly |

Anything outside your prefix fails with `TopicAuthorizationFailedError`, and a
topic you have no rights to is reported as "does not exist" rather than
"forbidden" — so if a topic seems mysteriously missing, check the prefix first.

On a shared project, each author runs it under their own platform ID — keep `PG_ID`
and topic names configurable rather than hard-coding one person's prefix.

The Kafka cluster you have access to is a **teaching cluster**, separate from the
one running the platform's own pipelines. Twenty-four hour retention means it is
a place to learn, not a place to keep anything.

## CI

Workflows run on **GitHub-hosted runners** only, and live in `.github/`, which
maintainers look after. Never add `runs-on: self-hosted` — a pull request that does
will be closed.

## Getting your credentials

Your Kafka username and password are at
**[datapg.dev/credentials](https://datapg.dev/credentials)** once you are signed
in. They are yours; anyone you share them with is acting as you. Never commit them —
read them from the environment instead.
