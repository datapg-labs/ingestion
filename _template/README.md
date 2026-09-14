# Template

Copy this whole directory, rename it to your platform ID, and start editing.

```bash
cp -r _template pgXXXX
```

Then in `pipeline.py`, change `PG_ID` to your own.

## What to put in your README

Replace this file with a short description of what you built. Aim it at the next
person who opens the directory:

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
