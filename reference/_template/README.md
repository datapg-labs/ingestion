# Project name — say what it does

Authors: @your-github-user

This README is the template for your project's README. Copy the whole directory into
`projects/`, under a name that says what it does, and start editing:

```bash
cp -r reference/_template projects/btc-price-alerts
```

Then:

1. Replace the title, and put **your** GitHub handle on the `Authors:` line above. The
   scope check uses that line to decide who can change the project — a new project
   without your handle on it fails the check.
2. In `pipeline.py`, change `PG_ID` to your own platform ID, in lowercase. On a shared
   project, read it from the environment instead so every author can run it.

## What to put in your README

Replace this text with a short description of what you built. Aim it at the next
person who opens the directory — quite possibly a teammate joining the project:

- What does it do?
- Where does the data come from, and what shape is it?
- What did you learn, or what surprised you?

That last one is the most valuable and the most often skipped. "The producer hung
for a minute because the topic did not exist" is worth more to the next reader
than a description of Kafka.

## Running it

Your password should never be in a committed file. Set it in the notebook first:

```python
import os
os.environ["KAFKA_PASSWORD"] = "..."   # from https://datapg.dev/credentials
```

Then run `pipeline.py`. It creates your topic, writes ten messages, reads them
back, and stops.
