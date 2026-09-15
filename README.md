# ingestion

Streaming and ingestion pipelines — Kafka producers, consumers, and the config
that feeds the lakehouse.

This is the repo where things actually run today. If you are new, start here.

## Layout

```
reference/_template/   the starting point: create a topic, produce, consume
projects/<name>/       learner projects — README.md lists the authors
```

This is a shared repository: projects live side by side, changes go through pull
requests, and teammates review each other's work. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Before you start

1. Sign in at [datapg.dev](https://datapg.dev) and open
   **[Your credentials](https://datapg.dev/credentials)**. You need your Kafka
   username and password.
2. Open **JupyterHub** from the launchpad. That is where your code runs — it sits
   on the same network as the teaching Kafka cluster, so `kafka-learn:9092`
   resolves there and nowhere else.
3. Create a branch and copy `reference/_template/` into `projects/<your-project>/`,
   or join an existing project.

## Your first five minutes

There is nothing to install. The notebook image already ships the Kafka client
(`kafka-python`) — and platform notebooks have no internet access, so
`pip install` would fail anyway.

Your JupyterHub server has a ready-made `examples/kafka_example.ipynb` to run
first. Then follow `reference/_template/pipeline.py`.

Two things trip up almost everyone:

**Topics are not auto-created.** Producing to a topic that does not exist does
not fail helpfully — it hangs for sixty seconds and then reports
`KafkaTimeoutError: Failed to update metadata`, which says nothing about the real
cause. Create the topic first. The template does this.

**Everything you own starts with your prefix.** Topics and consumer groups both.
`pgXXXX.orders` is yours; `orders` is not, and `pgYYYY.orders` certainly is not.
The error for getting this wrong is `TopicAuthorizationFailedError`.

## What you can build here

- A producer that generates events and writes them to your topic
- A consumer that reads them back and does something useful
- Connect configuration, as JSON, for review and discussion

You have 1 MB/s in, 2 MB/s out, and 24 hours of retention. That is deliberately
enough to learn the mechanics and not enough to store anything. If you hit the
rate limit you will see throughput flatten and latency climb rather than an
error — that is Kafka throttling you, and it is worth watching happen.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: work in `projects/<name>/` with your
handle on its `Authors:` line, branch and open a pull request; a teammate reviews it and
a maintainer merges.
