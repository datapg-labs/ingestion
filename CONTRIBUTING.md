# Contributing

Everything lands through a pull request that Naush reviews. There is no path
that skips review, and that is deliberate — the point of this playground is to
practise the workflow a real data team uses, not just to run code.

## Work in your own directory

Each contributor gets one directory, named after your platform ID:

```
ingestion/
  pgXXXX/
    my-first-pipeline/
      README.md
      produce.py
```

Your platform ID is the `PGxxxx` you were given when your access was approved —
the same name as your Kafka user. Stay inside your own directory. A pull request
that edits someone else's work, or anything at the repo root, will be sent back.

This is not bureaucracy: it is what keeps twenty people working in one repo
without constant merge conflicts.

## Clone locally, with your own GitHub account

**Do not use the browser-based VS Code on the platform for git work.** It is a
shared workspace. Pushing from it would mean putting your GitHub credentials
somewhere other people can reach, and any commit you made would be attributed to
whoever set the workspace up.

Clone to your own machine, with your own identity:

```bash
git clone https://github.com/datapg-labs/ingestion.git
cd ingestion
```

Use the platform's VS Code and JupyterHub for *running* things against the
lakehouse and Kafka. Use your laptop for *git*. The two are separate on purpose.

## The flow

If you are not a member of the `datapg-labs` org, or the org is read-only for
you, **fork the repo first** and work in your fork. Otherwise work in a branch.

```bash
git checkout -b pgXXXX/my-first-pipeline
# ... make your changes, inside your own directory ...
git add ingestion/pgXXXX/
git commit -m "Add a worked example of consuming from a Kafka topic"
git push origin pgXXXX/my-first-pipeline
```

Then open a pull request. In the description, say what it does and what you
learned — that is the part reviewers actually respond to.

## What a review looks for

- Does it stay inside your own directory?
- Does it respect the platform limits below?
- Does the README explain what it does, so the next person can learn from it?
- No credentials, tokens, keys, or `.env` files. Not even fake-looking ones.

Reviews are meant to teach. Expect comments; they are not a rejection.

## Platform limits

These are enforced by the platform, not by politeness. Hitting them produces a
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

The Kafka cluster you have access to is a **teaching cluster**, separate from the
one running the platform's own pipelines. Twenty-four hour retention means it is
a place to learn, not a place to keep anything.

## CI

Workflows run on **GitHub-hosted runners**. Never add `runs-on: self-hosted` — a
pull request that does will be closed. Those runners belong to the platform's own
infrastructure and are not part of this playground.

## Getting your credentials

Your Kafka username and password are at
**[datapg.dev/credentials](https://datapg.dev/credentials)** once you are signed
in. They are yours; anyone you share them with is acting as you.
