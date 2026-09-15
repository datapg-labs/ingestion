# Example Kafka producer

The worked example to start from. It creates your topic, writes ten messages, reads them
back, and stops.

Copy it to a folder named after what your producer will do, and start editing:

```bash
cp -r producer-scripts/example-kafka-producer producer-scripts/btc-price-alerts
```

Then in `pipeline.py`, change `PG_ID` to your own platform ID, in lowercase.

## What to put in your README

Replace this file with a short description of what you built. Aim it at the next person
who opens the folder:

- What does it do?
- Where does the data come from, and what shape is it?
- Who built it? (your GitHub handle)
- Which data contract describes the topic it produces?
- What did you learn, or what surprised you?

That last one is the most valuable and the most often skipped. "The producer hung for a
minute because the topic did not exist" is worth more to the next reader than a
description of Kafka.

## Running it

Your password should never be in a committed file. Set it in the notebook first:

```python
import os
os.environ["KAFKA_PASSWORD"] = "..."   # from https://datapg.dev/credentials
```

Then run `pipeline.py`.
