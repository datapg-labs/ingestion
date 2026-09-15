# Producer scripts

Python programs that produce to (and read back from) the teaching Kafka cluster — one
folder per project.

## Start a project

Copy the worked example to a folder named after what your producer does:

```bash
cp -r producer-scripts/example-kafka-producer producer-scripts/btc-price-alerts
```

[`example-kafka-producer`](example-kafka-producer/) creates your topic, writes ten
messages, reads them back, and stops. Change `PG_ID` and build from there.

## What a project folder contains

```
btc-price-alerts/
  README.md       what it does, where the data comes from, who built it, what you learned
  pipeline.py     the producer (and consumer, if it has one)
```

In the README, link the **data contract** for the topic you produce to — see
[`data-contracts`](https://github.com/datapg-labs/data-contracts).

## Things to know

- **Runs in JupyterHub.** `kafka-learn:9092` only resolves inside the platform network,
  so it will not run from your laptop.
- **Nothing to install.** `kafka-python` is already in the notebook image; notebooks have
  no internet access.
- **Your prefix.** Topics and consumer groups must start with your platform ID and a dot
  (`pgXXXX.orders`). Keep the ID configurable so someone else can run your project too.
- **No credentials in files.** Read the password from the environment:
  `os.environ["KAFKA_PASSWORD"]`.
