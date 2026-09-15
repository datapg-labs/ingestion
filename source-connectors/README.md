# Source connectors

Kafka Connect **source** connector configurations, as JSON — one folder per project.

## What you can do here

Learners design, document and review connector configurations here; they are not
deployed. The teaching Kafka cluster has no Connect worker of its own, and the platform's
Connect cluster runs the platform's own pipelines.

That is still the useful half of the skill: most connector problems are configuration
problems — the wrong offset mode, a missing key column, a converter that doesn't match
the data, or a secret pasted into the config.

## Connectors available on the platform

| Connector | Class | Use it for |
|---|---|---|
| HTTP Source | `io.confluent.connect.http.HttpSourceConnector` | Polling a REST / JSON API into a topic |
| JDBC Source | `io.confluent.connect.jdbc.JdbcSourceConnector` | Reading new or changed rows from a relational table |
| MirrorMaker 2 | `org.apache.kafka.connect.mirror.MirrorSourceConnector` | Replicating topics from one Kafka cluster to another |

For context, the sinks on the same Connect cluster are **Iceberg** (Kafka → lakehouse
tables — this is how the platform's own streams land), **HTTP**, **JDBC** and
**Elasticsearch**.

Each connector's documentation lists its properties — look them up for the version
you are designing against rather than copying settings from a blog post.

## What a project folder contains

```
http-json-orders/
  README.md        what it pulls, from where, how often, into which topic — and why
  connector.json   the configuration
```

The shape every configuration shares:

```json
{
  "name": "pgXXXX-http-json-orders",
  "config": {
    "connector.class": "io.confluent.connect.http.HttpSourceConnector",
    "tasks.max": "1",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false"
  }
}
```

…plus the connector-specific properties: the source (URL or JDBC connection), the
polling interval, the offset or incremental mode, and the target topic — which must
start with your platform ID (`pgXXXX.orders`).

## Things to know

- **No credentials in the JSON.** Leave passwords, tokens and API keys as clearly marked
  placeholders and say in the README where they would come from.
- **Add a data contract** for the topic the connector produces, in
  [`data-contracts`](https://github.com/datapg-labs/data-contracts), and link it from the
  README.
- **Explain the choices** in the README: why this offset mode, what happens on restart,
  what a duplicate looks like. That is what the review will be about.
