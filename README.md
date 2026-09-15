# ingestion

Streaming and ingestion pipelines — Kafka producers, source connector configs, and the
contracts for what they ingest.

This is the repo where things actually run today. If you are new, start here.

## Layout

```
producer-scripts/            Python producers, one folder per project
  example-kafka-producer/    start here: create a topic, produce, consume
source-connectors/           Kafka Connect source configs (JSON), one folder per project
```

## Before you start

1. Sign in at [datapg.dev](https://datapg.dev) and open
   **[Your credentials](https://datapg.dev/credentials)**. You need your Kafka username
   and password.
2. Open **JupyterHub** from the launchpad. That is where your code runs — it sits on the
   same network as the teaching Kafka cluster, so `kafka-learn:9092` resolves there and
   nowhere else.
3. Read [`producer-scripts/example-kafka-producer`](producer-scripts/example-kafka-producer/)
   and copy it to start your own.

## Your first five minutes

There is nothing to install. The notebook image already ships the Kafka client
(`kafka-python`) — and platform notebooks have no internet access, so `pip install`
would fail anyway.

Your JupyterHub server has a ready-made `examples/kafka_example.ipynb` to run first.

Two things trip up almost everyone:

**Topics are not auto-created.** Producing to a topic that does not exist does not fail
helpfully — it hangs for sixty seconds and then reports
`KafkaTimeoutError: Failed to update metadata`, which says nothing about the real cause.
Create the topic first. The example does this.

**Everything you own starts with your prefix.** Topics and consumer groups both.
`pgXXXX.orders` is yours; `orders` is not, and `pgYYYY.orders` certainly is not. The
error for getting this wrong is `TopicAuthorizationFailedError`.

## What you can build here

- A producer that generates or fetches events and writes them to your topic
- A consumer that reads them back and does something useful
- A source connector configuration, as JSON, designed and reviewed — see
  [`source-connectors/`](source-connectors/)

For every ingestion, add a **data contract** in
[`data-contracts`](https://github.com/datapg-labs/data-contracts) describing what lands
on the topic. It is recommended, and reviewers will ask.

You have 1 MB/s in, 2 MB/s out, and 24 hours of retention. That is deliberately enough
to learn the mechanics and not enough to store anything. If you hit the rate limit you
will see throughput flatten and latency climb rather than an error — that is Kafka
throttling you, and it is worth watching happen.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: one folder per project, clone locally,
branch, and open a pull request — everything is reviewed before it merges.
