# Contributing

## Your work lives in your own repository

This repository is a **template**. It holds the starting point and the worked
examples, and it is kept in shape for everyone. Your own pipelines are not merged
into it — they live in a repository you own:

1. Open [datapg-labs/ingestion](https://github.com/datapg-labs/ingestion) and click
   **Use this template → Create a new repository**.
2. Choose **your own GitHub account** as the owner. Public or private is up to you.
3. Clone your new repository to your own machine (next section).

From then on it is yours: commit and push whenever you like, organise it however
you like, and it shows on your GitHub profile. Nobody has to approve anything
before you can keep going.

Why not one shared repository with a directory per person? Every change would wait
on one reviewer, anyone with access could edit anyone else's folder, and your work
would live in someone else's organisation instead of on your profile.

## Clone locally, with your own GitHub account

**Do not use the browser-based VS Code on the platform for git work.** It is a
shared workspace. Pushing from it would mean putting your GitHub credentials
somewhere other people can reach, and any commit you made would be attributed to
whoever set the workspace up.

Clone to your own machine, with your own identity:

```bash
git clone https://github.com/<your-github-user>/<your-repo>.git
cd <your-repo>
```

## Where your code runs

The platform's services — Kafka, Trino, the lakehouse — are only reachable from
inside the platform. Write and run your code in **JupyterHub** (or a platform VS
Code workspace if you have one), then copy it into your local clone to commit.
Your laptop and GitHub Actions cannot reach those services. The two halves are
separate on purpose.

## Improving this template

Pull requests to this repository are welcome when they improve the shared material
for everyone: a mistake in the docs, a template that no longer runs, a clearer
worked example. They are not the place for your own projects.

1. Fork `datapg-labs/ingestion` and create a branch in your fork
2. Make one focused change
3. Open a pull request that says what was wrong and how you checked the fix

Every pull request here is reviewed before it merges. Expect comments; they are
meant to teach, not to reject. A review looks for:

- A change that helps the next learner, not just you
- Nothing personal: no platform IDs, no notebooks full of your own output
- No credentials, tokens, keys, or `.env` files. Not even fake-looking ones.

## Show what you built

Built something worth seeing? Open an issue in this repository titled
`Showcase: <what you built>`, link your repository, and say what you learned. The
best ones get linked from the README, so the next person can learn from them.

## Platform limits

These are enforced by the platform on your platform account, wherever your code
lives. Hitting them produces a real error, so it is worth knowing them before you
are confused by one.

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

In your own repository, use **GitHub-hosted runners**. They cannot reach the
platform, so use CI for linting and tests that don't need Kafka or the lakehouse.

In this repository, never add `runs-on: self-hosted` — a pull request that does
will be closed.

## Getting your credentials

Your Kafka username and password are at
**[datapg.dev/credentials](https://datapg.dev/credentials)** once you are signed
in. They are yours; anyone you share them with is acting as you.

Never commit them — not to this repository, and not to your own, even if it is
private. Private repositories get made public, forked and shared. Read them from
the environment instead.
