# Contributing

Everything reaches `main` through a pull request, and every pull request is reviewed
before it merges. That is the workflow a real data team uses, and practising it is part
of the point.

## Join the Discord

**[datapg.dev/discord](https://datapg.dev/discord)** is where the community lives. Ask
there when you are stuck, find people to build a project with, and post your pull request
when it is ready for review. Never paste credentials into Discord — they are as personal
there as in a commit.

## Where things go

```
producer-scripts/            Python producers — one folder per project
  example-kafka-producer/    the worked example: create a topic, produce, consume
source-connectors/           Kafka Connect source configs (JSON) — one folder per project
```

Each project gets its own folder with a short `README.md`: what it does, where the data
comes from, and who built it. Name the folder after what it does (`btc-price-alerts`),
not after a person.

## Recommended: a data contract for every ingestion

Anything you ingest becomes a dataset someone else will read. Describe it in
[`data-contracts`](https://github.com/datapg-labs/data-contracts) — one contract per topic
— and link the contract from your project's README. A pull request that adds an ingestion
without one will usually get a review comment asking for it.

## The flow

Nobody pushes to `datapg-labs` directly — every change arrives from a **fork**.

1. Fork the repository on GitHub (the **Fork** button, top right), then clone your fork:

   ```bash
   git clone https://github.com/<your-github-user>/ingestion.git
   cd ingestion
   git remote add upstream https://github.com/datapg-labs/ingestion.git
   git checkout -b btc-price-alerts
   cp -r producer-scripts/example-kafka-producer producer-scripts/btc-price-alerts
   ```

2. Edit the README and the code. Run it in JupyterHub (see *Where your code runs*), then
   copy it back into your clone.
3. Commit, push the branch to your fork (`git push -u origin btc-price-alerts`), and open a
   pull request into `datapg-labs/ingestion` — GitHub offers the button as soon as you
   push. In the description, say what it does and what you learned — that is the part
   reviewers respond to.

Before you start something new, bring your fork up to date — **Sync fork** on GitHub, or:

```bash
git fetch upstream
git switch main
git merge --ff-only upstream/main
```

Want to improve someone else's project or the example? Open a pull request for that too
and say why — the original author is welcome to review it.

## Working as a team

Building with someone? One of you forks, and adds the others as collaborators on the fork
(**Settings → Collaborators**). You all push to the same branch, and the pull request
shows everyone's commits. Name every author in the project README. Discord is the place to
find a team.

## Reviews and merging

A pull request merges once a member of the **reviewers** team approves it — someone other
than the author. Anyone can comment on and learn from any pull request; ask for a review
when yours is ready.

Automated checks run on every pull request. On your first one they wait until a
maintainer approves the run — GitHub does that for every new contributor.

## What happens after merge

Merged producers run **once an hour** on the platform, in a locked-down sandbox: as Kafka
user `pipelines`, with only Binance and Yahoo Finance reachable, a 5-minute limit and logs
visible in Airflow. See
[`producer-scripts/README.md`](producer-scripts/README.md#what-happens-after-merge) for
what that means for your code.

Merged source connectors are **deployed** to the learners' Kafka Connect worker within 15
minutes and run continuously — see
[`source-connectors/README.md`](source-connectors/README.md#the-rules-a-config-must-follow)
for the rules a config must follow.

## What a review looks for

- Does it stay inside its own project folder?
- Does the README explain it to the next person, and link a data contract?
- Will it run in the sandbox — `PG_ID` from the environment, project name in the topic,
  exits in time, only Binance or Yahoo Finance as sources?
- For a connector: does it follow the rules, and does the README explain the interval and
  offset choices?
- Does it respect the platform limits below?
- No credentials, tokens, keys, or `.env` files. Not even fake-looking ones.

Expect comments; they are meant to teach, not to reject.

## Clone locally, with your own GitHub account

**Do not use the browser-based VS Code on the platform for git work.** It is a shared
workspace. Pushing from it would mean putting your GitHub credentials somewhere other
people can reach, and any commit you made would be attributed to whoever set the
workspace up. Clone your fork to your own machine, with your own identity.

## Where your code runs

The platform's services — Kafka, Trino, the lakehouse — are only reachable from inside
the platform. Write and run your code in **JupyterHub** (or a platform VS Code workspace
if you have one), then copy it into your local clone to commit. Your laptop and GitHub
Actions cannot reach those services.

## Platform limits

These are enforced by the platform. Hitting them produces a real error, so it is worth
knowing them before you are confused by one.

| Limit | Value |
|---|---|
| Kafka topics you may create | Must start with `<your-pg-id>.` — e.g. `pgXXXX.orders` (`pipelines.` after merge) |
| Kafka consumer groups | Same prefix rule |
| Produce rate | 1 MB/s |
| Consume rate | 2 MB/s |
| Kafka retention | 24 hours, 1 GB per partition |
| Topic auto-creation | **Off.** Create topics explicitly |

Anything outside your prefix fails with `TopicAuthorizationFailedError`, and a topic you
have no rights to is reported as "does not exist" rather than "forbidden" — so if a topic
seems mysteriously missing, check the prefix first.

The Kafka cluster you have access to is a **teaching cluster**, separate from the one
running the platform's own pipelines. Twenty-four hour retention means it is a place to
learn, not a place to keep anything.

## CI

Workflows run on **GitHub-hosted runners** only. Never add `runs-on: self-hosted` — a
pull request that does will be closed.

## Getting your credentials

Your Kafka username and password are at
**[datapg.dev/credentials](https://datapg.dev/credentials)** once you are signed in. They
are yours; anyone you share them with is acting as you. Never commit them — read them
from the environment instead.
